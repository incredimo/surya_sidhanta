#!/usr/bin/env python3
"""
calibrate_engine.py
THE DIGITAL TWIN OPTIMIZATION (Fix + Moon Apsis Support)
"""

import os
import math
import subprocess
import numpy as np
import swisseph as swe
from datetime import datetime
from scipy.optimize import minimize

# ---------------- CONFIGURATION ----------------
START_YEAR = 2023
YEARS_TO_SAMPLE = 3 
AYANAMSHA = swe.SIDM_LAHIRI
RUST_SRC = os.path.join("src", "main.rs")
MAHAYUGA_DAYS = 1_577_917_828.0
JD_KALI_EPOCH = 588_465.50
R = 3438.0

# Fixed Physics Constants
EPICYCLES = {
    "Sun":     (14.0, 13.67, None, None),
    "Moon":    (32.0, 31.67, None, None),
    "Mars":    (75.0, 72.0, 235.0, 232.0),
    "Mercury": (30.0, 28.0, 133.0, 132.0),
    "Jupiter": (33.0, 32.0, 70.0, 72.0),
    "Venus":   (12.0, 11.0, 262.0, 260.0),
    "Saturn":  (49.0, 48.0, 39.0, 40.0),
}

STD_REVS = {
    "Sun": 4_320_000.0,
    "Moon": 57_753_336.0,
    "Mars": 2_296_832.0,
    "Mercury": 17_937_060.0,
    "Jupiter": 364_220.0,
    "Venus": 7_022_376.0,
    "Saturn": 146_568.0,
    "Rahu": -232_238.0
}
MOON_APSIS_REV_GUESS = 488_203.0 # SS Default for Moon Apogee

# ---------------- PYTHON SS ENGINE ----------------

def norm360(angle):
    angle = angle % 360.0
    return angle + 360.0 if angle < 0 else angle

def sin_d(deg): return math.sin(math.radians(deg))
def cos_d(deg): return math.cos(math.radians(deg))
def asin_d(val): return math.degrees(math.asin(val))

def get_mean_longitude(days, revs, offset):
    cycles = (days * revs) / MAHAYUGA_DAYS
    fraction = cycles - int(cycles)
    return norm360((fraction * 360.0) + offset)

def get_manda_corr(mean_lon, ucca, even, odd):
    anomaly = norm360(mean_lon - ucca)
    diff = even - odd
    rect_circ = even - (diff * abs(sin_d(anomaly)))
    sin_eq = (rect_circ * sin_d(anomaly)) / 360.0
    return asin_d(sin_eq)

def get_sighra_corr(planet_lon, sighrocca, even, odd):
    anomaly = norm360(sighrocca - planet_lon)
    diff = even - odd
    rect_circ = even - (diff * abs(sin_d(anomaly)))
    r_val = (rect_circ / 360.0) * R
    doh = r_val * sin_d(anomaly)
    koti = r_val * cos_d(anomaly)
    karna = math.sqrt((R + koti)**2 + doh**2)
    sine_val = (doh * R) / karna
    sine_val = max(-R, min(R, sine_val))
    return asin_d(sine_val / R)

def calc_true_pos_py(days, name, revs, offset, apsis_offset, apsis_revs, mean_sun_pos):
    # Determine Mean and Sighra inputs
    if name in ["Sun", "Moon"]:
        mean = get_mean_longitude(days, revs, offset)
        sighra = 0.0
        ptype = "Luminary"
    elif name in ["Mercury", "Venus"]:
        mean = mean_sun_pos
        sighra = get_mean_longitude(days, revs, offset)
        ptype = "Star"
    else:
        mean = get_mean_longitude(days, revs, offset)
        sighra = mean_sun_pos
        ptype = "Star"

    m_ev, m_od, s_ev, s_od = EPICYCLES[name]
    
    # Dynamic Apsis Calculation
    manda_ucca = get_mean_longitude(days, apsis_revs, apsis_offset)

    if ptype == "Luminary":
        corr = get_manda_corr(mean, manda_ucca, m_ev, m_od)
        return norm360(mean - corr)
    
    s1 = get_sighra_corr(mean, sighra, s_ev, s_od)
    p1 = mean + (s1 / 2.0)
    m1 = get_manda_corr(p1, manda_ucca, m_ev, m_od)
    p2 = mean + (m1 / 2.0)
    m2 = get_manda_corr(p2, manda_ucca, m_ev, m_od)
    p_manda = mean + m2
    s2 = get_sighra_corr(p_manda, sighra, s_ev, s_od)
    return norm360(p_manda + s2)

# ---------------- OPTIMIZATION ----------------

def smallest_diff(a, b):
    d = a - b
    d = (d + 180) % 360 - 180
    return d

def objective_function(params, name, times, targets, fixed_sun_pos=None):
    # Unpack params. Size depends on planet.
    # We optimize: [Revs, Offset, Apsis_Offset, Apsis_Revs]
    revs, offset, apsis_off, apsis_revs = params
    
    errors = []
    for i, t in enumerate(times):
        ms = fixed_sun_pos[i] if fixed_sun_pos is not None else 0.0
        calc = calc_true_pos_py(t, name, revs, offset, apsis_off, apsis_revs, ms)
        err = smallest_diff(calc, targets[i])
        errors.append(err**2)
        
    return np.mean(errors)

def get_training_data(body_name):
    swe.set_ephe_path(os.getenv("SWISS_EPHE_PATH", "./ephe"))
    swe.set_sid_mode(AYANAMSHA, 0, 0)
    mapping = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, 
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    start_dt = datetime(START_YEAR, 1, 1)
    jd_start = swe.julday(start_dt.year, start_dt.month, start_dt.day, 0)
    days_start = jd_start - JD_KALI_EPOCH
    total_days = YEARS_TO_SAMPLE * 365
    step = 5 # Finer resolution for Moon accuracy
    
    times = []
    targets = []
    for i in range(0, total_days, step):
        t_jd = jd_start + i
        res = swe.calc_ut(t_jd, mapping[body_name], swe.FLG_SIDEREAL)
        times.append(days_start + i)
        targets.append(res[0][0])
    return np.array(times), np.array(targets)

def optimize_planet(name, fixed_sun=None):
    print(f"Optimizing {name}...", end="", flush=True)
    times, targets = get_training_data(name)
    
    # Guesses
    x0_revs = STD_REVS[name]
    x0_offset = 0.0 
    x0_apsis_off = 0.0
    x0_apsis_revs = 0.0
    
    if name == "Moon":
        x0_apsis_revs = MOON_APSIS_REV_GUESS

    # Define Bounds
    rev_wiggle = abs(x0_revs) * 0.05
    apsis_rev_wiggle = 50000.0 if name == "Moon" else 10.0 # Only Moon apsis moves fast
    
    # Only let Moon optimize Apsis Revs significantly. Others stay near 0 (static approx)
    b_revs = (x0_revs - rev_wiggle, x0_revs + rev_wiggle)
    b_aps_revs = (x0_apsis_revs - apsis_rev_wiggle, x0_apsis_revs + apsis_rev_wiggle)
    
    init_guess = [x0_revs, x0_offset, x0_apsis_off, x0_apsis_revs]
    
    sun_means = None
    if fixed_sun:
        s_revs, s_off = fixed_sun['revs'], fixed_sun['offset']
        sun_means = [get_mean_longitude(t, s_revs, s_off) for t in times]
        
    res = minimize(
        objective_function, 
        init_guess, 
        args=(name, times, targets, sun_means),
        method='Nelder-Mead',
        tol=1e-5
    )
    
    final = res.x
    rms = math.sqrt(res.fun) * 60.0
    print(f" RMS: {rms:.2f}' | Revs: {final[0]:.2f} | Ap.Revs: {final[3]:.2f}")
    
    return {
        "revs": final[0],
        "offset": norm360(final[1]),
        "apsis_offset": norm360(final[2]),
        "apsis_revs": final[3]
    }

def optimize_rahu():
    print("Optimizing Rahu...", end="", flush=True)
    times, targets = get_training_data("Rahu")
    def rahu_obj(params):
        revs, offset = params
        errs = []
        for i, t in enumerate(times):
            m = get_mean_longitude(t, revs, offset)
            calc = norm360(m) 
            err = smallest_diff(calc, targets[i])
            errs.append(err**2)
        return np.mean(errs)
    x0 = [STD_REVS["Rahu"], 0.0]
    res = minimize(rahu_obj, x0, method='Nelder-Mead')
    rms = math.sqrt(res.fun) * 60.0
    print(f" RMS: {rms:.2f}'")
    return {"revs": res.x[0], "offset": norm360(res.x[1])}

def write_rust(params):
    code = "const PLANETS: &[PlanetParam] = &[\n"
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for p in order:
        d = params[p]
        ep = EPICYCLES[p]
        ptype = "PlanetType::Luminary" if p in ["Sun", "Moon"] else "PlanetType::Star"
        manda = f"EpicycleDims {{ even: {ep[0]}, odd: {ep[1]} }}"
        sighra = "None"
        if ep[2]: sighra = f"Some(EpicycleDims {{ even: {ep[2]}, odd: {ep[3]} }})"
        
        code += f"""    PlanetParam {{
        name: "{p}", ptype: {ptype},
        revs: {d['revs']:.8f}, 
        manda_ep: {manda}, sighra_ep: {sighra},
        bija_offset: {d['offset']:.8f}, 
        apsis_offset: {d['apsis_offset']:.8f},
        apsis_revs: {d['apsis_revs']:.8f},
    }},\n"""

    code += "];\n"
    code += f"const NODE_REVS: f64 = {params['Rahu']['revs']:.8f};\n"
    code += f"const NODE_OFFSET: f64 = {params['Rahu']['offset']:.8f};\n"
    
    with open(RUST_SRC, 'r') as f: raw = f.read()
    start = "// <<PLANET_DATA_START>>"
    end = "// <<PLANET_DATA_END>>"
    if start in raw:
        s_idx = raw.find(start) + len(start)
        e_idx = raw.find(end)
        new_code = raw[:s_idx] + "\n" + code + raw[e_idx:]
        with open(RUST_SRC, 'w') as f: f.write(new_code)

def main():
    print("--- DIGITAL TWIN OPTIMIZATION START ---")
    final_params = {}
    
    final_params["Sun"] = optimize_planet("Sun")
    final_params["Moon"] = optimize_planet("Moon")
    
    for p in ["Mars", "Jupiter", "Saturn"]:
        final_params[p] = optimize_planet(p, final_params["Sun"])
    for p in ["Mercury", "Venus"]:
        final_params[p] = optimize_planet(p, final_params["Sun"])
        
    final_params["Rahu"] = optimize_rahu()
    
    write_rust(final_params)
    subprocess.run(["cargo", "build", "--release"], check=True)
    print("Optimization Complete.")

if __name__ == "__main__":
    main()
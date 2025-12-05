#!/usr/bin/env python3
"""
validate_robust.py (Debug Edition)
"""

import os
import sys
import subprocess
import argparse
import platform
import numpy as np
import pandas as pd
import swisseph as swe
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tqdm import tqdm

AYANAMSHA_MODE = swe.SIDM_LAHIRI 

# Detect OS
IS_WINDOWS = platform.system() == "Windows"
BIN_EXT = ".exe" if IS_WINDOWS else ""
RUST_BIN_PATH = os.path.join(".", "target", "release", f"surya_sidhanta{BIN_EXT}")

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

def install_check():
    if not os.path.exists(RUST_BIN_PATH):
        print(f"ERROR: Rust binary not found at {RUST_BIN_PATH}")
        print("Please run: cargo build --release")
        sys.exit(1)

def smallest_signed_angle(a, b):
    d = a - b
    d = (d + 180) % 360 - 180
    return d

def get_rust_positions(dt, debug=False):
    dt_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        result = subprocess.run(
            [RUST_BIN_PATH, dt_iso],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Rust execution failed: {e.stderr}")
        return {}

    # DEBUG: If parsing fails later, we want to know what this output was
    if debug:
        print(f"\n[DEBUG] Raw Output for {dt_iso}:\n{result.stdout}")

    positions = {}
    for line in result.stdout.splitlines():
        parts = line.split('|')
        # We need at least Body|Lon. Filter out headers or garbage.
        if len(parts) >= 2 and parts[0] in PLANETS:
            try:
                positions[parts[0]] = float(parts[1])
            except ValueError:
                continue
    
    return positions

def get_swiss_positions(dt):
    swe.set_ephe_path(os.getenv("SWISS_EPHE_PATH", "./ephe"))
    swe.set_sid_mode(AYANAMSHA_MODE, 0, 0)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    positions = {}
    mapping = {
        "Sun": swe.SUN, "Moon": swe.MOON, 
        "Mars": swe.MARS, "Mercury": swe.MERCURY, 
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, 
        "Saturn": swe.SATURN
    }
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    for name, pid in mapping.items():
        res = swe.calc_ut(jd, pid, flags)
        positions[name] = res[0][0]
        
    rahu_res = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu_lon = rahu_res[0][0]
    positions["Rahu"] = rahu_lon
    positions["Ketu"] = (rahu_lon + 180.0) % 360.0
    
    return positions

def run_suite(start_date, end_date, steps):
    total_seconds = (end_date - start_date).total_seconds()
    step_size = total_seconds / steps
    records = []
    
    # Check first frame for debug purposes
    print("Checking binary output format...")
    first_check = get_rust_positions(start_date, debug=True)
    if not first_check:
        print("\n[CRITICAL ERROR] Could not parse any planets from Rust binary.")
        print("Expected format: 'Sun|123.45|...'")
        print("Please ensure src/main.rs matches the Pipe-delimited format.")
        sys.exit(1)
    else:
        print(f"Successfully parsed {len(first_check)} bodies. Starting sequence...")

    for i in tqdm(range(steps + 1)):
        current_dt = start_date + timedelta(seconds=i * step_size)
        rust_pos = get_rust_positions(current_dt)
        swiss_pos = get_swiss_positions(current_dt)
        
        for body in PLANETS:
            if body in rust_pos and body in swiss_pos:
                err = smallest_signed_angle(swiss_pos[body], rust_pos[body])
                records.append({
                    "body": body,
                    "error_min": err * 60.0,
                    "timestamp": current_dt
                })

    return pd.DataFrame(records)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2025-01-01")
    parser.add_argument("--samples", type=int, default=100)
    args = parser.parse_args()
    
    install_check()
    
    s = datetime.strptime(args.start, "%Y-%m-%d")
    e = datetime.strptime(args.end, "%Y-%m-%d")
    
    df = run_suite(s, e, args.samples)
    
    if not df.empty:
        print("\n" + "="*60)
        print(f"{'RMS ERROR (Arc-Minutes) [Lower is Better]':^60}")
        print("="*60)
        stats = df.groupby('body')['error_min'].agg(lambda x: np.sqrt(np.mean(x**2)))
        print(stats.to_string(float_format="{:.2f}".format))
        print("="*60)
        
        # Plot
        bodies = df['body'].unique()
        fig, axes = plt.subplots(len(bodies), 1, figsize=(10, 2*len(bodies)), sharex=True)
        if len(bodies) == 1: axes = [axes]
        
        for ax, body in zip(axes, bodies):
            sub = df[df['body'] == body]
            ax.plot(sub['timestamp'], sub['error_min'])
            ax.set_ylabel(f"{body} Error (')")
            ax.grid(True)
            
        plt.tight_layout()
        plt.savefig("validation_report.png")
        print("\nReport saved to validation_report.png")
    else:
        print("\n[ERROR] No data collected. Check the debug output above.")

if __name__ == "__main__":
    main()
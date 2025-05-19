#!/usr/bin/env python3
"""
validate_siddhanta.py

Compare the classical Surya Siddhānta Rust implementation
against Swiss Ephemeris (DE431) over a long time period,
and plot both longitude time-series (Rust vs Swiss) for each body.

Usage:
    ./validate_siddhanta.py \
      --datetime 2025-05-19T13:51:26 \
      --start 2000-01-01 \
      --end   2100-01-01 \
      --step  30
"""
import os
import sys
import subprocess
import argparse
import math
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# 1) Ensure Python dependencies are installed
# -------------------------------------------------------------------
def install_pydeps():
    deps = ["pyswisseph", "numpy", "pandas", "matplotlib"]
    for pkg in deps:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", pkg
        ], check=True)

# -------------------------------------------------------------------
# 2) Ensure Rust code is built (uses existing Cargo.toml in repo root)
# -------------------------------------------------------------------
RUST_CWD = os.path.dirname(os.path.abspath(__file__))

def build_rust():
    subprocess.run([
        "cargo", "build", "--release"
    ], cwd=RUST_CWD, check=True)

# -------------------------------------------------------------------
# 3) Run the Rust calculator and parse its output
# -------------------------------------------------------------------
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]

def run_rust(dt_iso):
    cmd = ["cargo", "run", "--release", "--", dt_iso]
    p = subprocess.run(
        cmd,
        cwd=RUST_CWD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore'
    )
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(1)
    out = {}
    for line in p.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) == 3 and parts[0] in PLANETS:
            body, lon, _lat = parts
            out[body] = float(lon)
    return out

# -------------------------------------------------------------------
# 4) Fetch Swiss Ephemeris longitudes via pyswisseph
# -------------------------------------------------------------------
def get_swiss(dt, bodies):
    import swisseph as swe
    ephe = os.environ.get("SWISS_EPHE_PATH", "./ephe")
    swe.set_ephe_path(ephe)
    # Use sidereal mode (Lahiri)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    # Compute Julian Day UT
    jd = swe.julday(
        dt.year, dt.month, dt.day,
        dt.hour + dt.minute/60 + dt.second/3600
    )
    swiss = {}
    mapping = {
        "Sun": swe.SUN, "Moon": swe.MOON,
        "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN
    }
    for b in bodies:
        if b in mapping:
            lon = swe.calc_ut(jd, mapping[b], swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        elif b == "Rahu":
            lon = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        elif b == "Ketu":
            asc = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
            lon = (asc + 180.0) % 360
        else:
            raise ValueError(f"Unknown body: {b}")
        swiss[b] = lon
    return swiss

# -------------------------------------------------------------------
# 5) Build a time-series of both Rust and Swiss longitudes
# -------------------------------------------------------------------
def build_timeseries(start, end, step_days):
    records = []
    dt = start
    while dt <= end:
        iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
        rust = run_rust(iso)
        swiss = get_swiss(dt, PLANETS)
        for b in PLANETS:
            records.append({
                "date": dt,
                "body": b,
                "rust_lon": rust[b],
                "swiss_lon": swiss[b]
            })
        dt += timedelta(days=step_days)
    return pd.DataFrame(records)

# -------------------------------------------------------------------
# 6) Plotting both series per body
# -------------------------------------------------------------------
def plot_both(df):
    bodies = df['body'].unique()
    n = len(bodies)
    fig, axes = plt.subplots(n, 1, figsize=(12, 2*n), sharex=True)
    for ax, b in zip(axes, bodies):
        sub = df[df['body'] == b]
        ax.plot(sub['date'], sub['rust_lon'], label='Rust (Surya Siddhanta)')
        ax.plot(sub['date'], sub['swiss_lon'], label='Swiss Ephemeris')
        ax.set_ylabel(f"{b} Lon (°)")
        ax.legend(loc='upper right', fontsize='small')
        ax.grid(True)
    axes[-1].set_xlabel("Date")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# 7) Main entry point
# -------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datetime", required=True,
                        help="ISO date-time, e.g. 2025-05-19T13:51:26")
    parser.add_argument("--start", required=True,
                        help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True,
                        help="End date   YYYY-MM-DD")
    parser.add_argument("--step", type=int, default=30,
                        help="Days between samples")
    args = parser.parse_args()

    print("Installing Python dependencies…")
    install_pydeps()

    print("Building Rust implementation…")
    build_rust()

    # Single-epoch comparison
    dt0 = datetime.fromisoformat(args.datetime)
    rust0 = run_rust(args.datetime)
    swiss0 = get_swiss(dt0, PLANETS)
    print("=== Single-epoch Rust vs Swiss (deg) ===")
    print(f"Date/Time: {args.datetime}")
    print(f"{'Body':<8}{'Rust':>12}{'Swiss':>12}{'Δ (′)':>10}")
    for b in PLANETS:
        ddeg = ((rust0[b] - swiss0[b] + 180) % 360) - 180
        dm = ddeg * 60
        print(f"{b:<8}{rust0[b]:>12.6f}{swiss0[b]:>12.6f}{dm:>10.2f}")

    # Multi-epoch time series
    print("\nBuilding multi-epoch time series…")
    start = datetime.fromisoformat(args.start + "T00:00:00")
    end   = datetime.fromisoformat(args.end   + "T00:00:00")
    df = build_timeseries(start, end, args.step)

    print("Plotting time-series…")
    plot_both(df)

if __name__ == "__main__":
    main()
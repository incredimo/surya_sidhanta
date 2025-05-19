#!/usr/bin/env python3
"""
generate_corrections.py

Generate Fourier-based correction coefficients mapping
Surya Siddhanta outputs to high-precision Swiss Ephemeris values.

This script:
 1. Samples both Siddhanta and Swiss ephemeris longitudes for each
    body over a user-defined time span and sampling interval (minutes or days).
 2. Computes residuals Δλ(t) = λ_swiss(t) - λ_siddhanta(t) (normalized ±180°).
 3. Fits a truncated Fourier series to each body's residuals:
      Δλ(t) ≈ a0 + sum_{k=1..K} [ A_k cos(ω_k t) + B_k sin(ω_k t) ]
    where frequencies ω_k are selectable or auto-derived.
 4. Exports the fitted coefficients and frequencies to JSON and Rust source.

Usage:
  ./generate_corrections.py \
    --start 1900-01-01 \
    --end   2100-01-01 \
    --step  1440 \
    --unit  minute \
    --bodies Sun Moon Mercury Venus Mars Jupiter Saturn Rahu Ketu \
    --freqs annual Jupiter Saturn node \
    --order 5 \
    --out coeffs.json rust_corrections.rs

Options:
  --start, --end   : date range (YYYY-MM-DD)
  --step, --unit  : sampling step and unit (day or minute)
  --bodies        : list of bodies to fit
  --freqs         : list of frequency presets or explicit days-per-cycle
  --order         : number of harmonics per frequency
  --out json rust : paths to output JSON and Rust file
"""
import argparse
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import swisseph as swe
import subprocess, sys
import math

# Load Siddhanta rust binary
RUST_BIN = ["cargo","run","--release","--"]
PLANETS = []

# Frequency presets in days
FREQ_PRESETS = {
    'solar_year': 365.256363004,   # tropical year
    'jupiter': 4332.589,           # Jupiter sidereal period
    'saturn': 10759.22,            # Saturn sidereal period
    'node': 6798.38,               # mean lunar node regression (~18.6y)
}

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--start', required=True)
    p.add_argument('--end', required=True)
    p.add_argument('--step', type=int, required=True)
    p.add_argument('--unit', choices=['day','minute'], required=True)
    p.add_argument('--bodies', nargs='+', default=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Rahu','Ketu'])
    p.add_argument('--freqs', nargs='+', default=['solar_year','jupiter','saturn','node'])
    p.add_argument('--order', type=int, default=5)
    p.add_argument('json_out')
    p.add_argument('rust_out')
    return p.parse_args()

# Utilities for JD and Siddhanta run

def run_siddhanta(dt_iso):
    cmd = RUST_BIN + [dt_iso]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
    if proc.returncode!=0:
        print(proc.stderr, file=sys.stderr); sys.exit(1)
    lon = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts)==3 and parts[0] in PLANETS:
            lon[parts[0]] = float(parts[1])
    return lon

# Swiss ephemeris

def get_swiss(dt):
    swe.set_ephe_path(os.getenv('SWISS_EPHE_PATH','./ephe'))
    swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
    jd = swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600)
    vals = {}
    mapping={b:getattr(swe,b.upper()) for b in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']}
    for b in PLANETS:
        if b in mapping:
            vals[b]=swe.calc_ut(jd, mapping[b], swe.FLG_SWIEPH|swe.FLG_SIDEREAL)[0][0]
        elif b=='Rahu':
            vals[b]=swe.calc_ut(jd,swe.MEAN_NODE,swe.FLG_SWIEPH|swe.FLG_SIDEREAL)[0][0]
        elif b=='Ketu':
            asc=swe.calc_ut(jd,swe.MEAN_NODE,swe.FLG_SWIEPH|swe.FLG_SIDEREAL)[0][0]
            vals[b]=(asc+180)%360
    return vals

# Normalize difference ±180

def delta(a,b): return ((a-b+180)%360)-180

# Build time series
def build_series(start,end,step,unit,bodies):
    dt=start; recs=[]
    delta_t = timedelta(days=step) if unit=='day' else timedelta(minutes=step)
    while dt<=end:
        iso=dt.strftime('%Y-%m-%dT%H:%M:%S')
        sidh=run_siddhanta(iso)
        swi=get_swiss(dt)
        t=(dt-start).total_seconds()/86400.0  # days since
        for b in bodies:
            recs.append((t, b, delta(swi[b],sidh[b])))
        dt+=delta_t
    return pd.DataFrame(recs, columns=['t','body','delta'])

# Fourier fitting

def fit_fourier(df, freqs, order):
    results={}
    for b,grp in df.groupby('body'):
        t=grp['t'].values; y=grp['delta'].values
        # design matrix: constant + cos/sin for each freq and harmonic
        cols=[np.ones_like(t)]
        labels=['a0']
        for f_label in freqs:
            P=FREQ_PRESETS.get(f_label,float(f_label))
            omega=2*math.pi/P
            for k in range(1,order+1):
                cols.append(np.cos(k*omega*t)); labels.append(f'C_{f_label}_{k}')
                cols.append(np.sin(k*omega*t)); labels.append(f'S_{f_label}_{k}')
        A=np.vstack(cols).T
        # least squares
        coeffs,_,_,_ = np.linalg.lstsq(A,y,rcond=None)
        results[b]={lab:float(coeffs[i]) for i,lab in enumerate(labels)}
    return results

# Export

def export_json(coeffs,path):
    with open(path,'w') as f: json.dump(coeffs,f,indent=2)

# Rust source

def export_rust(coeffs,path):
    with open(path,'w') as f:
        f.write('// Auto-generated Fourier corrections\n')
        f.write('use std::f64::consts::PI;\n')
        f.write('pub struct Term{pub freq:f64,pub cos:f64,pub sin:f64;}\n')
        for b,coef in coeffs.items():
            f.write(f'pub const {b.upper()}_CORR: [Term; {len(coef)-1} ] = [\n')
            # skip a0 at idx0
            i=1
            for lab,val in list(coef.items())[1:]:
                parts=lab.split('_'); ftype,flab,k=parts[0],parts[1],int(parts[2])
                P=FREQ_PRESETS.get(flab,float(flab)); omega=2*math.pi/P*k
                if ftype=='C': cos=val; sin=coef[f'S_{flab}_{k}']
                if ftype=='S': continue
                f.write(f'  Term{{freq:{omega:.12},cos:{cos:.12},sin:{sin:.12}}},\n')
                i+=1
            f.write('];\n\n')

# Main
def main():
    args=parse_args();
    global PLANETS; PLANETS=args.bodies
    start=datetime.fromisoformat(args.start+'T00:00:00')
    end=datetime.fromisoformat(args.end+'T00:00:00')
    df=build_series(start,end,args.step,args.unit,PLANETS)
    coeffs=fit_fourier(df,args.freqs,args.order)
    export_json(coeffs,args.json_out)
    export_rust(coeffs,args.rust_out)
    print('Generated corrections for bodies:',', '.join(PLANETS))

if __name__=='__main__': main()

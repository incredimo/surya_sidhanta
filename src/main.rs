// =============================================================================
// SŪRYA SIDDHĀNTA: DYNAMIC APOGEE ENGINE
// =============================================================================

use chrono::{Datelike, NaiveDateTime, Timelike};
use std::env;

const MAHAYUGA_DAYS: f64 = 1_577_917_828.0;
const JD_KALI_EPOCH: f64 = 588_465.50;
const R: f64 = 3438.0;

#[derive(Debug, Clone, Copy, PartialEq)]
enum PlanetType { Luminary, Star }

#[derive(Debug, Clone, Copy)]
struct EpicycleDims { even: f64, odd: f64 }

struct PlanetParam {
    name: &'static str,
    ptype: PlanetType,
    revs: f64,             // Mean Motion
    manda_ep: EpicycleDims,
    sighra_ep: Option<EpicycleDims>, 
    bija_offset: f64,      // Mean Longitude at Epoch
    apsis_offset: f64,     // Apogee Longitude at Epoch
    apsis_revs: f64,       // Apogee Speed (Critical for Moon)
}

// <<PLANET_DATA_START>>
const PLANETS: &[PlanetParam] = &[
    PlanetParam {
        name: "Sun", ptype: PlanetType::Luminary,
        revs: 4320848.34408488, 
        manda_ep: EpicycleDims { even: 14.0, odd: 13.67 }, sighra_ep: None,
        bija_offset: 358.23069795, 
        apsis_offset: 150.65387626,
        apsis_revs: -167.46602982,
    },
    PlanetParam {
        name: "Moon", ptype: PlanetType::Luminary,
        revs: 57753342.92393804, 
        manda_ep: EpicycleDims { even: 32.0, odd: 31.67 }, sighra_ep: None,
        bija_offset: 0.00018896, 
        apsis_offset: 359.99999923,
        apsis_revs: 494300.42432448,
    },
    PlanetParam {
        name: "Mars", ptype: PlanetType::Star,
        revs: 2296812.59669639, 
        manda_ep: EpicycleDims { even: 75.0, odd: 72.0 }, sighra_ep: Some(EpicycleDims { even: 235.0, odd: 232.0 }),
        bija_offset: 11.08405200, 
        apsis_offset: 292.32580688,
        apsis_revs: 41.43232597,
    },
    PlanetParam {
        name: "Mercury", ptype: PlanetType::Star,
        revs: 17937100.89276243, 
        manda_ep: EpicycleDims { even: 30.0, odd: 28.0 }, sighra_ep: Some(EpicycleDims { even: 133.0, odd: 132.0 }),
        bija_offset: 337.29402275, 
        apsis_offset: 45.06132833,
        apsis_revs: 2.13840157,
    },
    PlanetParam {
        name: "Jupiter", ptype: PlanetType::Star,
        revs: 364191.78110405, 
        manda_ep: EpicycleDims { even: 33.0, odd: 32.0 }, sighra_ep: Some(EpicycleDims { even: 70.0, odd: 72.0 }),
        bija_offset: 7.81164608, 
        apsis_offset: 351.08026288,
        apsis_revs: -2.89738145,
    },
    PlanetParam {
        name: "Venus", ptype: PlanetType::Star,
        revs: 7011399.58589762, 
        manda_ep: EpicycleDims { even: 12.0, odd: 11.0 }, sighra_ep: Some(EpicycleDims { even: 262.0, odd: 260.0 }),
        bija_offset: 359.99978305, 
        apsis_offset: 0.00015868,
        apsis_revs: 0.00015838,
    },
    PlanetParam {
        name: "Saturn", ptype: PlanetType::Star,
        revs: 146704.22608823, 
        manda_ep: EpicycleDims { even: 49.0, odd: 48.0 }, sighra_ep: Some(EpicycleDims { even: 39.0, odd: 40.0 }),
        bija_offset: 309.70285787, 
        apsis_offset: 3.55375712,
        apsis_revs: 143.30051754,
    },
];
const NODE_REVS: f64 = -232269.44830466;
const NODE_OFFSET: f64 = 189.47238376;
// <<PLANET_DATA_END>>

fn norm360(mut angle: f64) -> f64 {
    angle = angle % 360.0;
    if angle < 0.0 { angle + 360.0 } else { angle }
}
fn sin_d(deg: f64) -> f64 { deg.to_radians().sin() }
fn cos_d(deg: f64) -> f64 { deg.to_radians().cos() }
fn asin_d(val: f64) -> f64 { val.asin().to_degrees() }

fn get_mean_longitude(days_elapsed: f64, revs: f64, correction: f64) -> f64 {
    let cycles = (days_elapsed * revs) / MAHAYUGA_DAYS;
    let fraction = cycles.fract();
    norm360((fraction * 360.0) + correction)
}

fn get_rectified_periphery(ep: EpicycleDims, anomaly: f64) -> f64 {
    let difference = ep.even - ep.odd;
    ep.even - (difference * sin_d(anomaly).abs())
}

fn get_manda_correction(mean_lon: f64, ucca: f64, ep: EpicycleDims) -> f64 {
    let anomaly = norm360(mean_lon - ucca);
    let rectified_circum = get_rectified_periphery(ep, anomaly);
    let sin_eq = (rectified_circum * sin_d(anomaly)) / 360.0;
    asin_d(sin_eq)
}

fn get_sighra_correction(planet_lon: f64, sighrocca: f64, ep: EpicycleDims) -> f64 {
    let anomaly = norm360(sighrocca - planet_lon);
    let rectified_circum = get_rectified_periphery(ep, anomaly);
    let r = (rectified_circum / 360.0) * R;
    let dohphala = r * sin_d(anomaly);
    let kotiphala = r * cos_d(anomaly);
    let karna = ((R + kotiphala).powi(2) + dohphala.powi(2)).sqrt();
    let sine_val = (dohphala * R) / karna;
    let clamped = sine_val.max(-R).min(R);
    asin_d(clamped / R)
}

fn calculate_true_position(days: f64, planet: &PlanetParam, sun_mean: f64) -> f64 {
    let (mean_lon, sighrocca_lon) = match planet.ptype {
        PlanetType::Luminary => (get_mean_longitude(days, planet.revs, planet.bija_offset), 0.0),
        PlanetType::Star => {
            if planet.name == "Mercury" || planet.name == "Venus" {
                (sun_mean, get_mean_longitude(days, planet.revs, planet.bija_offset))
            } else {
                (get_mean_longitude(days, planet.revs, planet.bija_offset), sun_mean)
            }
        }
    };
    
    // Calculate Dynamic Apogee
    let manda_ucca = get_mean_longitude(days, planet.apsis_revs, planet.apsis_offset);

    if planet.ptype == PlanetType::Luminary {
        let corr = get_manda_correction(mean_lon, manda_ucca, planet.manda_ep);
        return norm360(mean_lon - corr);
    }
    
    let sighra_ep = planet.sighra_ep.unwrap();
    let s1 = get_sighra_correction(mean_lon, sighrocca_lon, sighra_ep);
    let p1 = mean_lon + (s1 / 2.0); 
    let m1 = get_manda_correction(p1, manda_ucca, planet.manda_ep);
    let p2 = mean_lon + (m1 / 2.0);
    let m2 = get_manda_correction(p2, manda_ucca, planet.manda_ep);
    let p_manda = mean_lon + m2; 
    let s2 = get_sighra_correction(p_manda, sighrocca_lon, sighra_ep);
    norm360(p_manda + s2)
}

fn calculate_node_longitude(days: f64) -> f64 {
    let motion = get_mean_longitude(days, NODE_REVS, NODE_OFFSET);
    norm360(motion) 
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let target_date_str = if args.len() > 1 { &args[1] } else { "2025-05-19T13:51:26" };
    let dt = match NaiveDateTime::parse_from_str(target_date_str, "%Y-%m-%dT%H:%M:%S") {
        Ok(d) => d,
        Err(_) => { eprintln!("Error parsing date."); return; }
    };

    let year = dt.year();
    let month = dt.month();
    let day = dt.day();
    let hour = dt.hour() as f64 + dt.minute() as f64 / 60.0 + dt.second() as f64 / 3600.0;
    
    let a = (14 - month) / 12;
    let y = year + 4800 - a as i32;
    let m = month + 12 * a as u32 - 3;
    let jdn = day as i32 + (153 * m as i32 + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
    let jd = jdn as f64 + (hour - 12.0) / 24.0;
    let days_elapsed = jd - JD_KALI_EPOCH;

    println!("Body|True|Mean|Sighra");
    
    let sun_param = &PLANETS[0]; 
    let mean_sun = get_mean_longitude(days_elapsed, sun_param.revs, sun_param.bija_offset);

    for planet in PLANETS {
        let true_lon = calculate_true_position(days_elapsed, planet, mean_sun);
        
        let (disp_mean, disp_sighra) = match planet.ptype {
            PlanetType::Luminary => (get_mean_longitude(days_elapsed, planet.revs, planet.bija_offset), 0.0),
            PlanetType::Star => {
                if planet.name == "Mercury" || planet.name == "Venus" {
                    (mean_sun, get_mean_longitude(days_elapsed, planet.revs, planet.bija_offset))
                } else {
                    (get_mean_longitude(days_elapsed, planet.revs, planet.bija_offset), mean_sun)
                }
            }
        };
        println!("{}|{:.6}|{:.6}|{:.6}", planet.name, true_lon, disp_mean, disp_sighra);
    }
    
    let rahu = calculate_node_longitude(days_elapsed);
    let ketu = norm360(rahu + 180.0);
    println!("Rahu|{:.6}|{:.6}|0.0", rahu, rahu);
    println!("Ketu|{:.6}|{:.6}|0.0", ketu, ketu);
}
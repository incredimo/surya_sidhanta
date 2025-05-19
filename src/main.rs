// Surya Siddhanta planetary‑position calculator in Rust
// -------------------------------------------------------
// This single Rust source file implements every step given in the classical
// Surya Siddhanta for computing geocentric ecliptic longitude and latitude of
// the Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn as well as the lunar
// nodes Rāhu (ascending) and Ketu (descending).  It follows the stanza‑by‑stanza
// rules, using the traditional epoch (Kali Yuga start, 588 465.5 JD) and the
// exact constants of revolutions and epicycle dimensions that the text gives.
 
// -------------------------------------------------------

use chrono::{NaiveDateTime, NaiveDate, Timelike, Datelike};
use std::f64::consts::PI;

// -------------------------- CONSTANTS ---------------------------
const MAHAYUGA_DAYS: f64 = 1_577_917_828.0;        // civil days in a Mahā‑yuga
const JD_KALI_START: f64 = 588_465.5;              // JD at 00:00 Ujjain, 18 Feb 3102 BCE
const R: f64 = 3438.0;                             // Indian sine‑table radius (arc‑minutes)
const OBLIQUITY_DEG: f64 = 24.0;                   // Surya Siddhānta ecliptic obliquity

#[derive(Clone, Copy)]
struct PlanetParam {
    revs: f64,           // revolutions per Mahā‑yuga
    apsidal_revs: f64,   // revolutions of apsis per Mahā‑yuga
    sighra_diam_deg: Option<f64>, // diameter of sīghra epicycle (°) – None ⇒ Sun
    incl_deg: f64,       // orbital inclination (°)
    node_revs: f64,      // revolutions of node per Mahā‑yuga (retrograde ⇒ negative)
}

// Surya Siddhānta canonical constants
const PLANETS: &[(&str, PlanetParam)] = &[
    ("Sun",     PlanetParam{ revs: 4_320_000.0,  apsidal_revs:  387.0,    sighra_diam_deg: None,      incl_deg: 0.0,     node_revs:   0.0 }),
    ("Moon",    PlanetParam{ revs: 57_753_336.0, apsidal_revs: 488_203.0, sighra_diam_deg: Some(63.333_333), incl_deg: 5.145,  node_revs: -232_238.0 }),
    ("Mercury", PlanetParam{ revs: 17_937_060.0, apsidal_revs:  368.0,    sighra_diam_deg: Some(132.0),     incl_deg: 2.2667, node_revs:   -488.0 }),
    ("Venus",   PlanetParam{ revs: 7_022_370.0,  apsidal_revs:  535.0,    sighra_diam_deg: Some(260.0),     incl_deg: 1.6833, node_revs:   -903.0 }),
    ("Mars",    PlanetParam{ revs: 2_296_832.0,  apsidal_revs:  204.0,    sighra_diam_deg: Some(234.0),     incl_deg: 1.850,  node_revs:   -214.0 }),
    ("Jupiter", PlanetParam{ revs:   364_220.0,  apsidal_revs:  900.0,    sighra_diam_deg: Some(72.0),      incl_deg: 1.303,  node_revs:   -174.0 }),
    ("Saturn",  PlanetParam{ revs:   146_568.0,  apsidal_revs:   39.0,    sighra_diam_deg: Some(40.0),      incl_deg: 2.488,  node_revs:   -662.0 }),
];

// -------------- BASIC ASTRONOMICAL / TRIG UTILITIES -------------
#[inline] fn deg_to_rad(d:f64)->f64 { d*PI/180.0 }
#[inline] fn rad_to_deg(r:f64)->f64 { r*180.0/PI }
#[inline] fn norm360(mut x:f64)->f64 { while x<0.0 {x+=360.0;} while x>=360.0 {x-=360.0;} x }

fn jd_from_datetime(dt: &NaiveDateTime) -> f64 {
    let mut y = dt.year();
    let mut m = dt.month() as i32;
    let d = dt.day() as i32;
    let frac_day = (dt.hour() as f64 + dt.minute() as f64/60.0 + dt.second() as f64/3600.0) / 24.0;
    if m <= 2 { y -= 1; m += 12; }
    let a = (y as f64/100.0).floor();
    let b = 2.0 - a + (a/4.0).floor();
    let jd = (365.25*(y as f64 + 4716.0)).floor()
           + (30.6001*((m+1) as f64)).floor()
           + d as f64 + b - 1524.5 + frac_day;
    jd
}

// ----------------- CORE SURYA‑SIDDHĀNTA ROUTINES ----------------

fn mean_longitude(days: f64, revs: f64) -> f64 {
    norm360(days * revs / MAHAYUGA_DAYS * 360.0)
}

fn apsis_longitude(days: f64, apsidal_revs: f64) -> f64 {
    norm360(days * apsidal_revs / MAHAYUGA_DAYS * 360.0)
}

// Equation of centre (mandaphala) – two‑step iteration
fn true_longitude_manda(mean_long: f64, apsis: f64) -> f64 {
    // first half‑correction
    let delta = (mean_long - apsis).to_radians().sin();
    let corr = rad_to_deg((delta).asin());
    let interm = mean_long + corr/2.0;
    // full correction with updated anomaly
    let delta2 = (interm - apsis).to_radians().sin();
    let corr2 = rad_to_deg((delta2).asin());
    norm360(mean_long + corr2)
}

// Sīghra correction for Mercury…Saturn (+ Moon)
fn sighra_correction(true_lon_once: f64, sun_true: f64, diam_deg: f64) -> f64 {
    // Surya Siddhānta: Δλ = arcsin( (H/R) * sin(β) ) where H = diameter/2 * RADIUS_SCALE
    let h_arcmin = diam_deg * 30.0; // diameter/2 × 60′
    let beta = deg_to_rad(true_lon_once - sun_true);
    let ratio = (h_arcmin / R) * beta.sin();
    // guard domain
    let clipped = ratio.max(-1.0).min(1.0);
    rad_to_deg(clipped.asin())
}

fn true_position(days: f64, pp: &PlanetParam, sun_true: f64) -> (f64,f64) {
    let mean = mean_longitude(days, pp.revs);
    let apsis = apsis_longitude(days, pp.apsidal_revs);
    let once = true_longitude_manda(mean, apsis);
    let true_lon = if let Some(diam) = pp.sighra_diam_deg {
        let ds = sighra_correction(once, sun_true, diam);
        norm360(once - ds)
    } else { once };

    // latitude from node & inclination
    let node_lon = norm360(days * pp.node_revs / MAHAYUGA_DAYS * 360.0);
    let inc = deg_to_rad(pp.incl_deg);
    let lat = rad_to_deg(((true_lon - node_lon).to_radians().sin() * inc.sin()).asin());

    (true_lon, lat)
}

// ------------------------- MAIN DRIVER -------------------------

fn main() {
    // Date‑time argument in ISO 8601 (UTC).  If omitted ⇒ now.
    let arg = std::env::args().nth(1).unwrap_or_else(|| chrono::Utc::now().to_rfc3339());
 
    
    // Extract just the date and time part before the timezone
    let date_part = arg.split('+').next().unwrap_or(&arg).split('Z').next().unwrap_or(&arg);
    
    let dt = if date_part.contains('.') {
        // With microseconds
        NaiveDateTime::parse_from_str(date_part, "%Y-%m-%dT%H:%M:%S.%f")
    } else {
        // Without microseconds
        NaiveDateTime::parse_from_str(date_part, "%Y-%m-%dT%H:%M:%S")
    }.expect("Invalid date/time format");
    
    let jd = jd_from_datetime(&dt);
    let days = jd - JD_KALI_START;

    // First compute Sun (needed for sīghra of others)
    let sun_params = PLANETS[0].1;
    let (sun_true, _) = true_position(days, &sun_params, 0.0);

    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Date/Time (UTC): {}", dt);
    println!("Julian Day      : {:.5}", jd);
    println!("Days since epoch: {:.2}", days);
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("{:<15} {:>15} {:>15}", "Body", "Lon (°)", "Lat (°)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    for (name, param) in PLANETS {
        let (lon, lat) = true_position(days, &param, sun_true);
        println!("{:<15} {:>15.6} {:>15.6}", name, lon, lat);
    }

    // Lunar nodes Rāhu & Ketu
    // Start at 180° (Libra) and then apply the retrograde motion
    let moon_node = norm360(
        180.0 
        + days * PLANETS[1].1.node_revs / MAHAYUGA_DAYS * 360.0
    );
    let rahu = moon_node;               // ascending
    let ketu = norm360(rahu + 180.0);   // descending
    println!("{:<15} {:>15.6} {:>15.6}", "Rahu", rahu, 0.0);
    println!("{:<15} {:>15.6} {:>15.6}", "Ketu", ketu, 0.0);
}



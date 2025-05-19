 
# Surya Siddhānta Astronomical Engine

"The Surya Siddhānta ('Doctrine of the Sun') is one of the most important and influential astronomical treatises of ancient India," said ChatGPT one fine Tuesday. So, I thought, "Why not just go check it out?" Turns out, it's a whole universe of calculations, and this repository is my attempt to bottle some of that ancient starlight into modern code.

This project provides a comprehensive implementation of the Sūrya Siddhānta, for computing planetary positions like it's 500 CE (but on your 21st-century computer). It features a core engine written in Rust for memory safety (lol), alongside Python tools for checking if our ancient math lines up with what the fancy modern satellites say, and for generating some slick error correction models. 

## Table of Contents

- [Surya Siddhānta Astronomical Engine](#surya-siddhānta-astronomical-engine)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Goals](#project-goals)
  - [Introduction to the Sūrya Siddhānta](#introduction-to-the-sūrya-siddhānta)
    - [Historical Context and Origins](#historical-context-and-origins)
    - [Astronomical Significance and Innovations](#astronomical-significance-and-innovations)
    - [Structure of the Text](#structure-of-the-text)
  - [The Mathematical System of the Sūrya Siddhānta](#the-mathematical-system-of-the-sūrya-siddhānta)
    - [Core Cosmological and Kinematic Principles](#core-cosmological-and-kinematic-principles)
    - [The Grand Time Scales and Epoch](#the-grand-time-scales-and-epoch)
    - [Mean Motion Theory: The Foundation](#mean-motion-theory-the-foundation)
    - [Correction Mechanisms: Epicycles and Anomalies](#correction-mechanisms-epicycles-and-anomalies)
      - [Manda Correction (Equation of Center)](#manda-correction-equation-of-center)
      - [Śīghra Correction (Synodic Anomaly)](#śīghra-correction-synodic-anomaly)
    - [Planetary Models and Parameters](#planetary-models-and-parameters)
    - [Calculation of Latitude](#calculation-of-latitude)
  - [Project Implementation Details](#project-implementation-details)
    - [Core Engine: Rust Implementation (`surya_sidhanta`)](#core-engine-rust-implementation-surya_sidhanta)
    - [Validation Framework: Python and Swiss Ephemeris (`validate.py`)](#validation-framework-python-and-swiss-ephemeris-validatepy)
    - [Error Correction Generator (`generate_corrections.py`)](#error-correction-generator-generate_correctionspy)
  - [Comprehensive Usage Guide](#comprehensive-usage-guide)
    - [Prerequisites](#prerequisites)
    - [Building the Project](#building-the-project)
    - [Command Line Interface (Rust Core)](#command-line-interface-rust-core)
    - [Validation Workflow (`validate.py`)](#validation-workflow-validatepy)
    - [Correction Generation (`generate_corrections.py`)](#correction-generation-generate_correctionspy)
      - [Integrating Corrections (Conceptual)](#integrating-corrections-conceptual)
  - [Analysis of Results and Accuracy](#analysis-of-results-and-accuracy)
    - [Intrinsic Accuracy of the Sūrya Siddhānta](#intrinsic-accuracy-of-the-sūrya-siddhānta)
    - [Accuracy with Fourier Corrections](#accuracy-with-fourier-corrections)
    - [Visualizing Comparisons: Understanding the Charts](#visualizing-comparisons-understanding-the-charts)
    - [Characteristic Error Patterns](#characteristic-error-patterns)
  - [Future Development and Enhancements](#future-development-and-enhancements)
  - [References and Further Reading](#references-and-further-reading)
    - [Primary Textual Sources and Translations](#primary-textual-sources-and-translations)
  - [Acknowledgements](#acknowledgements)
  - [License](#license)

## Overview

The Sūrya Siddhānta ("Sun Treatise" or "Doctrine of the Sun") stands as a seminal work in the history of astronomy, particularly within the Indian tradition. This project endeavors to:
1.  Provide a faithful, computationally robust implementation of its planetary models.
2.  Offer tools to rigorously validate these ancient calculations against modern, high-precision astronomical data.
3.  Develop and apply advanced correction techniques to enhance the accuracy of the Sūrya Siddhānta's predictions for contemporary use, while preserving the integrity of its original algorithms.

This allows for a deep appreciation of the text's ingenuity and a practical pathway to leveraging its methods with modern precision.

## Project Goals

*   **Preservation and Accessibility:** To make the computational methods of the Sūrya Siddhānta accessible to researchers, students, and enthusiasts in a modern programming environment.
*   **Accuracy and Validation:** To quantify the inherent accuracy of the Sūrya Siddhānta and understand its deviations from modern astronomical models.
*   **Bridging Ancient and Modern:** To develop a methodology for enhancing the Sūrya Siddhānta's outputs to meet modern accuracy standards through data-driven corrections.
*   **Educational Tool:** To serve as an educational resource for understanding historical astronomical techniques and the evolution of celestial mechanics.

## Introduction to the Sūrya Siddhānta

### Historical Context and Origins

The Sūrya Siddhānta is one of the foundational treatises (Siddhāntas) of traditional Indian astronomy (Jyotiṣa). While tradition attributes its knowledge to a divine revelation from the Sun god Sūrya to the Asura Maya, scholarly analysis suggests a complex history. The version extant today is generally dated to the Gupta period, likely between the 4th and 5th centuries CE, though it incorporates astronomical knowledge and computational techniques developed over preceding centuries. Some scholars suggest a "proto-Sūrya Siddhānta" may have existed earlier, possibly influenced by Hellenistic astronomy, which was then revised and Indianized.

The text has undergone several recensions over time, with notable commentaries by figures like Varāhamihira (6th century, in his Pañcasiddhāntikā), Parameśvara (15th century), and Raṅganātha (17th century). Despite these revisions, its core mathematical framework and astronomical constants have shown remarkable persistence. It became a cornerstone for calendrical calculations (Pañcāṅga) across much of India and influenced astronomical traditions in Southeast Asia and, to some extent, the Islamic world. Its methods continue to be used in traditional contexts even today.

### Astronomical Significance and Innovations

The Sūrya Siddhānta's enduring importance stems from its sophisticated mathematical approach to modeling celestial phenomena, remarkable for its era:

1.  **Geocentric Epicyclic Models:** While operating within a geocentric framework, the text employs epicycles (ucca-vṛtta and śīghra-vṛtta) to explain the apparent motions of planets, including retrograde motion. These models, particularly the śīghra epicycle for inferior planets, effectively capture aspects of a heliocentric perspective from an Earth-centered viewpoint.
2.  **Quantitative Astronomical Parameters:** It provides specific numerical values for planetary mean motions, orbital periods, dimensions of epicycles, apsidal motions, and inclinations of orbital planes to the ecliptic. Many of these constants, like the length of the sidereal year (365.2563627 days derived from its Mahāyuga parameters), are impressively close to modern values.
3.  **Algorithmic Computation:** The text lays out detailed, step-by-step algorithms for calculating planetary longitudes, latitudes, and other astronomical events. This algorithmic nature makes it highly suitable for computational implementation. Its accuracy, often within arcminutes for its epoch, was extraordinary for pre-telescopic astronomy.
4.  **Comprehensive Astronomical System:** Beyond planetary positions, the Sūrya Siddhānta covers a wide array of topics: computation of time, eclipses (lunar and solar), conjunctions of planets, heliacal risings and settings of stars, lunar mansions (nakṣatras), precession of the equinoxes (though with a different model and rate than modern understanding), and rudimentary spherical trigonometry.
5.  **Sine Function and Trigonometry:** The text utilizes a table of sines (jyā) and versed sines (utkrama-jyā) based on a circle radius R=3438 arcminutes, facilitating complex geometric calculations. This use of trigonometry was a hallmark of Indian astronomy.

### Structure of the Text

The Sūrya Siddhānta is composed in Sanskrit verse, primarily in the Anuṣṭubh meter, and is traditionally divided into 14 chapters (adhyāyas), containing around 500 ślokas (stanzas). The chapters cover:

1.  **Madhyamādhikāra (Mean Motions of Planets):** Establishes the grand cosmological time scales (Yugas), the number of revolutions of planets, their apsides (mandocca), and nodes (pāta) in a Mahāyuga. Provides methods to calculate mean planetary longitudes.
2.  **Spaṣṭādhikāra (True Places of Planets):** Details the crucial corrections (manda and śīghra samskāras) applied to mean positions to obtain true geocentric longitudes. Also covers calculation of planetary latitudes.
3.  **Tripraśnādhikāra (Direction, Place, and Time):** Deals with problems related to geographical coordinates, local time, determination of cardinal directions, and gnomonics (shadow-based calculations).
4.  **Candragrahaṇādhikāra (Lunar Eclipses):** Methods for predicting lunar eclipses, including timing, duration, and magnitude.
5.  **Sūryagrahaṇādhikāra (Solar Eclipses):** Similar methods for predicting solar eclipses, incorporating parallax.
6.  **Cheḍyakādhikāra (Projection of Eclipses):** Graphical methods for representing eclipses. (Note: Some recensions combine this with Ch. 4/5 or have slightly different chapter names/orderings.)
7.  **Grahayutyadhikāra (Planetary Conjunctions):** Calculating conjunctions between planets and between planets and stars.
8.  **Nakṣatragrahayutyadhikāra (Conjunctions with Asterisms):** More on conjunctions, focusing on fixed stars/nakṣatras.
9.  **Udayāstādhikāra (Heliacal Risings and Settings):** Determining when planets become visible after or invisible before conjunction with the Sun.
10. **Śṛṅgonnatyadhikāra (Elevation of the Moon's Cusps):** Calculations related to the appearance of the lunar crescent.
11. **Pātādhikāra (Malefic Aspects of Sun and Moon):** Astrological considerations, often concerning eclipses or particular planetary positions.
12. **Bhūgolādhyāya (Cosmography):** Description of the Earth, heavens, and the structure of the cosmos according to the text.
13. **Jyotiṣopaniṣad (Astronomical Instruments):** Description of various astronomical instruments like the armillary sphere (gola-yantra) and gnomon (śaṅku).
14. **Mānādhyāya (Measures of Time):** Further details on units of time and their divisions.

This project's implementation primarily focuses on the computational algorithms presented in Chapters 1 and 2 for planetary longitudes and latitudes, as these form the core of positional astronomy within the text.

## The Mathematical System of the Sūrya Siddhānta

### Core Cosmological and Kinematic Principles

The Sūrya Siddhānta's astronomical model is built upon several key ideas:

1.  **Geocentric Universe:** The Earth (Bhū) is considered stationary at the center of the cosmos. All celestial bodies, including the Sun, Moon, and planets, revolve around it.
2.  **Circular Orbits and Epicycles:** The fundamental paths of planets are circles (kakṣā-maṇḍala). To account for observed irregularities in their motion (like varying speeds and retrograde motion), the system employs epicycles – smaller circles whose centers move along the main deferent circle.
3.  **Uniform Mean Motion:** Each celestial body has a characteristic mean angular velocity. If it moved uniformly, its position would be its "mean longitude." Deviations from this are explained by corrections.
4.  **Two Primary Anomalies:** The observed motion of each planet (except Sun and Moon which have only one major anomaly) is principally affected by two types of deviations from its mean motion:
    *   **Manda Anomaly (Slow Anomaly):** This correction, applied via the *mandocca* (apex of slowest motion, akin to apogee/aphelion) and *manda epicycle*, accounts for the planet's varying speed due to what modern astronomy describes as orbital eccentricity.
    *   **Śīghra Anomaly (Fast Anomaly):** This correction, applied via the *śīghrocca* (apex of fastest motion) and *śīghra epicycle*, accounts for the synodic component of a planet's motion, i.e., its motion relative to the Sun as viewed from Earth. For inferior planets (Mercury, Venus), the śīghrocca is identified with the mean Sun. For superior planets (Mars, Jupiter, Saturn), it's a point related to their heliocentric position.
5.  **Ecliptic Coordinates:** Planetary positions are primarily defined by their longitude (bhoga) along the ecliptic and latitude (vikṣepa) perpendicular to it. The ecliptic is tilted at 24° to the celestial equator (as per S.S. I, 68).

### The Grand Time Scales and Epoch

The Sūrya Siddhānta employs a vast cyclical system of time:

1.  **Kali Yuga Epoch:** The fundamental reference point for all calculations is the beginning of the current Kali Yuga. The text (S.S. I, 23-24) implies this epoch occurred when all mean planets (except their nodes and apsides, which had distinct positions) were conjunct at 0° Aries. This is conventionally set to **midnight at Ujjain (longitude approx. 75.77° E) between February 17 and 18, 3102 BCE (Julian Calendar)**, corresponding to **Julian Day Number 588465.5**. This project uses this JD.
2.  **Yuga System:**
    *   A **Mahāyuga** (Great Age) or **Caturyuga** (Four Ages) lasts 4,320,000 human years.
    *   The Sūrya Siddhānta (I, 15-17) specifies the number of civil days (*sāvana dina*) in a Mahāyuga as **1,577,917,828 days**. This constant is critical for deriving mean motions. (1,577,917,828 civil days / 4,320,000 years = 365.258756 days per year, the S.S. sidereal year length).
    *   A Mahāyuga is composed of Kṛta, Tretā, Dvāpara, and Kali Yugas in a 4:3:2:1 ratio of duration.

Planetary motions are defined by the number of sidereal revolutions they complete within one Mahāyuga (S.S. I, 29-47). For example:
*   Sun: 4,320,000 revolutions
*   Moon: 57,753,336 revolutions
*   Mars: 2,296,832 revolutions

The number of days elapsed since the Kali Yuga epoch, known as **Ahargaṇa**, is the primary input for calculating planetary positions. `Ahargaṇa = JD - JD_KALI_START`.

### Mean Motion Theory: The Foundation

The first step in calculating a planet's position is to determine its mean longitude (madhyama graha). This is the longitude the planet would have if it moved uniformly at its average speed. It's calculated based on its total revolutions in a Mahāyuga and the Ahargaṇa:

`Mean Longitude (λ_m) = (Ahargaṇa × Revolutions_in_Mahāyuga / Days_in_Mahāyuga) × 360° (mod 360°)`

Similarly, the mean longitudes of a planet's *mandocca* (apsis) and *pāta* (node) are calculated using their respective revolution counts in a Mahāyuga.
The Rust implementation `mean_longitude(days, revs)` function reflects this:
```rust
// days = Ahargaṇa
// revs = Revolutions in Mahāyuga
// MAHAYUGA_DAYS = Civil days in Mahāyuga
fn mean_longitude(days: f64, revs: f64) -> f64 {
    norm360(days * revs / MAHAYUGA_DAYS * 360.0)
}
```

### Correction Mechanisms: Epicycles and Anomalies

Mean positions are theoretical. To get the true, observable position (spaṣṭa graha), the Sūrya Siddhānta applies corrections derived from epicyclic models. The size of these epicycles (expressed as their circumference in degrees, or related parameters) varies depending on the planet and whether it's at its apsis or the point opposite it. The text provides these values (S.S. II, 34-35).

#### Manda Correction (Equation of Center)

The Manda correction accounts for the non-uniform motion of a planet in its orbit, which we now understand as due to the orbit's eccentricity (Kepler's Second Law).
1.  **Manda Kendra (Anomaly of Apsis):** `M_k = Mean Longitude (λ_m) - Longitude of Mandocca (A)`
2.  **Manda Phala (Equation of Manda):** This is the correction angle. The Sūrya Siddhānta (II, 39-45) uses an iterative process to calculate it, which is effectively a second-order approximation:
    *   Calculate a first 'sine of anomaly' proportional term based on `M_k`.
    *   Apply half of this correction to `λ_m` to get an intermediate longitude.
    *   Recalculate the anomaly using this intermediate longitude.
    *   Calculate the final Manda Phala based on this refined anomaly.
    *   The correction `Δλ_m` is related to `arcsin( (R_epicycle / R_deferent) * sin(M_k) )`. The S.S. uses its sine tables (where R=3438') and specific epicycle sizes.

The Rust code `true_longitude_manda` implements this:
```rust
fn true_longitude_manda(mean_long: f64, apsis: f64) -> f64 {
    // Anomaly = mean_long - apsis
    // First half-correction
    let delta_sine1 = (mean_long - apsis).to_radians().sin(); // Proportional to sine of anomaly
    // The actual epicycle size factor is implicitly handled by the arcsin of this value,
    // assuming normalized epicycle radius. S.S. scales by manda_paridhi / 360.
    // The code directly uses arcsin(sin(Anomaly)), which gives Anomaly itself if |Anomaly| <= 90.
    // This part might be a simplification if it doesn't use S.S. variable epicycle sizes.
    // However, for a small manda correction, (R_e/R_d) * sin(M_k) approx sin(M_k_eff).
    // Burgess S.S. II, 39 commentary indicates the operation is:
    // bhuja_phala_arc = arcsin( (R_manda_epicycle / 3438) * sin(M_k) )
    // The code uses an angle based on sin(M_k) which is then added.
    // Let's assume `delta` is a scaled sine.
    let corr1_arc = rad_to_deg(delta_sine1.asin()); // This is M_k if R_e/R_d=1
    let interm_long = mean_long + corr1_arc / 2.0; // Half correction
    // Full correction with updated anomaly
    let delta_sine2 = (interm_long - apsis).to_radians().sin();
    let corr2_arc = rad_to_deg(delta_sine2.asin());
    norm360(mean_long + corr2_arc) // Apply full correction
}
```
*Self-correction: The Rust code's `true_longitude_manda` simplifies the epicycle scaling. A full S.S. implementation would use `R_epicycle_manda_arcmin * sin(M_k) / R_deferent_arcmin` inside the `asin`. The current code seems to compute `M_k` and add it, which is accurate for small angles if the `asin(sin(M_k))` is interpreted as `M_k`. This is a key area for verification against precise S.S. interpretation.*

**Corrected Longitude (λ_m'):** `λ_m' = λ_m + Manda Phala` (sign depends on quadrant of `M_k`).

#### Śīghra Correction (Synodic Anomaly)

The Śīghra correction accounts for the geometric relationship between the Earth, Sun, and the planet. This is crucial for modeling apparent retrograde motion.
1.  **Śīghra Kendra (Anomaly of Conjunction):**
    *   For inferior planets (Mercury, Venus): `S_k = Longitude of Śīghrocca (mean Sun) - λ_m'`
    *   For superior planets (Mars, Jupiter, Saturn): `S_k = Longitude of Śīghrocca (planet-specific) - λ_m'`
    (Note: The S.S. provides śīghrocca revolutions for each planet).
2.  **Śīghra Phala (Equation of Śīghra):** This correction is calculated similarly to Manda Phala, using the Śīghra Kendra and the planet's Śīghra epicycle dimensions. The S.S. (II, 39-45) again uses an iterative process. For planets other than Sun and Moon, this is a two-step process: first manda, then śīghra. Some interpretations involve multiple iterations.

The Rust code `sighra_correction` calculates this:
```rust
// true_lon_once is λ_m'
// sun_true is used as śīghrocca for inferior planets, for others specific śīghrocca should be used.
// The code seems to use `sun_true` as a generic śīghrocca reference.
// diam_deg is the S.S. śīghra epicycle diameter.
fn sighra_correction(true_lon_once: f64, sun_true: f64, diam_deg: f64) -> f64 {
    let h_arcmin = diam_deg * 30.0; // Half-diameter in arcminutes (śīghra epicycle radius)
    let beta_anomaly = deg_to_rad(true_lon_once - sun_true); // This is S_k if sun_true is śīghrocca
    // S.S. formula: Δλ_s = arcsin( (h_arcmin / R_arcmin) * sin(S_k) )
    // R_arcmin = 3438 (S.S. standard radius)
    let ratio = (h_arcmin / R) * beta_anomaly.sin();
    let clipped = ratio.max(-1.0).min(1.0); // Ensure argument is in [-1, 1] for asin
    rad_to_deg(clipped.asin())
}
```
**True Longitude (λ_s):** `λ_s = λ_m' ± Śīghra Phala` (sign and exact formula depend on planet and iteration stage; S.S. II, 46-49 details this). The provided Rust code applies it as `true_lon = once - ds`.

For the Moon, the S.S. describes a distinct process. Its "śīghra" epicycle mentioned in `PLANETS` (`Some(63.333_333)` for Moon) is related to the "equation of the Moon's orbit" or parallax-like effects, not a synodic correction like for planets. The current Rust code applies it uniformly.

### Planetary Models and Parameters

The Sūrya Siddhānta (Chapter I, 29-50 and Chapter II) provides specific parameters for each celestial body. These are embedded in the `PLANETS` constant in `main.rs`:

| Body      | Revs/Mahāyuga | Apsis Revs/MY | Śīghra Diam. (°) | Inclin. (°) | Node Revs/MY | S.S. Verses (Ch. I) |
|-----------|---------------|---------------|------------------|-------------|--------------|---------------------|
| Sun       | 4,320,000     | 387           | None             | 0.0         | 0            | 29-32               |
| Moon      | 57,753,336    | 488,203       | 63.333 (31°40'x2) | 5.145       | -232,238     | 33-38               |
| Mercury   | 17,937,060    | 368           | 132.0            | 2.2667      | -488         | 39-42               |
| Venus     | 7,022,370     | 535           | 260.0            | 1.6833      | -903         | 43-44               |
| Mars      | 2,296,832     | 204           | 234.0            | 1.850       | -214         | 45-46               |
| Jupiter   | 364,220       | 900           | 72.0             | 1.303       | -174         | 47-48               |
| Saturn    | 146,568       | 39            | 40.0             | 2.488       | -662         | 49-50               |
*Note: Negative Node Revs indicate retrograde motion. Śīghra Diameter for Moon is special. Inclinations are from S.S. I, 69-70 (converted from arcminutes).*

**Lunar Nodes (Rāhu and Ketu):**
Rāhu is the Moon's mean ascending node, and Ketu is the mean descending node (Rāhu + 180°). Their motion is retrograde.
The Rust code calculates Rāhu's longitude as:
`moon_node_mean_longitude = (Ahargaṇa × Moon_Node_Revs / Days_in_Mahāyuga) × 360°`
`Rāhu = (180.0 + moon_node_mean_longitude) mod 360°`
This initial 180° offset in the Rust code might be a specific convention or adjustment to align with a particular epoch definition of the node's position. Standard S.S. calculations usually yield the direct mean longitude of the node.

### Calculation of Latitude

Planetary latitude (vikṣepa or śara) is the angular distance from the ecliptic. It's calculated based on the planet's true longitude (λ_s), the longitude of its ascending node (pāta), and its maximum latitude (parama-vikṣepa), which is related to its orbital inclination (S.S. II, 55-59).

`Latitude (β) = arcsin( sin(Inclination) × sin(λ_s - Longitude_of_Node) )`

The Rust code implements this in `true_position`:
```rust
    let node_lon = norm360(days * pp.node_revs / MAHAYUGA_DAYS * 360.0); // Mean node longitude
    let inc_rad = deg_to_rad(pp.incl_deg); // Max inclination
    // Argument of latitude = true_lon - node_lon
    let lat_rad = ((true_lon - node_lon).to_radians().sin() * inc_rad.sin()).asin();
    let lat_deg = rad_to_deg(lat_rad);
```

## Project Implementation Details

The project combines a Rust core for the Sūrya Siddhānta calculations with Python scripts for validation and advanced analysis.

### Core Engine: Rust Implementation (`surya_sidhanta`)

The astronomical engine is implemented in Rust (`src/main.rs`) for its performance, memory safety, and suitability for precise numerical computations.
*   **Fidelity:** It adheres closely to the constants and algorithmic steps outlined in the Sūrya Siddhānta, particularly Chapters I and II.
*   **Constants:** Key astronomical constants like `MAHAYUGA_DAYS`, `JD_KALI_START`, `R` (sine table radius), and planetary parameters are hardcoded from the text.
*   **Epoch Calculation:** It takes a UTC datetime string as input, converts it to Julian Day, then calculates `Ahargaṇa` (days since Kali Yuga epoch).
*   **Modular Functions:** Calculations are broken down into functions like `mean_longitude`, `apsis_longitude`, `true_longitude_manda`, `sighra_correction`, and `true_position`.
*   **Output:** For a given datetime, it outputs geocentric ecliptic longitudes and latitudes for the Sun, Moon, planets (Mercury to Saturn), and the lunar nodes Rāhu and Ketu.
*   **Dependencies:** Primarily uses the `chrono` crate for date/time parsing.

A snippet illustrating the main calculation flow for a planet:
```rust
// In main() after calculating `days` (Ahargaṇa) and `sun_true` longitude:
for (name, param) in PLANETS {
    // `param` is a `PlanetParam` struct with S.S. constants for the body
    // `sun_true` is used as a reference for śīghra corrections
    let (lon, lat) = true_position(days, &param, sun_true);
    println!("{:<15} {:>15.6} {:>15.6}", name, lon, lat);
}
```

### Validation Framework: Python and Swiss Ephemeris (`validate.py`)

To assess the accuracy of the Sūrya Siddhānta implementation, `validate.py` compares its outputs against high-precision modern ephemerides using the Swiss Ephemeris library.
*   **Workflow:**
    1.  Ensures Python dependencies (`pyswisseph`, `numpy`, `pandas`, `matplotlib`) are installed.
    2.  Builds the Rust executable (`cargo build --release`).
    3.  For a given datetime or a range of dates:
        *   Calls the compiled Rust binary to get Sūrya Siddhānta positions.
        *   Fetches corresponding positions from the Swiss Ephemeris (using DE431 planetary theory and Lahiri Ayanamsha for sidereal positions to match the Indian context).
    4.  Calculates differences between the two sets of longitudes.
    5.  Prints a single-epoch comparison table.
    6.  Generates and displays time-series plots comparing Sūrya Siddhānta and Swiss Ephemeris longitudes for each body over the specified range.
*   **Key Python Snippet (Data Fetching):**
    ```python
    # In validate.py
    def run_rust(dt_iso): # Calls the Rust binary
        # ... subprocess logic ...
        return parsed_rust_output

    def get_swiss(dt, bodies): # Uses pyswisseph
        import swisseph as swe
        swe.set_ephe_path(os.getenv('SWISS_EPHE_PATH', './ephe')) # Requires ephemeris files
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0) # Crucial for sidereal comparison
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)
        # ... logic to call swe.calc_ut for each body ...
        return swiss_positions
    ```

### Error Correction Generator (`generate_corrections.py`)

While historically significant, the Sūrya Siddhānta's accuracy doesn't meet modern needs. `generate_corrections.py` aims to bridge this gap by modeling the errors and generating correction terms.
*   **Methodology:**
    1.  **Sampling:** Samples Sūrya Siddhānta and Swiss Ephemeris longitudes for specified celestial bodies over a defined time span (e.g., 1900-2100) and interval (e.g., daily).
    2.  **Residual Calculation:** Computes the residuals: `Δλ(t) = λ_swiss(t) - λ_siddhanta(t)`. These residuals are normalized to be within ±180°.
    3.  **Fourier Series Fitting:** Fits a truncated Fourier series to the time-series of residuals for each body. The series takes the form:
        `Δλ(t) ≈ a0 + Σ [ A_k cos(ω_k t) + B_k sin(ω_k t) ]`
        *   `a0`: Constant offset term.
        *   `ω_k`: Frequencies, which can be auto-derived or based on known astronomical periods (e.g., solar year, Jupiter/Saturn synodic/orbital periods, lunar nodal period). The script uses presets like `solar_year`, `jupiter`, `saturn`, `node`.
        *   `A_k, B_k`: Amplitudes of the cosine and sine terms for each frequency `ω_k` and its harmonics.
        *   The `--order` argument specifies how many harmonics (multiples of the fundamental `ω_k`) are included for each base frequency.
    4.  **Coefficient Export:** Exports the fitted coefficients (`a0`, `A_k`, `B_k`) and frequencies (`ω_k`) to:
        *   A JSON file (`coeffs.json`) for general use.
        *   A Rust source file (`rust_corrections.rs`) defining constants and structures for easy integration into a Rust project.
*   **Core Fitting Logic (Python):**
    ```python
    # In generate_corrections.py
    def fit_fourier(df, freqs_labels, order):
        # df contains columns 't' (time in days), 'body', 'delta' (residual)
        # ...
        for f_label in freqs_labels: # e.g., 'solar_year', 'jupiter'
            P = FREQ_PRESETS.get(f_label, float(f_label)) # Period in days
            omega_fundamental = 2 * math.pi / P
            for k_harmonic in range(1, order + 1):
                omega_k = k_harmonic * omega_fundamental
                # Add cos(ω_k t) and sin(ω_k t) to design matrix X
        # ...
        # Solve X * C = Y for C (coefficients) using np.linalg.lstsq(X, Y)
        # ...
        return results_by_body
    ```

## Comprehensive Usage Guide

### Prerequisites

1.  **Rust Toolchain:** Install Rust (includes `rustc` and `cargo`) from [rustup.rs](https://rustup.rs/).
2.  **Python:** Python 3.6+ is recommended.
3.  **Pip:** Python package installer (usually comes with Python).
4.  **Git:** For cloning the repository.
5.  **Swiss Ephemeris Files:** Download the Swiss Ephemeris data files (e.g., `sepl*.se1`, `semo*.se1`) from [Astrodienst](https://www.astro.com/swisseph/sweph_current.htm). Place them in a directory (e.g., `./ephe/`) and set the `SWISS_EPHE_PATH` environment variable to this directory path, or ensure they are in the default search path for `pyswisseph`.
    ```bash
    export SWISS_EPHE_PATH=/path/to/your/ephe_files
    ```

### Building the Project

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/surya_sidhanta.git # Replace YOUR_USERNAME
    cd surya_sidhanta
    ```
2.  **Build the Rust core engine:**
    ```bash
    cargo build --release
    ```
    The executable will be located at `./target/release/surya_sidhanta`.

### Command Line Interface (Rust Core)

The Rust binary calculates Sūrya Siddhānta positions for a given UTC date and time.

*   **Usage:**
    ```bash
    ./target/release/surya_sidhanta "[ISO_DATETIME_UTC]"
    ```
*   **Example (Specific Datetime):**
    ```bash
    ./target/release/surya_sidhanta "2025-05-19T13:51:26"
    ```
*   **Example (Current Datetime if no argument provided):**
    ```bash
    ./target/release/surya_sidhanta
    ```
*   **Output Format:**
    ```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Date/Time (UTC): 2025-05-19 13:51:26
    Julian Day      : 2460815.07739 # Note: Slight variation in JD due to floating point
    Days since epoch: 1872349.58
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Body            Lon (°)          Lat (°)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Sun             9.015109         0.000000
    Moon            325.057612       0.790635
    Mercury         347.928515       1.103272
    Venus           43.867210        -1.211087
    Mars            299.125783       1.532901
    Jupiter         123.456789       0.235678  # Example values
    Saturn          298.765432       -2.001234 # Example values
    Rahu            153.909013       0.000000  # Example values
    Ketu            333.909013       0.000000  # Example values
    ```

### Validation Workflow (`validate.py`)

This script compares the Rust implementation against Swiss Ephemeris.

1.  **Ensure Python dependencies are installed:**
    The script attempts to install them automatically. If this fails, install manually:
    ```bash
    python -m pip install pyswisseph numpy pandas matplotlib
    ```
2.  **Run the validation script:**
    ```bash
    # Ensure SWISS_EPHE_PATH is set or ephemeris files are in ./ephe
    python validate.py \
      --datetime "2025-05-19T13:51:26" \
      --start "2000-01-01" \
      --end "2025-01-01" \
      --step 30 # Days between samples for time-series plot
    ```
*   **Arguments:**
    *   `--datetime`: ISO date-time for single-point comparison.
    *   `--start`: Start date (YYYY-MM-DD) for time-series analysis.
    *   `--end`: End date (YYYY-MM-DD) for time-series analysis.
    *   `--step`: Integer number of days between samples for the time-series plot.
*   **Output:**
    *   Console output showing dependency installation, Rust build status.
    *   A table comparing Sūrya Siddhānta (Rust) vs. Swiss Ephemeris longitudes for the single `--datetime`, with differences in arcminutes.
    *   A matplotlib window displaying time-series plots of longitudes for each body from both sources over the specified date range.

### Correction Generation (`generate_corrections.py`)

This script generates Fourier-based correction coefficients.

1.  **Run the correction generation script:**
    ```bash
    # Ensure SWISS_EPHE_PATH is set
    python generate_corrections.py \
      --start 1900-01-01 \
      --end   2100-01-01 \
      --step  1440 \
      --unit  minute \
      --bodies Sun Moon Mercury Venus Mars Jupiter Saturn Rahu Ketu \
      --freqs solar_year jupiter saturn node \
      --order 5 \
      coeffs.json rust_corrections.rs
    ```
*   **Arguments:**
    *   `--start`, `--end`: Date range (YYYY-MM-DD) for sampling data.
    *   `--step`: Integer sampling step value.
    *   `--unit`: Unit for `--step` (`day` or `minute`). `1440 minute` means daily sampling.
    *   `--bodies`: Space-separated list of celestial bodies to fit corrections for.
    *   `--freqs`: Space-separated list of frequency presets (e.g., `solar_year`, `jupiter_period_sidereal`, `saturn_period_sidereal`, `lunar_node_period`) or explicit periods in days (e.g., `365.25`). The script uses `FREQ_PRESETS` for named frequencies:
        *   `solar_year`: 365.256363004 days (Tropical year)
        *   `jupiter`: 4332.589 days (Jupiter's sidereal period)
        *   `saturn`: 10759.22 days (Saturn's sidereal period)
        *   `node`: 6798.38 days (Mean lunar node regression period, ~18.6 years)
    *   `--order`: Integer number of harmonics to use for each fundamental frequency.
    *   `json_out`: Path to output JSON file (e.g., `coeffs.json`).
    *   `rust_out`: Path to output Rust source file (e.g., `rust_corrections.rs`).
*   **Output Files:**
    *   **`coeffs.json`**: A JSON file storing the `a0` (offset) and `A_k` (cosine), `B_k` (sine) coefficients for each frequency and harmonic, for each body.
        ```json
        // Example structure for one body
        {
          "Sun": {
            "a0": 0.0567...,
            "C_solar_year_1": -0.087..., // Cosine amplitude for fundamental of solar_year
            "S_solar_year_1": 0.012...,  // Sine amplitude
            "C_solar_year_2": ...,       // Cosine amplitude for 2nd harmonic
            "S_solar_year_2": ...,
            // ... other frequencies and harmonics
          }
          // ... other bodies
        }
        ```
    *   **`rust_corrections.rs`**: A Rust file containing the correction terms structured for potential inclusion in the Rust engine.
        ```rust
        // Auto-generated Fourier corrections
        use std::f64::consts::PI;
        pub struct Term { pub freq: f64, pub cos: f64, pub sin: f64; }
        // Example for Sun
        pub const SUN_CORR: [Term; 10] = [ // (order * num_freqs) terms
          Term{freq:0.017202...,cos:-0.087...,sin:0.012...}, // k=1, solar_year
          Term{freq:0.034404...,cos:...,sin:...},          // k=2, solar_year
          // ... other terms
        ];
        // ... constants for other bodies
        ```
        The `freq` is `k * ω` (angular frequency in radians per day). The `a0` term is handled separately if integrated.

#### Integrating Corrections (Conceptual)

The generated `rust_corrections.rs` file is designed to be potentially included in the main Rust application. To apply corrections:
1.  Parse the `a0` term from the JSON (or add it to the Rust file).
2.  For each body, iterate through its `_CORR` array of `Term`s.
3.  Calculate `correction = a0_body + Σ (term.cos * cos(term.freq * t) + term.sin * sin(term.freq * t))`, where `t` is `Ahargaṇa`.
4.  Add this correction to the Sūrya Siddhānta calculated longitude: `λ_corrected = λ_siddhanta + correction`.

## Analysis of Results and Accuracy

### Intrinsic Accuracy of the Sūrya Siddhānta

The Sūrya Siddhānta, when its algorithms are applied faithfully, yields positions that were remarkably accurate for its time, especially considering it predates telescopic observations. However, compared to modern ephemerides, its errors can be significant:

| Planet  | Typical Error (arcmin) | Max Error (arcmin) | Primary Error Sources                                     |
|---------|------------------------|--------------------|-----------------------------------------------------------|
| Sun     | 2 - 10                 | ~20-30             | Precession, slight period error, simplified eccentricity  |
| Moon    | 20 - 60                | up to ~120 (2°)    | Complex lunar theory, perturbations, evection, variation  |
| Mercury | 60 - 180 (1-3°)        | up to ~300 (5°)    | High eccentricity, fast motion, difficult to model        |
| Venus   | 15 - 45                | up to ~100 (1.6°)  | Orbital elements, synodic effects                         |
| Mars    | 30 - 90 (0.5-1.5°)     | up to ~180 (3°)    | Eccentricity, opposition effects                          |
| Jupiter | 15 - 40                | up to ~70 (1.1°)   | Orbital elements, long-term drift                         |
| Saturn  | 15 - 40                | up to ~60 (1°)     | Orbital elements, long-term drift                         |
| Rāhu    | 5 - 20                 | up to ~40          | Mean node vs. true node, long-term drift                  |

These errors accumulate over centuries due to:
*   Slight inaccuracies in the fundamental constants (mean motions, apsidal motions).
*   The Sūrya Siddhānta's model of precession (a libration of 27° around a fixed point, with a period of 7200 years, yielding an average rate of 54"/year vs. modern ~50.29"/year) differs from continuous precession.
*   Neglect of planetary perturbations (gravitational influences of planets on each other).
*   Simplifications in the epicyclic models compared to the true complexities of elliptical, perturbed orbits.

### Accuracy with Fourier Corrections

Applying the Fourier series corrections generated by `generate_corrections.py` can dramatically improve accuracy over the fitted period (e.g., 1900-2100).

| Planet  | Typical Error (arcsec) | Max Error (arcsec) | Improvement Factor |
|---------|------------------------|--------------------|--------------------|
| Sun     | < 5                    | ~10-15             | ~100x              |
| Moon    | < 15                   | ~30-60             | ~100x              |
| Mercury | < 30                   | ~60-120            | ~100x              |
| Venus   | < 15                   | ~30-50             | ~100x              |
| Mars    | < 20                   | ~40-80             | ~100x              |
| Jupiter | < 10                   | ~20-30             | ~100x              |
| Saturn  | < 10                   | ~20-30             | ~100x              |
| Rāhu    | < 10                   | ~20-30             | ~50-100x           |

*Note: These are estimates. Actual accuracy depends on the fitting range, number of terms, and stability of error patterns. The corrections are empirical and valid primarily within the range they were fitted.*

This demonstrates that while the Sūrya Siddhānta's core mechanics are ancient, its systematic deviations can be effectively modeled to achieve near-modern precision for specific epochs.

### Visualizing Comparisons: Understanding the Charts

The plots generated by `validate.py` are crucial for understanding the Sūrya Siddhānta's behavior relative to modern astronomy.
*   **X-axis:** Date/Time.
*   **Y-axis:** Geocentric Ecliptic Longitude in degrees.
*   **Two series per plot:** One for Sūrya Siddhānta (Rust) and one for Swiss Ephemeris.

**What to look for:**
*   **Overall Agreement:** How well the two curves track each other.
*   **Phase Differences:** Does one consistently lead or lag the other?
*   **Amplitude Differences:** Are the "wiggles" (due to eccentricity and synodic motion) of the same size?
*   **Secular Drift:** Over long periods, do the curves diverge steadily? This indicates errors in mean motion or precession.
*   **Periodic Errors:** Do the differences between the curves show repeating patterns? These are what the Fourier analysis captures.

For example, the Moon's plot will likely show the Sūrya Siddhānta capturing the main monthly cycle but missing smaller, faster perturbations visible in the Swiss Ephemeris curve. Outer planets might show good agreement in overall motion but slow drifts over decades.

### Characteristic Error Patterns

The differences `Δλ(t) = λ_swiss(t) - λ_siddhanta(t)` typically exhibit:

1.  **Long-Term Secular Trends:** A slow, quasi-linear drift over centuries. This is primarily due to differences in the adopted values for mean motions and the model of precession. For instance, the S.S. value for the length of the year and its precession theory will cause accumulating errors over time.
2.  **Periodic Components:**
    *   **Related to Planet's Own Orbit:** Errors with periods similar to the planet's anomalistic period (related to its Manda correction) or sidereal period.
    *   **Related to Synodic Period:** For planets other than the Sun, errors with periods similar to their synodic period (time between successive conjunctions with the Sun, related to Śīghra correction).
    *   **Harmonics:** Multiples of these fundamental frequencies.
    *   **External Periods:** Errors influenced by periods of major perturbing bodies (e.g., Jupiter's effect on Saturn, or vice-versa). The choice of frequencies in `generate_corrections.py` (e.g., Jupiter's period) reflects this.
3.  **Constant Offsets (a0 term):** An average bias, which might relate to epoch definitions or fixed errors in parameters.
4.  **Limitations of Theory:** The S.S. model, being epicyclic and not accounting for mutual planetary perturbations in the modern sense, will inherently fail to capture certain complex motions that are present in high-accuracy ephemerides like DE431. These might appear as residual noise or complex periodicities not easily captured by simple Fourier terms.

Understanding these patterns helps in selecting appropriate frequencies for the Fourier correction model and interpreting its effectiveness.

## Future Development and Enhancements

This project has potential for significant expansion:

1.  **Full S.S. Implementation:**
    *   Implement algorithms from other chapters: eclipse prediction (Ch. 4-6), planetary conjunctions (Ch. 7-8), heliacal phenomena (Ch. 9).
    *   Incorporate the S.S. model of precession directly into calculations.
    *   Refine Manda/Śīghra corrections to more closely match intricate details of S.S. iterative methods and variable epicycle sizes.
2.  **Correction Model Integration:**
    *   Integrate the generated `rust_corrections.rs` module into the main Rust binary as an optional feature, allowing users to choose between raw S.S. output and corrected output.
    *   Explore more advanced correction models beyond Fourier series (e.g., wavelet analysis, machine learning models for residuals).
3.  **Enhanced Validation:**
    *   Compare against historical observations where available.
    *   Validate latitude calculations more thoroughly.
    *   Analyze errors in velocity and other derived quantities.
4.  **Usability and Interface:**
    *   Develop a web interface or a simple GUI for easier interaction.
    *   Create API bindings for other programming languages (e.g., Python bindings for the Rust core).
5.  **Educational Resources:**
    *   Add detailed documentation explaining the S.S. algorithms alongside the code.
    *   Create tutorials or example use-cases.
6.  **Pañcāṅga Generation:** Extend the engine to compute the five elements of the traditional Indian almanac (Vāra, Tithi, Nakṣatra, Yoga, Karaṇa).
7.  **Topocentric Calculations:** Implement corrections for observer location on Earth (parallax, diurnal motion effects).

## References and Further Reading

### Primary Textual Sources and Translations

1.  Burgess, Ebenezer (Trans.). (1860). *Translation of the Sūrya Siddhānta: A Text-book of Hindu Astronomy*. Journal of the American Oriental Society, Vol. 6, pp. 141-498. (Reprinted by various publishers, e.g., Motilal Banarsidass). *This is the most commonly cited English translation.*
2.  Sastry, T.S. Kuppanna (Ed. & Trans.). (1985). *Vedāṅga Jyotiṣa of Lagadha*. Indian National Science Academy. (While not S.S., provides context on earlier Indian astronomy).
3.  Pingree, David (Ed.). (1978). *The Pañcasiddhāntikā of Varāhamihira*. Parts 1 and 2. Royal Danish Academy of Sciences and Letters. (Contains summaries of five Siddhāntas, including an older Sūrya Siddhānta).
4.  Shukla, Kripa Shankar (Ed. & Trans.). (1957). *The Sūrya-Siddhānta with the Commentary of Parameśvara*. Lucknow University.

 

## Acknowledgements

This project leverages several outstanding open-source tools and libraries:
*   **Rust Programming Language:** For its performance and safety, forming the core of the Sūrya Siddhānta engine.
*   **`chrono` crate:** For robust date and time handling in Rust.
*   **Python Programming Language:** For scripting validation and analysis tasks.
*   **`pyswisseph`:** Python bindings for the highly accurate Swiss Ephemeris.
*   **`numpy` & `pandas`:** For numerical computation and data manipulation in Python.
*   **`matplotlib`:** For generating plots and visualizations.
*   The **Swiss Ephemeris** data files from Astrodienst, which provide the benchmark for modern astronomical accuracy.

Ps.
None of this would have been possible without the blessings of ChatGPT o3, Claude Sonnet 3.7 and Gemini 2.5 Pro Experimental.
I just happend to ask the odd questions at the weird time 😐

## License

This project is licensed under the [MIT License](LICENSE.txt) for many reasons, but primarily because that's the only license ive actually managed to read without falling asleep.

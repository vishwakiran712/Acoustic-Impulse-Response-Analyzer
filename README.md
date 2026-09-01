# 🔊 Acoustic Impulse Response Analyzer

> An interactive room-acoustics laboratory for generating synthetic room impulse responses, analyzing reverberation and clarity parameters, visualizing energy decay and frequency response, and exporting acoustic measurement data.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt)
[![NumPy](https://img.shields.io/badge/Numerical-NumPy-orange?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-orange?logo=matplotlib)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img width="956" height="505" alt="image" src="https://github.com/user-attachments/assets/5a633904-cc59-4d91-9245-d07c9ff6e7b3" />


---

## 📌 Overview

**Acoustic Impulse Response Analyzer** is an interactive desktop application for studying the acoustic behavior of a simulated room through its **Room Impulse Response (RIR)**.

The application generates a synthetic impulse response consisting of:

* Direct sound arrival
* Early reflections
* Late reverberant energy
* Background noise

It then applies **Schroeder backward integration** to derive the Energy Decay Curve and calculates important room-acoustic parameters.

The analyzer provides quantitative measurements for:

* **RT60 / T30**
* **EDT**
* **C50**
* **C80**
* **Decay slope**
* **Peak arrival time**

It also displays the room's simulated frequency response and allows the generated impulse-response data to be exported as CSV.

The application runs at a **44.1 kHz sampling rate** and provides a dedicated educational reference panel explaining the acoustic parameters being calculated.

---

# ✨ Key Features

## 🏠 Synthetic Room Impulse Response Generation

The analyzer generates a room impulse response using a simplified acoustic model.

The simulated RIR contains four major components:

```text
              Room Impulse Response
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  Direct Arrival   Early Reflections  Late Reverberation
                                         │
                                         ▼
                                   Noise Floor
```

This provides a controlled environment for studying how different room parameters influence the resulting impulse response.

---

# ⚙️ Room Parameters

The simulator exposes several parameters that influence the generated acoustic environment.

| Parameter                  | Description                              |
| -------------------------- | ---------------------------------------- |
| **Room Dimensions**        | Defines the simulated room geometry      |
| **Speed of Sound**         | Acoustic propagation velocity            |
| **Reflection Density**     | Controls the density of late reflections |
| **Absorption Coefficient** | Controls acoustic energy absorption      |
| **Reverb Time T60**        | Target reverberation time                |
| **Noise Floor**            | Background noise level                   |

The application provides controls for speed of sound, reflection density, absorption coefficient, target T60, and noise-floor level.

---

# 🔊 Direct Sound

The simulated RIR begins with a direct-arrival component representing the initial acoustic energy reaching the receiver.

The direct arrival establishes the primary impulse and is used as the temporal reference for subsequent acoustic analysis.

The application tracks the impulse peak and calculates its arrival time as one of the measured parameters.

---

# 🪞 Early Reflections

Early reflections are modeled as discrete sparse reflections following the direct sound.

The simulator generates multiple reflection events within an approximately **80 ms early-reflection window**.

These reflections are influenced by:

* Reflection coefficient
* Arrival time
* Distance-related attenuation
* Randomized reflection positions

This provides a simplified model of the early acoustic field of a room.

---

# 🌊 Late Reverberant Tail

The late reverberation is modeled as a stochastic noise process multiplied by an exponential decay envelope.

The decay is controlled by the target reverberation time:

```text id="m6w9hz"
T60 Target
    │
    ▼
Decay Constant
    │
    ▼
Exponential Envelope
    │
    ▼
Late Reverberant Tail
```

The resulting tail represents the gradual loss of acoustic energy after the direct sound and early reflections.

---

# 🔇 Background Noise

A configurable background noise floor is added to the generated impulse response.

The noise level is specified in decibels, allowing the user to study the influence of measurement noise on the acoustic decay analysis.

---

# 📉 Schroeder Energy Decay Curve

The analyzer calculates the Energy Decay Curve using **backward Schroeder integration**.

The squared impulse response is integrated backwards from the end of the response:

```text id="4u0s9e"
h(t)
 │
 ▼
h²(t)
 │
 ▼
Backward Integration
 │
 ▼
Energy Decay Curve
 │
 ▼
EDC in dB
```

Mathematically:

```text
E(t) = ∫ₜ∞ h²(τ)dτ
```

The resulting curve provides a smooth representation of the room's acoustic energy decay and forms the basis for the reverberation-time calculations.

---

# ⏱️ RT60 / T30

**RT60** represents the time required for acoustic energy to decay by 60 dB.

The application estimates RT60 using a **T30-style extrapolation**, fitting the decay between:

```text id="a8eqs1"
-5 dB
   ↓
-35 dB
```

The fitted decay slope is extrapolated to a 60 dB decay.

Conceptually:

```text
  0 dB ────────●
              /
             /
 -5 dB ─────●
           /
          /
-35 dB ─●
       /
      /
-60 dB ────────────────►
          extrapolation
```

The resulting value is displayed as:

```text
RT60 (T30 Extrapolated)
```

in seconds.

---

# 🌅 Early Decay Time — EDT

**Early Decay Time (EDT)** focuses on the initial portion of the room's energy decay.

The application calculates EDT using the:

```text id="2j6o3n"
0 dB → -10 dB
```

decay region and extrapolates the result to a 60 dB decay.

EDT is useful for characterizing the early perceptual impression of reverberance and can differ from the longer-term RT60 measurement.

---

# 🎤 C50 — Speech Clarity

The analyzer calculates **C50**, which compares early acoustic energy arriving within the first 50 ms against later reverberant energy.

```text id="g7w8rj"
C50 =
10 log₁₀
(Early Energy 0–50 ms /
 Late Energy >50 ms)
```

Higher C50 generally indicates greater early-to-late energy dominance, which is useful when evaluating speech clarity.

---

# 🎼 C80 — Music Clarity

The analyzer also calculates **C80**, using an 80 ms boundary:

```text id="d2t8c4"
C80 =
10 log₁₀
(Early Energy 0–80 ms /
 Late Energy >80 ms)
```

This provides an acoustic indicator of the balance between early energy and the reverberant tail for music-oriented analysis.

---

# 📐 Decay Slope

The application calculates the decay slope in:

```text
dB/s
```

from the fitted reverberation decay.

The slope provides a direct representation of how rapidly acoustic energy decreases within the room model.

---

# 📍 Peak Arrival Time

The analyzer identifies the impulse-response peak and reports its arrival time in milliseconds.

```text
Peak Arrival
     │
     ▼
Time Reference
     │
     ▼
Acoustic Arrival Analysis
```

This provides a basic temporal measurement of the simulated direct acoustic arrival.

---

# 📡 Room Frequency Response

The generated RIR is transformed into the frequency domain using a real FFT.

The application calculates:

```text id="g3z2r8"
FFT Magnitude
      │
      ▼
20 log₁₀(|H(f)|)
      │
      ▼
Room Frequency Response
```

The frequency response is displayed from approximately:

```text
20 Hz → 20 kHz
```

using a logarithmic frequency axis.

This provides a spectral representation of the simulated room transfer function.

---

# 📊 Three-Stage Visualization

The application combines the main acoustic results into a dedicated visualization area.

### 1. Impulse Response

Shows:

* Direct arrival
* Early reflections
* Reverberant tail
* Background noise

### 2. Energy Decay

Shows:

* Schroeder energy decay curve
* Decay behavior
* Reverberation characteristics

### 3. Frequency Response

Shows:

* Room transfer function
* Magnitude in dB
* Frequency-dependent acoustic behavior

The interface explicitly groups these visualizations as **Impulse Response, Energies & Frequency Spectrum**.

---

# 📈 Measured Acoustic Indicators

The application displays the following metric cards:

| Metric           | Unit | Purpose               |
| ---------------- | ---: | --------------------- |
| **RT60 / T30**   |    s | Reverberation time    |
| **EDT**          |    s | Early decay time      |
| **Decay Slope**  | dB/s | Rate of energy decay  |
| **C50**          |   dB | Speech clarity        |
| **C80**          |   dB | Music clarity         |
| **Peak Arrival** |   ms | Direct-arrival timing |

These metrics are calculated directly from the generated impulse response and Schroeder energy decay curve.

---

# 🧠 Acoustic Analysis Pipeline

```text
┌───────────────────────────────┐
│       Room Parameters         │
│                               │
│ Dimensions / Absorption       │
│ Reflection Density / T60      │
│ Noise Floor / Sound Speed     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Synthetic RIR Generation    │
│                               │
│ Direct Sound                  │
│ Early Reflections             │
│ Late Reverberation            │
│ Background Noise              │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Energy Calculation      │
│                               │
│          h²(t)                │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Schroeder Backward          │
│       Integration             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      Energy Decay Curve       │
│             EDC               │
└───────────────┬───────────────┘
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
     RT60      EDT      C50/C80
       │        │         │
       └────────┼─────────┘
                ▼
┌───────────────────────────────┐
│       Acoustic Metrics        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       FFT Analysis            │
│                               │
│       Room Frequency          │
│          Response             │
└───────────────────────────────┘
```

---

# 🧪 Example Experiments

## Experiment 1 — Reverberation Time

Set a target:

```text
T60 = 1.2 s
```

Generate the RIR and compare the measured T30-extrapolated RT60 against the target.

Observe:

* Energy decay
* Decay slope
* RT60

---

## Experiment 2 — Absorption Coefficient

Run the simulator with different absorption values:

```text
α = 0.10
α = 0.25
α = 0.50
α = 0.75
```

Compare how increased absorption changes the reverberant behavior.

---

## Experiment 3 — Reflection Density

Change:

```text
Reflection Density
```

from a low value to a high value.

Observe the change in the density and appearance of the reverberant field.

---

## Experiment 4 — Speech Clarity

Compare C50 values under different reverberation settings.

Observe how changes in the early-to-late energy ratio influence the calculated speech-clarity indicator.

---

## Experiment 5 — Music Clarity

Compare C80 across different room conditions.

This provides a simple demonstration of how room decay characteristics affect early versus late acoustic energy.

---

## Experiment 6 — Frequency Response

Generate several room configurations and compare their frequency responses.

Look for:

* Resonant regions
* Spectral peaks
* Frequency-dependent attenuation
* Changes in room transfer characteristics

---

# 🎓 Educational Applications

This project can be used to demonstrate:

* Room Acoustics
* Acoustic Impulse Responses
* Reverberation
* RT60
* T30
* EDT
* C50
* C80
* Schroeder Integration
* Energy Decay Curves
* Acoustic Clarity
* Frequency Response
* FFT
* Room Transfer Functions
* Reflection Modeling
* Absorption
* Acoustic Measurement Concepts
* Digital Signal Processing

---

# 🛠️ Technology Stack

| Technology     | Purpose                                           |
| -------------- | ------------------------------------------------- |
| **Python**     | Core application                                  |
| **NumPy**      | Signal generation, numerical calculations and FFT |
| **PyQt5**      | Desktop graphical interface                       |
| **Matplotlib** | Acoustic-response visualization                   |

The current implementation uses a 44.1 kHz sampling frequency and embeds Matplotlib inside the PyQt5 interface.

---

# 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/vishwakiran712/Acoustic-Impulse-Response-Analyzer.git
cd Acoustic-Impulse-Response-Analyzer
```

### 2. Install dependencies

```bash
pip install numpy matplotlib PyQt5
```

### 3. Run the analyzer

```bash
python app.py
```

---

# 💾 CSV Export

The analyzer can export the generated impulse response and Energy Decay Curve to CSV.

The exported dataset contains:

```text
Time_s
ImpulseResponse_Amplitude
EnergyDecayCurve_dB
```

This makes the generated acoustic data available for further analysis in:

* Python
* MATLAB
* Excel
* Acoustic-analysis workflows
* Custom DSP pipelines

The export functionality is implemented directly in the application using NumPy CSV output.

---

# 📂 Project Structure

```text
Acoustic-Impulse-Response-Analyzer/
│
├── app.py
├── README.md
└── LICENSE
```

---

# 🔭 Possible Future Enhancements

Potential extensions include:

* Measured microphone RIR import
* WAV impulse-response loading
* Real room measurement workflow
* MLS excitation
* Exponential sine sweep measurement
* Octave-band RT60 analysis
* Frequency-dependent absorption
* Room dimension visualization
* Source/receiver positioning
* Image-source room modeling
* Early reflection visualization
* ETC / Energy Time Curve
* Clarity parameter plots
* Definition / D50
* Strength G
* Center Time Ts
* STI estimation
* Waterfall plots
* Spectrograms
* Binaural room impulse responses
* 3D room visualization
* Acoustic treatment simulation

---

# 📜 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

# 👨‍💻 Author

**Vishwakiran B.V.S.**

Engineering • Sports Technology • Product Research • Scientific Computing • Acoustics • Signal Processing

GitHub: [@vishwakiran712](https://github.com/vishwakiran712)

---

# ⭐ Project

If you find this project useful for learning, acoustic experimentation, or DSP research, consider giving the repository a ⭐.

**Repository:**
https://github.com/vishwakiran712/Acoustic-Impulse-Response-Analyzer

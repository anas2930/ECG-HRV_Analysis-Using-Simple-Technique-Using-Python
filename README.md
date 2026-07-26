What you'll learn

By the end of this walkthrough you'll understand how to:

Load and inspect a real clinical ECG recording
Visualize a raw ECG signal
Filter out noise (baseline drift, powerline interference) without distorting the heartbeat
Detect R-peaks (the sharp spikes that mark each heartbeat) and check your detector against expert-labeled ground truth
Turn a list of heartbeat timestamps into Heart Rate Variability (HRV) metrics
Prerequisites
Basic Python (loops, functions, arrays)
High-school-level familiarity with the idea of a "signal" — don't worry, the ideas below are explained from scratch
bash
pip install wfdb numpy scipy matplotlib
Getting the data

This repo does not include the raw ECG files — you download them directly from PhysioNet, the free, open archive that hosts the MIT-BIH Arrhythmia Database. Easiest way, right from Python:

python
import wfdb
wfdb.dl_database('mitdb', dl_dir='mitdb', records=['100'])

This pulls down the .dat (raw signal), .hea (header/metadata), and .atr (expert annotations — where a cardiologist marked every real heartbeat) files for those two records. Run your scripts from inside that folder, or point wfdb.rdrecord() at the right path.

What is MIT-BIH? It's the most widely used public ECG dataset in research — about 48 half-hour recordings, digitized at 360 Hz, each hand-annotated beat-by-beat by cardiologists. It's the standard benchmark almost every QRS/R-peak detection paper tests against.

Step 1 — Load the data and look at what's inside

File: step_01_load_data.py

An ECG record isn't just one number — wfdb gives you an object with the signal itself plus metadata: sampling frequency, number of leads, duration, etc.

Key idea — sampling frequency (fs): the ECG isn't a smooth continuous line in your computer; it's thousands of discrete voltage measurements per second. MIT-BIH records at 360 Hz, meaning 360 voltage readings every second. Higher fs = finer time resolution, but more data to process.

This step is just about getting comfortable with the object: how long is the recording, how many leads (channels) does it have, what does the raw array look like.

Step 2 — Visualize the raw signal

File: step_02_visualize_raw.py

Before doing anything else to a signal, look at it. This step builds a time axis (since the raw data is just a list of voltages with no explicit timestamps) and plots the first several seconds.

Key idea — building a time axis: if you have fs samples per second, then sample number i occurred at time i / fs seconds. That's literally the whole formula (np.arange(len(signal)) / fs).

At this stage the signal will look noisy and "off" compared to a textbook ECG — there's usually a slow wandering baseline and some high-frequency noise sitting on top of the heartbeat waveform. That's expected, and it's exactly what Step 3 fixes.

Step 3 — Filtering

File: step_03_filter.py

Raw ECG is contaminated by things that aren't the heartbeat:

Baseline wander (very low frequency, <0.5 Hz) — caused by breathing, body movement, electrode contact shifting
High-frequency noise (>40 Hz) — muscle activity, electronics

The clinically useful part of an ECG waveform lives roughly between 0.5 Hz and 40 Hz, so a bandpass filter that keeps that range and discards everything else cleans the signal up dramatically. This matches the frequency range commonly used with hardware front-ends like the AD8232 sensor.

Key idea — Butterworth filter: a standard, "maximally flat" filter design — it doesn't ring or distort the passband much, which matters because we don't want to distort the actual heartbeat shape while removing noise. The butter() call here uses a 3rd-order filter, a reasonable default for ECG work.

Key idea — filtfilt vs lfilter: filtfilt runs the filter forward, then backward, which cancels out the phase delay a normal filter would introduce. Phase delay would shift your peaks in time, which would ruin any timing-based analysis (like the beat intervals we care about in Step 4 and Step 6) — so filtfilt is the correct choice for this kind of offline analysis.

Step 4 — R-peak detection and validation

File: step_04_r_peak_detection.py

The R-peak is the tall, sharp spike in each heartbeat — it's the easiest and most reliable point to detect, so basically every heart-rate algorithm is built around finding R-peaks first.

This step:

Normalizes the filtered signal (zero mean, unit variance) so a single prominence threshold works across different recordings
Uses scipy.signal.find_peaks with a minimum distance constraint based on a physiologically realistic maximum heart rate (200 bpm here) — this stops the detector from picking two peaks that are impossibly close together
Validates against the ground truth: MIT-BIH's .atr annotation files contain the true beat locations, hand-labeled by cardiologists. Comparing your detected peaks against those (within a tolerance window, here 50 ms) gives standard detector-performance metrics — on Record 100, this pipeline hits 99.6% Sensitivity and 98.05% Precision, which is a genuinely strong result for a fairly simple threshold-based detector:
Sensitivity — of all real beats, what fraction did you catch?
Precision — of everything you flagged as a beat, what fraction was real?
F1 score — a single number balancing the two
DER (Detection Error Rate) — combines false positives and false negatives relative to true beats; commonly reported in QRS-detection literature

This peak detector (threshold + minimum-distance) is a simplified version of the ideas behind the classic Pan–Tompkins algorithm (see references below), which most real-world detectors are still based on in some form.

Step 5 — (add your own step here if you have one)

If you have an R-peak refinement or beat-classification step between detection and HRV analysis, this is where it goes. Otherwise, renumber your HRV script to step_05 so the sequence has no gap.

Step 6 — Heart Rate Variability (HRV) analysis

File: step_06_hrv_analysis.py

Once you know when every heartbeat happened, you can compute how much the time between beats varies — that's HRV, a well-studied marker of autonomic nervous system activity.

R-R intervals — the time gap between consecutive R-peaks, in milliseconds
Artifact removal — intervals outside a physiologically plausible range (here 400–1500 ms, i.e. 40–150 bpm) are discarded, since a missed or extra detected peak would otherwise show up as an impossible interval and badly skew the stats
Time-domain HRV metrics:
SDNN — standard deviation of all R-R intervals; reflects overall variability
RMSSD — root mean square of successive differences; more sensitive to short-term, beat-to-beat changes
pNN50 — percentage of successive R-R interval differences greater than 50 ms

These three are the standard starting set in HRV literature — see the Task Force reference below for the full clinical standard (there's also a frequency-domain side — LF/HF ratio via power spectral density — as a natural next step if you want to extend this).

Note on this script: it re-fetches fs from record.fs, then immediately overwrites it with a hardcoded 360. That works because MIT-BIH is always 360 Hz, but it's fragile — worth using record.fs consistently if you reuse this code on other datasets

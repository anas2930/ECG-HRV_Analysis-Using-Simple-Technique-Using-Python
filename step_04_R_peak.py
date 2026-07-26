import wfdb
import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt

# -----------------------------
# Load MIT-BIH Record
# -----------------------------
record_name = "100"

record = wfdb.rdrecord(record_name,sampto=30*60*360)
annotation = wfdb.rdann(record_name, 'atr')

fs = record.fs
signal = record.p_signal[:, 0]

# -----------------------------
# Bandpass Filter
# -----------------------------
nyquist = 0.5 * fs

b, a = sps.butter(3,
                  [0.5/nyquist, 40.0/nyquist],
                  btype='band')

cleaned_signal = sps.filtfilt(b, a, signal)

# -----------------------------
# Normalize
# -----------------------------
norm_signal = (cleaned_signal - np.mean(cleaned_signal)) / np.std(cleaned_signal)

# -----------------------------
# Peak Detection
# -----------------------------
max_hr_bpm = 200

min_gap_seconds = 60 / max_hr_bpm
min_gap_samples = int(fs * min_gap_seconds)

peak_indices, _ = sps.find_peaks(
    norm_signal,
    distance=min_gap_samples,
    prominence=0.5
)

print("Detected beats :", len(peak_indices))

# ==========================================================
# Read Reference (.atr)
# ==========================================================

valid_symbols = [
    'N','L','R','A','a','J','S',
    'V','E','F','e','j','/',
    'f','Q'
]

mask = np.isin(annotation.symbol, valid_symbols)

reference_peaks = annotation.sample[mask]

print("Reference beats:", len(reference_peaks))

# ==========================================================
# Compare Detected Peaks with Reference
# ==========================================================

tolerance_ms = 50
tolerance = int(fs * tolerance_ms / 1000)

matched = np.zeros(len(reference_peaks), dtype=bool)

TP = 0
FP = 0

for detected in peak_indices:

    distance = np.abs(reference_peaks - detected)

    nearest = np.argmin(distance)

    if distance[nearest] <= tolerance:

        if not matched[nearest]:
            TP += 1
            matched[nearest] = True
        else:
            FP += 1

    else:
        FP += 1

FN = np.sum(~matched)

# ==========================================================
# Performance Metrics
# ==========================================================

Sensitivity = TP / (TP + FN)

Precision = TP / (TP + FP)

F1 = 2 * TP / (2 * TP + FP + FN)

DER = (FP + FN) / TP

print("\n=========== PERFORMANCE ===========")

print(f"True Positive : {TP}")
print(f"False Positive: {FP}")
print(f"False Negative: {FN}")

print(f"Sensitivity   : {Sensitivity*100:.2f}%")
print(f"Precision     : {Precision*100:.2f}%")
print(f"F1 Score      : {F1*100:.2f}%")
print(f"DER           : {DER:.4f}")

# ==========================================================
# Visualization
# ==========================================================

time = np.arange(len(signal)) / fs

seconds_to_show = 20

n_samples = int(seconds_to_show * fs)

visible_detected = peak_indices[peak_indices < n_samples]
visible_reference = reference_peaks[reference_peaks < n_samples]

plt.figure(figsize=(14,5))

plt.plot(time[:n_samples],
         cleaned_signal[:n_samples],
         color='black',
         label='Filtered ECG')

plt.scatter(time[visible_reference],
            cleaned_signal[visible_reference],
            color='green',
            marker='o',
            s=50,
            label='Reference (.atr)')

plt.scatter(time[visible_detected],
            cleaned_signal[visible_detected],
            color='red',
            marker='v',
            s=60,
            label='Detected')

plt.title(f"Record {record_name}")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (mV)")
plt.legend()

plt.show()
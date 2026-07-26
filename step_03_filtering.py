import wfdb
import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt

record_name = "100"
record = wfdb.rdrecord(record_name)
fs = record.fs
signal = record.p_signal[:, 0]

# Filter Design for ECG signal, according to literature, typical frequencies , like used
# in AD8232 sensor as well, lies between~ 0.5-40Hz, in order to remove the dc drift (low freq) and upper range freq

low_f = 0.5 # lower cut off
high_f = 40.0 # high cut off

nyquist = 0.5 * fs # fixed formula , needs to be understood
# for scipy filter design, it's necessary to scale the filter between 0 and 1 (normalization)  
low = low_f / nyquist
high = high_f / nyquist
# Understanding of basic filters and their attenuation is encouraged, also little bit about the signals and systems for (b,a) paramters
b, a = sps.butter(3, [low, high], btype='band') #It'll return two values 
cleaned_signal = sps.filtfilt(b, a, signal) #Use filtfilt to implement filter on signal

# Now, compare the signals
time = np.arange(len(signal)) / fs
seconds_to_show = 10
n_samples = int(fs * seconds_to_show)

plt.figure(figsize=(12, 4))
plt.plot(time[:n_samples], signal[:n_samples], color='k', alpha=1, label='Raw Signal')
plt.plot(time[:n_samples], cleaned_signal[:n_samples], color='green', label='filtered Signal')
plt.title(f"Raw vs Filtered ECG  {record_name}")
plt.xlabel("Time (seconds)")
plt.ylabel("Voltage (mV)")
plt.legend()
plt.grid(True) #optional
plt.show() 
import wfdb
import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sps

desired_min = 30 # input of time in min from the user 
sampto = int(desired_min * 60 * 360) #Command is coverting min to no. of samples in that specific time 

record = wfdb.rdrecord("100", sampto=sampto) #Now paste the samples amount in this function to get the interested samples    

fs = record.fs
signal = record.p_signal[:, 0] # Taking lead 1 signal

nyquist = 0.5 * fs
b, a = sps.butter(3, [0.5/nyquist, 40.0/nyquist], btype='band')
b_n,a_n= sps.iirnotch(50,34,fs)
#b_n_2,a_n_2= sps.iirnotch(60,34,fs)
cleaned_signal_1 = sps.filtfilt(b, a, signal)
cleaned_signal = sps.filtfilt(b_n, a_n, cleaned_signal_1)

norm_signal = (cleaned_signal - np.mean(cleaned_signal)) / np.std(cleaned_signal)
min_gap_samples = int(fs * (60.0 / 200))
peaks, _ = sps.find_peaks(norm_signal, distance=min_gap_samples, prominence=0.5)

# Now, we'll be calculating the clinically important parameters  
fs = 360 #sampling frequency

# STEP 1: R-R peak intervals 
rr_ms = np.diff(peaks) / fs * 1000

# STEP 2: Filtering artifact (physiologically impossible values)
valid = (rr_ms > 400) & (rr_ms < 1500)   # 40-150 bpm range is actually tunabel and it's approximated based on the resting phase of patients 
rr_clean = rr_ms[valid]
rr_times = np.cumsum(rr_clean) / 1000     # This is cumulative 

# STEP 3: TIME-DOMAIN HRV
sdnn = np.std(rr_clean)
rmssd = np.sqrt(np.mean(np.diff(rr_clean) ** 2))
nn50 = np.sum(np.abs(np.diff(rr_clean)) > 50)
pnn50 = nn50 / len(rr_clean) * 100

# Visualization
print(f"SDNN:  {sdnn:.2f} ms")
print(f"RMSSD: {rmssd:.2f} ms")
print(f"pNN50: {pnn50:.2f} %")
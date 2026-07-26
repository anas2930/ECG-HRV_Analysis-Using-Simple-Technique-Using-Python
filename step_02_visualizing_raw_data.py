import wfdb # important for reading and analysis of the data
import numpy as np # necessary for faster computation
import matplotlib.pyplot as plt # important for visualization (can use others too )

record_name = "100" #patient id 
record = wfdb.rdrecord(record_name) #reading the data contained in id
fs = record.fs #sampling frequency
signal = record.p_signal[:, 0] #to extract the data contained in first columns (MLII) 

# Data doesn't contain any x axis, so we need to make the time axis in order to 
# compare the sample on its secific interval (can also be done in minutes by deviding with /hr), so
time = np.arange(len(signal)) / fs

# Now let's define the time to read the samples contained in that specific time
seconds_to_show = 10  # we can also take input from user, (1805 seconds max) 
n_samples = int(fs * seconds_to_show) # now multiply the time with samples per second to get totol samples

# Visualization
plt.figure(figsize=(12, 4))
plt.plot(time[:n_samples], signal[:n_samples])
plt.title(f"Raw ECG signal: Record {record_name} , \n ( first {seconds_to_show} seconds)")
plt.xlabel("Time (seconds)")
plt.ylabel("Voltage (mV)")
plt.grid(True)
plt.show() 
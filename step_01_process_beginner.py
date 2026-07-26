import wfdb
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
# ENTER THE PATIENT ID (222, 223, ya 231)
record_name = "100"

record = wfdb.rdrecord(record_name) # similar to pd.read_csv() etc. command to read file 

print(" sampling frequency (fs):", record.fs) # frequency at which the signal is sampled (high fs = more finedetails between intervals )
print(" total samples:", record.sig_len) # lentgh of total samples recorded
print(" totoal time (seconds):", record.sig_len / record.fs) # scale the no. of samples per 1 sec (samples) to get the total time od samples
print("Leads:", record.sig_name) # how many leads data it contains (currently 2)
print("Shape of signal data:", record.p_signal.shape) # to get the info of data's columns and rows
print(record.p_signal[:,0]) # slicing to get all rows of column 2
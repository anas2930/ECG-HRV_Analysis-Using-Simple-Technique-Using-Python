import scipy.signal as sps
import numpy as np

def pan_tompkins_s(ecg, fs):

    nyquist = 0.5 * fs
    b, a = sps.butter(2, [5/nyquist, 15/nyquist], btype='band')
    filtered = sps.filtfilt(b, a, ecg)

    derivative = np.diff(filtered, prepend=filtered[0])
    squared = derivative ** 2

    window_size = int(0.15 * fs)
    integrated = np.convolve(squared, np.ones(window_size)/window_size, mode='same')

    peaks = []
    spki, npki, threshold1 = 0.0, 0.0, 0.0
    last_peak_idx = 0
    rr_history = []

    candidate_peaks, _ = sps.find_peaks(integrated, distance=int(0.2*fs))

    for idx in candidate_peaks:
        peak_val = integrated[idx]
        if peak_val > threshold1:
            spki = 0.125 * peak_val + 0.875 * spki
            peaks.append(idx)
            if last_peak_idx != 0:
                rr_history.append(idx - last_peak_idx)
                if len(rr_history) > 8:
                    rr_history.pop(0)
            last_peak_idx = idx
        else:
            npki = 0.125 * peak_val + 0.875 * npki
        threshold1 = npki + 0.25 * (spki - npki)

        if rr_history:
            avg_rr = np.mean(rr_history)
            if last_peak_idx != 0 and (idx - last_peak_idx) > 1.66 * avg_rr:
                threshold1 *= 0.5

    return np.array(peaks)
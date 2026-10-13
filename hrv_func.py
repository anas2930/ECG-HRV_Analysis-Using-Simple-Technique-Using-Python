import numpy as np
def compute_hrv(peaks, fs):
    """Standard time-domain HRV from detected peak indices. Does not
    touch or depend on any Pan-Tompkins algorithm internals -- purely
    a post-processing step on the returned peak array."""
    if len(peaks) < 3:
        return None

    rr_ms = np.diff(np.sort(peaks)) / fs * 1000
    valid = (rr_ms > 400) & (rr_ms < 1500)
    rr_clean = rr_ms[valid]

    if len(rr_clean) < 2:
        return None

    sdnn = np.std(rr_clean)
    rmssd = np.sqrt(np.mean(np.diff(rr_clean) ** 2))
    nn50 = np.sum(np.abs(np.diff(rr_clean)) > 50)
    pnn50 = nn50 / len(rr_clean) * 100
    mean_hr = 60000 / np.mean(rr_clean)

    return {"mean_hr": mean_hr, "sdnn": sdnn, "rmssd": rmssd, "pnn50": pnn50}
import numpy as np
import scipy.signal as sps


def pan_tompkins_plus(ecg, fs):
    """
    Pan-Tompkins++ R-peak Detection Algorithm
    """

    nyquist = 0.5 * fs

    # 1. Expanded Bandpass Filter (5-18 Hz)
    b, a = sps.butter(
        2,
        [5 / nyquist, 18 / nyquist],
        btype="band"
    )

    filtered = sps.filtfilt(b, a, ecg)

    # 2. Derivative (Slope Estimation)
    derivative = np.diff(
        filtered,
        prepend=filtered[0]
    )

    # 3. Squaring (Nonlinear Amplification)
    squared = derivative ** 2

    # 4. Flattop Window Moving Average Smoothing (60 ms window)
    flattop_len = max(1, int(0.06 * fs))

    flattop_win = sps.windows.flattop(flattop_len)

    # Normalize weights
    flattop_win = flattop_win / np.sum(flattop_win)

    smoothed = np.convolve(
        squared,
        flattop_win,
        mode="same"
    )

    # 5. Moving Window Integration (150 ms MWI)
    mwi_len = max(1, int(0.15 * fs))

    integrated = np.convolve(
        smoothed,
        np.ones(mwi_len) / mwi_len,
        mode="same"
    )

    # 6. Candidate Peaks with 231 ms Refractory Period
    #    (Maximum ~260 bpm)
    refractory_samples = max(
        1,
        int(0.231 * fs)
    )

    candidate_peaks, _ = sps.find_peaks(
        integrated,
        distance=refractory_samples
    )

    if len(candidate_peaks) == 0:
        return (
            np.array([]),
            filtered,
            derivative,
            squared,
            smoothed,
            integrated
        )

    # 7. Threshold Initialization (2-second learning phase)
    init_samples = min(
        len(integrated),
        int(2.0 * fs)
    )

    init_segment = integrated[:init_samples]

    if len(init_segment) > 0:
        maxf = np.max(init_segment)
        meanf = np.mean(init_segment)
    else:
        maxf = np.max(integrated)
        meanf = np.mean(integrated)

    threshold1 = maxf / 3.0
    threshold2 = 0.5 * meanf

    spk = threshold1
    npk = threshold2

    peaks = []

    # Stores 70 ms slopes of detected QRS complexes
    qrs_slopes = []

    rr_history = []

    last_peak_idx = 0

    slope_window_samples = max(
        1,
        int(0.07 * fs)
    )

    # Helper function to compute 70 ms mean slope
    def calc_70ms_slope(signal, peak_idx):
        start_idx = max(
            0,
            peak_idx - slope_window_samples
        )

        segment = signal[start_idx:peak_idx + 1]

        if len(segment) >= 2:
            return np.mean(np.diff(segment))

        return 0.0

    # 8. Decision Making Loop
    for i, idx in enumerate(candidate_peaks):

        peak_val = integrated[idx]

        current_rr = (
            idx - last_peak_idx
            if last_peak_idx != 0
            else None
        )

        # Rule 4:
        # T-Wave & Early Noise Discrimination
        # RR < 360 ms OR RR < 0.5 * mean RR
        is_t_wave = False

        if current_rr is not None and len(rr_history) >= 8:

            avg_rr = np.mean(
                rr_history[-8:]
            )

            if (
                current_rr < int(0.36 * fs)
                or current_rr < (0.5 * avg_rr)
            ):

                curr_slope = calc_70ms_slope(
                    integrated,
                    idx
                )

                prev_slope = (
                    qrs_slopes[-1]
                    if len(qrs_slopes) > 0
                    else 0.0
                )

                if (
                    prev_slope > 0
                    and curr_slope < 0.6 * prev_slope
                ):
                    is_t_wave = True

        if is_t_wave:

            # Classified as T-wave
            # Update NPK using Rule-1
            npk = (
                0.125 * peak_val
                + 0.875 * npk
            )

        elif peak_val > threshold1:

            # Valid QRS Peak
            # Update SPK using Rule-1
            spk = (
                0.125 * peak_val
                + 0.875 * spk
            )

            peaks.append(idx)

            qrs_slopes.append(
                calc_70ms_slope(
                    integrated,
                    idx
                )
            )

            if current_rr is not None:

                rr_history.append(current_rr)

                if len(rr_history) > 8:
                    rr_history.pop(0)

            last_peak_idx = idx

        else:

            # Search-back evaluation for missed beats
            recovered = False

            if len(rr_history) > 0:
                avg_rr = np.mean(
                    rr_history[-8:]
                )
            else:
                avg_rr = 1.0 * fs

            # Rule 5:
            # Search-Back with Threshold3 & MEANSB
            # Gap > 1.66 * avg_rr OR gap > 1.0 s
            if (
                current_rr is not None
                and (
                    current_rr > 1.66 * avg_rr
                    or current_rr > 1.0 * fs
                )
            ):

                preceding_qrs = (
                    [integrated[p] for p in peaks[-3:]]
                    if len(peaks) > 0
                    else [spk]
                )

                following_cands = [
                    integrated[candidate_peaks[j]]
                    for j in range(
                        i,
                        min(
                            len(candidate_peaks),
                            i + 3
                        )
                    )
                ]

                if preceding_qrs or following_cands:
                    meansb = np.mean(
                        preceding_qrs + following_cands
                    )
                else:
                    meansb = spk

                threshold3 = (
                    0.5 * threshold2
                    + 0.5 * meansb
                )

                if peak_val > threshold3:

                    # Beat recovered via Threshold3
                    # Update using Rule-2 (0.75 weight)
                    spk = (
                        0.75 * peak_val
                        + 0.25 * spk
                    )

                    peaks.append(idx)

                    qrs_slopes.append(
                        calc_70ms_slope(
                            integrated,
                            idx
                        )
                    )

                    rr_history.append(current_rr)

                    if len(rr_history) > 8:
                        rr_history.pop(0)

                    last_peak_idx = idx
                    recovered = True

            # Rule 6:
            # Emergency Reset Lockout
            # Gap > 1.4 s
            if (
                not recovered
                and current_rr is not None
                and current_rr > 1.4 * fs
            ):

                emergency_thresh = 0.2 * threshold2

                if peak_val > emergency_thresh:

                    # Beat recovered via Emergency Floor
                    # Update using Rule-2 (0.75 weight)
                    spk = (
                        0.75 * peak_val
                        + 0.25 * spk
                    )

                    peaks.append(idx)

                    qrs_slopes.append(
                        calc_70ms_slope(
                            integrated,
                            idx
                        )
                    )

                    rr_history.append(current_rr)

                    if len(rr_history) > 8:
                        rr_history.pop(0)

                    last_peak_idx = idx
                    recovered = True

            if not recovered:

                # Confirmed Noise Peak
                # Update NPK using Rule-1
                npk = (
                    0.125 * peak_val
                    + 0.875 * npk
                )

        # Threshold recalibration for next iteration
        threshold1 = (
            npk
            + 0.25 * (spk - npk)
        )

        threshold2 = 0.4 * threshold1

    return (
        np.array(peaks)
    )
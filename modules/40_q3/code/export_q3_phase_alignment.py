"""Peak/valley position alignment diagnostic for the frozen Q3 Airy fits.

This script does not refit any model parameter. It reads the frozen fit CSV files,
lightly smooths the observed and Airy curves, detects extrema of the same type,
and reports wavenumber-position discrepancies. The diagnostic is intended to
separate fringe-position agreement from amplitude-fit metrics such as R^2.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

PROJECT = Path(__file__).resolve().parents[3]
MODULE = PROJECT / "modules" / "40_q3"


def odd_window_from_span(x: np.ndarray, span_cm: float = 15.0) -> int:
    step = float(np.median(np.diff(x)))
    points = max(5, int(round(span_cm / step)))
    if points % 2 == 0:
        points += 1
    return min(points, len(x) - (1 - len(x) % 2))


def extrema(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return smoothed peak and valley wavenumbers using an adaptive prominence."""
    window = odd_window_from_span(x)
    smooth = savgol_filter(y, window_length=window, polyorder=min(3, window - 2))
    scale = float(np.percentile(smooth, 95) - np.percentile(smooth, 5))
    prominence = max(0.02 * scale, 1.0e-6)
    # A 50 cm^-1 minimum spacing only suppresses residual high-frequency noise;
    # the physical fringe spacing is substantially larger for the present sample.
    min_distance = max(1, int(round(50.0 / float(np.median(np.diff(x))))))
    peak_idx, _ = find_peaks(smooth, prominence=prominence, distance=min_distance)
    valley_idx, _ = find_peaks(-smooth, prominence=prominence, distance=min_distance)
    return x[peak_idx], x[valley_idx]


def match_same_type(observed: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    """Greedily match monotone extrema of the same type within half a fringe period."""
    if len(observed) == 0 or len(predicted) == 0:
        return np.array([], dtype=float)
    if len(predicted) > 1:
        tolerance = 0.5 * float(np.median(np.diff(predicted)))
    else:
        tolerance = np.inf
    used: set[int] = set()
    differences: list[float] = []
    for value in observed:
        candidates = [(abs(value - p), j) for j, p in enumerate(predicted) if j not in used]
        if not candidates:
            break
        error, index = min(candidates)
        if error <= tolerance:
            used.add(index)
            differences.append(float(error))
    return np.asarray(differences, dtype=float)


def analyse(path: Path) -> dict[str, float | int | str]:
    frame = pd.read_csv(path)
    x = frame["wavenumber_cm-1"].to_numpy(float)
    observed = frame["observed_reflectance_fraction"].to_numpy(float)
    predicted = frame["airy_reflectance_fraction"].to_numpy(float)

    obs_peaks, obs_valleys = extrema(x, observed)
    fit_peaks, fit_valleys = extrema(x, predicted)
    peak_errors = match_same_type(obs_peaks, fit_peaks)
    valley_errors = match_same_type(obs_valleys, fit_valleys)
    errors = np.concatenate([peak_errors, valley_errors])

    return {
        "source": str(path.relative_to(PROJECT)).replace("\\", "/"),
        "observed_peak_count": int(len(obs_peaks)),
        "observed_valley_count": int(len(obs_valleys)),
        "matched_peak_count": int(len(peak_errors)),
        "matched_valley_count": int(len(valley_errors)),
        "extremum_position_mae_cm-1": float(np.mean(errors)) if len(errors) else float("nan"),
        "extremum_position_max_abs_cm-1": float(np.max(errors)) if len(errors) else float("nan"),
    }


def main() -> None:
    rows = []
    for angle in (10, 15):
        result = analyse(MODULE / "tables" / f"q3_si_{angle}deg_paper_a.csv")
        result["angle_deg"] = angle
        rows.append(result)

    table = pd.DataFrame(rows)
    csv_path = MODULE / "tables" / "q3_phase_alignment.csv"
    json_path = MODULE / "tables" / "q3_phase_alignment.json"
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()

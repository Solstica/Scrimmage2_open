"""Official 2025B spectral data loader and deterministic preprocessing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


@dataclass(frozen=True)
class Spectrum:
    wavenumber_cm: np.ndarray
    reflectance: np.ndarray
    angle_deg: float
    source: str


def load_spectrum(path: Path, angle_deg: float) -> Spectrum:
    frame = pd.read_excel(path, sheet_name=0, usecols=[0, 1], engine="openpyxl")
    frame.columns = ["wavenumber_cm", "reflectance_percent"]
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    values = frame.to_numpy(dtype=float)
    finite = np.isfinite(values).all(axis=1)
    values = values[finite]
    if values.shape[0] < 10 or np.any(np.diff(values[:, 0]) <= 0):
        raise ValueError(f"Invalid spectrum grid: {path}")
    # The first row is zero in all four attachments while its neighbours are not;
    # it is retained in the raw audit but excluded from inverse calculations.
    usable = ~((values[:, 1] == 0.0) & (values[:, 0] < 400.0))
    values = values[usable]
    return Spectrum(values[:, 0], values[:, 1] / 100.0, angle_deg, path.name)


def select_band(
    spectrum: Spectrum,
    band: tuple[float, float],
    *,
    smooth_window: int = 31,
    step: int = 1,
) -> Spectrum:
    mask = (spectrum.wavenumber_cm >= band[0]) & (spectrum.wavenumber_cm <= band[1])
    x = spectrum.wavenumber_cm[mask]
    y = spectrum.reflectance[mask]
    if x.size < 11:
        raise ValueError(f"Too few samples in band {band}")
    window = min(smooth_window, x.size if x.size % 2 else x.size - 1)
    window = max(5, window if window % 2 else window - 1)
    y_smooth = savgol_filter(y, window_length=window, polyorder=3)
    index = np.arange(0, x.size, step, dtype=int)
    return Spectrum(x[index], y_smooth[index], spectrum.angle_deg, spectrum.source)


def load_official_bundle(data_dir: Path) -> dict[str, tuple[Spectrum, Spectrum]]:
    return {
        "sic": (
            load_spectrum(data_dir / "附件1.xlsx", 10.0),
            load_spectrum(data_dir / "附件2.xlsx", 15.0),
        ),
        "si": (
            load_spectrum(data_dir / "附件3.xlsx", 10.0),
            load_spectrum(data_dir / "附件4.xlsx", 15.0),
        ),
    }

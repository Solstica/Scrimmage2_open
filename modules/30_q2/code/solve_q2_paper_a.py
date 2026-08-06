"""Reproduce PAPER_A Q2 with two independent angle fits and arithmetic averaging."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

AIR_INDEX = 1.0003
M0 = 9.1093837015e-31
MSTAR = 0.28 * M0
E_CHARGE = 1.602176634e-19
EPS0 = 8.8541878128e-12
C0 = 299792458.0
FIT_RANGE = (2500.0, 3300.0)
FILES = (("10deg", "附件1.xlsx", 10.0), ("15deg", "附件2.xlsx", 15.0))

SELL_REF = np.array([1.0, 0.20075, 5.54861, 35.65066, -12.07224, 0.02641, 1268.24708])
SELL_LOWER = np.minimum(SELL_REF * 0.95, SELL_REF * 1.05)
SELL_UPPER = np.maximum(SELL_REF * 0.95, SELL_REF * 1.05)
STAGE1_LOWER = np.array([6.5, 14.0, 2.20])
STAGE1_UPPER = np.array([8.5, 20.5, 3.20])
FULL_LOWER = np.r_[STAGE1_LOWER, SELL_LOWER]
FULL_UPPER = np.r_[STAGE1_UPPER, SELL_UPPER]
PARAMETER_NAMES = (
    "thickness_um", "log10_carrier_cm3", "substrate_index", "sellmeier_A",
    "sellmeier_B1", "sellmeier_B2", "sellmeier_B3", "sellmeier_C1_um2",
    "sellmeier_C2_um2", "sellmeier_C3_um2",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_spectrum(path: Path, angle: float) -> dict[str, object]:
    frame = pd.read_excel(path, sheet_name=0, usecols=[0, 1], engine="openpyxl")
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    values = frame.to_numpy(float)
    values = values[np.isfinite(values).all(axis=1) & (values[:, 0] > 0)]
    values = values[np.argsort(values[:, 0])]
    mask = (values[:, 0] >= FIT_RANGE[0]) & (values[:, 0] <= FIT_RANGE[1])
    return {
        "wavenumber": values[mask, 0],
        "reflectance": values[mask, 1] / 100.0,
        "angle_deg": angle,
        "source": str(path.resolve()),
        "source_sha256": sha256(path),
    }


def sellmeier_epsilon(wavenumber: np.ndarray, sell: np.ndarray) -> np.ndarray:
    wavelength2 = (1.0e4 / wavenumber) ** 2
    return sell[0] + np.sum(
        sell[1:4, None] * wavelength2[None, :] /
        (wavelength2[None, :] - sell[4:7, None]), axis=0,
    )


def film_index(wavenumber: np.ndarray, log_density: float, sell: np.ndarray) -> np.ndarray:
    wavelength_m = 1.0e-2 / wavenumber
    density_m3 = 10.0 ** log_density * 1.0e6
    correction = density_m3 * E_CHARGE**2 * wavelength_m**2 / (
        4.0 * np.pi**2 * C0**2 * EPS0 * MSTAR
    )
    return np.sqrt(np.maximum(sellmeier_epsilon(wavenumber, sell) - correction, 1.0e-12))


def fresnel(n_i, n_j, theta_i, theta_j, polarization: str):
    ci, cj = np.cos(theta_i), np.cos(theta_j)
    if polarization == "s":
        denominator = n_i * ci + n_j * cj
        return (n_i * ci - n_j * cj) / denominator, 2.0 * n_i * ci / denominator
    denominator = n_j * ci + n_i * cj
    return (n_j * ci - n_i * cj) / denominator, 2.0 * n_i * ci / denominator


def reflectance(wavenumber: np.ndarray, angle_deg: float, parameters: np.ndarray) -> np.ndarray:
    thickness, log_density, substrate_index = parameters[:3]
    n2 = film_index(wavenumber, log_density, parameters[3:])
    theta1 = np.deg2rad(angle_deg)
    theta2 = np.arcsin(np.clip(AIR_INDEX * np.sin(theta1) / n2, -1.0, 1.0))
    theta3 = np.arcsin(np.clip(AIR_INDEX * np.sin(theta1) / substrate_index, -1.0, 1.0))
    phase = 4.0 * np.pi * 1.0e-4 * wavenumber * thickness * n2 * np.cos(theta2)
    intensities = []
    for polarization in ("s", "p"):
        r12, t12 = fresnel(AIR_INDEX, n2, theta1, theta2, polarization)
        r23, _ = fresnel(n2, substrate_index, theta2, theta3, polarization)
        _, t21 = fresnel(n2, AIR_INDEX, theta2, theta1, polarization)
        field = r12 + t12 * r23 * t21 * np.exp(-1j * phase)
        intensities.append(np.abs(field) ** 2)
    return 0.5 * (intensities[0] + intensities[1])


def residual_full(parameters: np.ndarray, spectrum: dict[str, object]) -> np.ndarray:
    return np.asarray(spectrum["reflectance"]) - reflectance(
        np.asarray(spectrum["wavenumber"]), float(spectrum["angle_deg"]), parameters
    )


def fit_one_angle(spectrum: dict[str, object]) -> tuple[np.ndarray, list[dict[str, object]]]:
    stage1 = []
    for d0, log_n0, n30 in product(np.linspace(6.6, 8.4, 10), (15.5, 18.0, 20.0), (2.35, 2.75, 3.10)):
        fit = least_squares(
            lambda p: residual_full(np.r_[p, SELL_REF], spectrum),
            np.array([d0, log_n0, n30]), bounds=(STAGE1_LOWER, STAGE1_UPPER),
            x_scale="jac", max_nfev=2500, ftol=1e-11, xtol=1e-11, gtol=1e-11,
        )
        stage1.append((float(np.sqrt(np.mean(fit.fun**2))), fit.x))
    candidates, seen = [], set()
    for _, parameters in sorted(stage1, key=lambda row: row[0]):
        key = (round(float(parameters[0]), 3), round(float(parameters[1]), 2))
        if key not in seen:
            candidates.append(parameters)
            seen.add(key)
        if len(candidates) == 8:
            break
    refined = []
    for parameters in candidates:
        fit = least_squares(
            residual_full, np.r_[parameters, SELL_REF], args=(spectrum,),
            bounds=(FULL_LOWER, FULL_UPPER), x_scale="jac", max_nfev=5000,
            ftol=1e-12, xtol=1e-12, gtol=1e-12,
        )
        refined.append({
            "parameters": fit.x, "rmse": float(np.sqrt(np.mean(fit.fun**2))),
            "success": bool(fit.success), "nfev": int(fit.nfev),
        })
    refined.sort(key=lambda row: float(row["rmse"]))
    return np.asarray(refined[0]["parameters"]), refined


def metrics(observed: np.ndarray, fitted: np.ndarray) -> dict[str, float]:
    error = observed - fitted
    sse = float(np.sum(error**2))
    sst = float(np.sum((observed - np.mean(observed)) ** 2))
    return {
        "rmse_fraction": float(np.sqrt(np.mean(error**2))),
        "mae_fraction": float(np.mean(np.abs(error))),
        "r2": float(1.0 - sse / sst),
    }


def boundary_hits(parameters: np.ndarray) -> list[str]:
    tolerance = np.maximum(1.0e-3 * (FULL_UPPER - FULL_LOWER), 1.0e-8)
    hits = []
    for name, value, lower, upper, tol in zip(
        PARAMETER_NAMES, parameters, FULL_LOWER, FULL_UPPER, tolerance
    ):
        if value - lower <= tol:
            hits.append(f"{name}:lower")
        elif upper - value <= tol:
            hits.append(f"{name}:upper")
    return hits


def save_angle_assets(module: Path, label: str, spectrum: dict[str, object], parameters: np.ndarray) -> dict[str, object]:
    x = np.asarray(spectrum["wavenumber"])
    y = np.asarray(spectrum["reflectance"])
    fitted = reflectance(x, float(spectrum["angle_deg"]), parameters)
    residual = y - fitted
    table = pd.DataFrame({
        "wavenumber_cm-1": x, "observed_reflectance_fraction": y,
        "fitted_reflectance_fraction": fitted, "residual_fraction": residual,
    })
    table_path = module / "tables" / f"q2_{label}_paper_a_fit.csv"
    table.to_csv(table_path, index=False, encoding="utf-8-sig")
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.0), sharex=True, height_ratios=(3, 1))
    axes[0].plot(x, y, lw=1.1, label="Observed")
    axes[0].plot(x, fitted, lw=1.2, label="PAPER_A fit")
    axes[0].set_ylabel("Reflectance")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(x, residual, lw=0.9, color="#b44")
    axes[1].axhline(0.0, color="black", lw=0.7)
    axes[1].set(xlabel=r"Wavenumber (cm$^{-1}$)", ylabel="Residual")
    axes[1].grid(alpha=0.25)
    fig.tight_layout()
    figure_path = module / "figures" / f"q2_{label}_paper_a_fit.png"
    fig.savefig(figure_path, dpi=240)
    plt.close(fig)
    return {
        "angle_deg": float(spectrum["angle_deg"]),
        "thickness_um": float(parameters[0]),
        "log10_carrier_cm3": float(parameters[1]),
        "carrier_density_cm3": float(10.0 ** parameters[1]),
        "substrate_index": float(parameters[2]),
        "sellmeier_parameters": {name: float(value) for name, value in zip(PARAMETER_NAMES[3:], parameters[3:])},
        "metrics": metrics(y, fitted),
        "boundary_hits": boundary_hits(parameters),
        "fit_table": str(table_path.relative_to(module.parents[1])).replace("\\", "/"),
        "figure": str(figure_path.relative_to(module.parents[1])).replace("\\", "/"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    project = args.project.resolve()
    module = project / "modules" / "30_q2"
    (module / "figures").mkdir(parents=True, exist_ok=True)
    (module / "tables").mkdir(parents=True, exist_ok=True)
    (project / "output" / "results").mkdir(parents=True, exist_ok=True)

    spectra = [read_spectrum(args.data_dir / filename, angle) for _, filename, angle in FILES]
    fits = [fit_one_angle(spectrum) for spectrum in spectra]
    angle_results = [
        save_angle_assets(module, label, spectrum, parameters)
        for (label, _, _), spectrum, (parameters, _) in zip(FILES, spectra, fits)
    ]
    thicknesses = [row["thickness_um"] for row in angle_results]
    pd.DataFrame([
        {
            "angle_deg": row["angle_deg"], "thickness_um": row["thickness_um"],
            "rmse_fraction": row["metrics"]["rmse_fraction"],
            "r2": row["metrics"]["r2"], "boundary_hit_count": len(row["boundary_hits"]),
        }
        for row in angle_results
    ]).to_csv(module / "tables" / "q2_paper_a_summary.csv", index=False, encoding="utf-8-sig")
    payload = {
        "schema_version": "run_02.q2.paper_a.v1",
        "status": "FROZEN_CANDIDATE",
        "method_source": "PAPER_A",
        "fit_band_cm-1": list(FIT_RANGE),
        "fixed_effective_mass_ratio": 0.28,
        "angle_results": angle_results,
        "primary_result": {
            "rule": "arithmetic_mean_of_independent_10deg_and_15deg_fits",
            "thickness_um": float(np.mean(thicknesses)),
            "angle_difference_um": float(abs(thicknesses[0] - thicknesses[1])),
            "half_range_um": float(abs(thicknesses[0] - thicknesses[1]) / 2.0),
        },
        "disclosures": [
            "The two angles are fitted independently; no shared-parameter joint fit enters the primary result.",
            "Several nuisance Sellmeier parameters can reach their +/-5% bounds; boundary hits are reported per angle.",
            "Reflectance is converted from percent to fraction before fitting.",
        ],
        "inputs": [{"path": row["source"], "sha256": row["source_sha256"]} for row in spectra],
    }
    output = project / "output" / "results" / "q2_paper_a_results.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["primary_result"], ensure_ascii=False))


if __name__ == "__main__":
    main()

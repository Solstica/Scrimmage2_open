"""PAPER_A Q3: fixed Si oscillator--Drude constants and Airy inversion."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

PROJECT = Path(__file__).resolve().parents[3]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from shared.code.data_io import Spectrum, load_official_bundle

N_AIR = 1.0
C0 = 299_792_458.0
EPS0 = 8.854_187_812_8e-12
E_CHARGE = 1.602_176_634e-19
M_E = 9.109_383_701_5e-31
MSTAR_RATIO = 0.26
SI_BAND = (1500.0, 3500.0)
SIC_BAND = (2500.0, 3300.0)
THRESHOLD_PERCENT = 0.1
PAPER_A_TARGET = {"10deg_um": 3.143, "15deg_um": 2.937, "average_um": 3.040}

EPS_INF = 11.68
OSCILLATORS = (
    (0.29972, 10.6683, 0.092613),
    (11.34965, 16.2026, 0.23572),
)
PARAMETER_NAMES = ("thickness_um", "substrate_index", "log10_carrier_cm3", "log10_collision_s-1")
LOWER = np.array([0.1, 2.0, 12.0, 11.0])
UPPER = np.array([100.0, 5.0, 20.0, 15.0])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def band_only(spectrum: Spectrum, band: tuple[float, float]) -> Spectrum:
    mask = (spectrum.wavenumber_cm >= band[0]) & (spectrum.wavenumber_cm <= band[1])
    return Spectrum(
        spectrum.wavenumber_cm[mask], spectrum.reflectance[mask],
        spectrum.angle_deg, spectrum.source,
    )


def silicon_index(wavenumber_cm: np.ndarray, log_density_cm3: float, log_collision_s: float) -> np.ndarray:
    """PAPER_A double-oscillator--Drude index under exp(-ikz)."""
    wavelength_um = 1.0e4 / np.asarray(wavenumber_cm, dtype=float)
    epsilon = np.full(wavelength_um.shape, EPS_INF, dtype=complex)
    for strength, resonance_um, damping_um in OSCILLATORS:
        epsilon += strength * wavelength_um**2 / (
            wavelength_um**2 - resonance_um**2 + 1j * damping_um * wavelength_um
        )
    omega = 2.0 * np.pi * C0 / (wavelength_um * 1.0e-6)
    density_m3 = 10.0 ** float(log_density_cm3) * 1.0e6
    collision_s = 10.0 ** float(log_collision_s)
    plasma2 = density_m3 * E_CHARGE**2 / (EPS0 * MSTAR_RATIO * M_E)
    epsilon -= plasma2 / (omega**2 - 1j * collision_s * omega)
    root = np.sqrt(epsilon + 0j)
    root = np.where(np.real(root) < 0.0, -root, root)
    return np.where(np.imag(root) > 0.0, np.conjugate(root), root)


def fresnel(n_i, n_j, theta_i, theta_j, polarization: str):
    ci, cj = np.cos(theta_i), np.cos(theta_j)
    if polarization == "s":
        denominator = n_i * ci + n_j * cj
        return (n_i * ci - n_j * cj) / denominator, 2.0 * n_i * ci / denominator
    denominator = n_j * ci + n_i * cj
    return (n_j * ci - n_i * cj) / denominator, 2.0 * n_i * ci / denominator


def components(
    wavenumber_cm: np.ndarray, angle_deg: float, thickness_um: float,
    film_index: np.ndarray, substrate_index: np.ndarray | float,
) -> dict[str, dict[str, np.ndarray]]:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    n2 = np.asarray(film_index, dtype=complex)
    n3 = np.broadcast_to(np.asarray(substrate_index, dtype=complex), sigma.shape)
    theta1 = np.deg2rad(angle_deg)
    theta2 = np.arcsin(np.clip(N_AIR * np.sin(theta1) / np.maximum(np.real(n2), 1.0e-12), -1.0, 1.0))
    theta3 = np.arcsin(np.clip(N_AIR * np.sin(theta1) / np.maximum(np.real(n3), 1.0e-12), -1.0, 1.0))
    propagation = np.exp(-1j * 4.0 * np.pi * 1.0e-4 * sigma * thickness_um * n2 * np.cos(theta2))
    if np.any(np.abs(propagation) <= 0.0) or np.any(np.abs(propagation) > 1.0 + 1.0e-12):
        raise FloatingPointError("Propagation gate failed: exp(-ikz) must satisfy 0 < |P| <= 1")
    result: dict[str, dict[str, np.ndarray]] = {}
    for polarization in ("s", "p"):
        r12, t12 = fresnel(N_AIR, n2, theta1, theta2, polarization)
        r23, _ = fresnel(n2, n3, theta2, theta3, polarization)
        r21, t21 = fresnel(n2, N_AIR, theta2, theta1, polarization)
        first = t12 * r23 * t21 * propagation
        loop = r21 * r23 * propagation
        result[polarization] = {
            "surface": r12, "first_internal": first, "loop": loop,
            "propagation": propagation,
        }
    return result


def reflectance(parts: dict[str, dict[str, np.ndarray]], model: str = "airy") -> np.ndarray:
    intensities = []
    for polarization in ("s", "p"):
        block = parts[polarization]
        if model == "airy":
            field = block["surface"] + block["first_internal"] / (1.0 - block["loop"])
        elif model == "double":
            field = block["surface"] + block["first_internal"]
        else:
            raise ValueError(model)
        intensities.append(np.abs(field) ** 2)
    return 0.5 * (intensities[0] + intensities[1])


def third_beam_ratio(parts: dict[str, dict[str, np.ndarray]]) -> np.ndarray:
    third = sum(np.abs(parts[p]["first_internal"] * parts[p]["loop"]) ** 2 for p in ("s", "p"))
    surface = sum(np.abs(parts[p]["surface"]) ** 2 for p in ("s", "p"))
    return third / np.maximum(surface, 1.0e-30)


def si_prediction(spectrum: Spectrum, parameters: np.ndarray, model: str = "airy") -> np.ndarray:
    d_um, n3, log_n, log_gamma = map(float, parameters)
    n2 = silicon_index(spectrum.wavenumber_cm, log_n, log_gamma)
    return reflectance(components(spectrum.wavenumber_cm, spectrum.angle_deg, d_um, n2, n3), model)


def metric_block(observed: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    residual = observed - predicted
    sse = float(np.sum(residual**2))
    sst = float(np.sum((observed - np.mean(observed)) ** 2))
    return {
        "rmse_fraction": float(np.sqrt(np.mean(residual**2))),
        "rmse_percentage_point": float(100.0 * np.sqrt(np.mean(residual**2))),
        "mae_percentage_point": float(100.0 * np.mean(np.abs(residual))),
        "r2": float(1.0 - sse / max(sst, 1.0e-30)),
    }


def fit_si(spectrum: Spectrum) -> dict[str, object]:
    # Starts concentrate around the fringe-count estimate used by PAPER_A but
    # retain the paper's broad physical bounds, including d in 0.1--100 um.
    starts = [
        [2.70, 3.0, 14.0, 12.0], [2.90, 3.5, 16.0, math.log10(5e13)],
        [3.05, 4.0, 18.0, 13.0], [3.20, 3.5, 16.0, 14.0],
        [3.40, 3.0, 18.0, 14.5], [3.60, 4.5, 20.0, 15.0],
    ]

    def residual(parameters: np.ndarray) -> np.ndarray:
        return si_prediction(spectrum, parameters, "airy") - spectrum.reflectance

    solutions = []
    for seed_id, start in enumerate(starts, start=1):
        answer = least_squares(
            residual, np.asarray(start), bounds=(LOWER, UPPER), method="trf",
            x_scale="jac", max_nfev=5000, ftol=1e-11, xtol=1e-11, gtol=1e-11,
        )
        solutions.append({"seed_id": seed_id, "initial": np.asarray(start), "answer": answer})
    solutions.sort(key=lambda row: float(np.mean(row["answer"].fun**2)))
    best = solutions[0]["answer"]
    predicted = si_prediction(spectrum, best.x, "airy")
    span = UPPER - LOWER
    proximity = np.minimum((best.x - LOWER) / span, (UPPER - best.x) / span)
    singular = np.linalg.svd(best.jac, compute_uv=False)

    def hits(parameters: np.ndarray) -> list[str]:
        distance = np.minimum((parameters - LOWER) / span, (UPPER - parameters) / span)
        return [name for name, value in zip(PARAMETER_NAMES, distance) if value < 1.0e-3]

    return {
        "parameters": dict(zip(PARAMETER_NAMES, map(float, best.x))),
        "metrics": metric_block(spectrum.reflectance, predicted),
        "success": bool(best.success),
        "boundary_hits": [name for name, value in zip(PARAMETER_NAMES, proximity) if value < 1.0e-3],
        "jacobian_condition_number": float(singular[0] / max(singular[-1], 1.0e-30)),
        "jacobian_sigma_min": float(singular[-1]),
        "multistart": [
            {
                "seed_id": int(row["seed_id"]),
                "initial": dict(zip(PARAMETER_NAMES, map(float, row["initial"]))),
                "parameters": dict(zip(PARAMETER_NAMES, map(float, row["answer"].x))),
                "rmse_percentage_point": float(100.0 * np.sqrt(np.mean(row["answer"].fun**2))),
                "success": bool(row["answer"].success),
                "boundary_hits": hits(row["answer"].x),
            }
            for row in solutions
        ],
    }


def q2_angle_index(wavenumber: np.ndarray, row: dict[str, object]) -> np.ndarray:
    sell = row["sellmeier_parameters"]
    wavelength2 = (1.0e4 / wavenumber) ** 2
    epsilon = sell["sellmeier_A"]
    for number in (1, 2, 3):
        epsilon += sell[f"sellmeier_B{number}"] * wavelength2 / (
            wavelength2 - sell[f"sellmeier_C{number}_um2"]
        )
    wavelength_m = 1.0e-2 / wavenumber
    density_m3 = row["carrier_density_cm3"] * 1.0e6
    epsilon -= density_m3 * E_CHARGE**2 * wavelength_m**2 / (
        4.0 * np.pi**2 * C0**2 * EPS0 * 0.28 * M_E
    )
    return np.sqrt(np.maximum(epsilon, 1.0e-12))


def save_si_assets(module: Path, spectrum: Spectrum, fit: dict[str, object]) -> dict[str, object]:
    parameters = np.array([fit["parameters"][name] for name in PARAMETER_NAMES])
    n2 = silicon_index(spectrum.wavenumber_cm, parameters[2], parameters[3])
    parts = components(spectrum.wavenumber_cm, spectrum.angle_deg, parameters[0], n2, parameters[1])
    airy = reflectance(parts, "airy")
    double = reflectance(parts, "double")
    ratio_percent = 100.0 * third_beam_ratio(parts)
    table = pd.DataFrame({
        "wavenumber_cm-1": spectrum.wavenumber_cm,
        "observed_reflectance_fraction": spectrum.reflectance,
        "airy_reflectance_fraction": airy,
        "double_beam_comparison_fraction": double,
        "airy_residual_fraction": spectrum.reflectance - airy,
        "third_beam_ratio_percent": ratio_percent,
    })
    label = f"{int(spectrum.angle_deg)}deg"
    table_path = module / "tables" / f"q3_si_{label}_paper_a.csv"
    table.to_csv(table_path, index=False, encoding="utf-8-sig")
    fig, axes = plt.subplots(
        2, 1, figsize=(8.0, 6.0), sharex=True,
        gridspec_kw={"height_ratios": (3, 1)},
    )
    axes[0].plot(spectrum.wavenumber_cm, spectrum.reflectance, lw=1.0, label="Observed")
    axes[0].plot(spectrum.wavenumber_cm, airy, lw=1.2, label="PAPER_A Airy")
    axes[0].set_ylabel("Reflectance")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(spectrum.wavenumber_cm, spectrum.reflectance - airy, lw=0.8, color="#b44")
    axes[1].axhline(0.0, color="black", lw=0.7)
    axes[1].set(xlabel=r"Wavenumber (cm$^{-1}$)", ylabel="Residual")
    axes[1].grid(alpha=0.25)
    fig.tight_layout()
    figure_path = module / "figures" / f"q3_si_{label}_paper_a_fit.png"
    fig.savefig(figure_path, dpi=240)
    plt.close(fig)
    fit["third_beam_ratio_max_percent"] = float(np.max(ratio_percent))
    fit["propagation_max_abs"] = float(max(np.max(np.abs(parts[p]["propagation"])) for p in ("s", "p")))
    fit["figure"] = str(figure_path.relative_to(module.parents[1])).replace("\\", "/")
    fit["table"] = str(table_path.relative_to(module.parents[1])).replace("\\", "/")
    return fit


def sic_backcheck(
    module: Path, spectra: tuple[Spectrum, Spectrum], q2: dict[str, object]
) -> dict[str, object]:
    rows, maxima = [], []
    for raw, q2_angle in zip(spectra, q2["angle_results"]):
        spectrum = band_only(raw, SIC_BAND)
        n2 = q2_angle_index(spectrum.wavenumber_cm, q2_angle)
        parts = components(
            spectrum.wavenumber_cm, spectrum.angle_deg,
            q2["primary_result"]["thickness_um"], n2, q2_angle["substrate_index"],
        )
        ratio = 100.0 * third_beam_ratio(parts)
        maxima.append(float(np.max(ratio)))
        rows.append(pd.DataFrame({
            "wavenumber_cm-1": spectrum.wavenumber_cm,
            "angle_deg": spectrum.angle_deg, "third_beam_ratio_percent": ratio,
        }))
    table = pd.concat(rows, ignore_index=True)
    table.to_csv(module / "tables" / "q3_sic_paper_a_backcheck.csv", index=False, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for angle, block in table.groupby("angle_deg"):
        ax.plot(block["wavenumber_cm-1"], block["third_beam_ratio_percent"], label=f"{angle:g} deg")
    ax.axhline(THRESHOLD_PERCENT, ls="--", color="#b44", label="0.1% threshold")
    ax.set(xlabel=r"Wavenumber (cm$^{-1}$)", ylabel="Third-beam ratio (%)")
    ax.set_yscale("log")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(module / "figures" / "q3_sic_paper_a_backcheck.png", dpi=240)
    plt.close(fig)
    return {
        "q2_thickness_um": q2["primary_result"]["thickness_um"],
        "max_ratio_percent_by_angle": maxima,
        "threshold_percent": THRESHOLD_PERCENT,
        "retain_q2_result": bool(max(maxima) < THRESHOLD_PERCENT),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--q2-results", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    module = project / "modules" / "40_q3"
    (module / "figures").mkdir(parents=True, exist_ok=True)
    (module / "tables").mkdir(parents=True, exist_ok=True)
    (project / "output" / "results").mkdir(parents=True, exist_ok=True)
    bundle = load_official_bundle(args.data_dir)
    si_spectra = tuple(band_only(row, SI_BAND) for row in bundle["si"])
    si_fits = [save_si_assets(module, spectrum, fit_si(spectrum)) for spectrum in si_spectra]
    thicknesses = [row["parameters"]["thickness_um"] for row in si_fits]
    mean_thickness = float(np.mean(thicknesses))
    distance_percent = 100.0 * abs(mean_thickness - PAPER_A_TARGET["average_um"]) / PAPER_A_TARGET["average_um"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    labels = ["10 deg", "15 deg", "Mean"]
    computed = [*thicknesses, mean_thickness]
    reference = [PAPER_A_TARGET["10deg_um"], PAPER_A_TARGET["15deg_um"], PAPER_A_TARGET["average_um"]]
    position = np.arange(3)
    ax.bar(position - 0.18, computed, width=0.36, label="Recomputed")
    ax.bar(position + 0.18, reference, width=0.36, label="PAPER_A reported", alpha=0.72)
    ax.set_xticks(position, labels)
    ax.set_ylabel("Thickness (um)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(module / "figures" / "q3_si_paper_a_thickness_comparison.png", dpi=240)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for spectrum in si_spectra:
        label = f"{int(spectrum.angle_deg)}deg"
        table = pd.read_csv(module / "tables" / f"q3_si_{label}_paper_a.csv")
        ax.plot(table["wavenumber_cm-1"], table["third_beam_ratio_percent"], label=f"{spectrum.angle_deg:g} deg")
    ax.axhline(THRESHOLD_PERCENT, ls="--", color="#b44", label="0.1% threshold")
    ax.set(xlabel=r"Wavenumber (cm$^{-1}$)", ylabel="Third-beam ratio (%)")
    ax.set_yscale("log")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(module / "figures" / "q3_si_paper_a_third_beam_ratio.png", dpi=240)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(7.6, 6.0), sharex=True)
    for spectrum in si_spectra:
        label = f"{int(spectrum.angle_deg)}deg"
        table = pd.read_csv(module / "tables" / f"q3_si_{label}_paper_a.csv")
        delta_pp = 100.0 * (
            table["airy_reflectance_fraction"] - table["double_beam_comparison_fraction"]
        )
        axes[0].plot(table["wavenumber_cm-1"], delta_pp, label=f"{spectrum.angle_deg:g} deg")
        axes[1].plot(
            table["wavenumber_cm-1"],
            100.0 * table["airy_residual_fraction"],
            label=f"{spectrum.angle_deg:g} deg",
        )
    axes[0].set_ylabel("Airy - double (p.p.)")
    axes[1].set_ylabel("Airy residual (p.p.)")
    axes[1].set_xlabel(r"Wavenumber (cm$^{-1}$)")
    for ax in axes:
        ax.axhline(0.0, color="0.35", lw=0.7)
        ax.grid(alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(module / "figures" / "q3_si_double_airy_comparison.png", dpi=240)
    plt.close(fig)
    q2 = json.loads(args.q2_results.read_text(encoding="utf-8"))
    if abs(q2["primary_result"]["thickness_um"] - 7.7398) > 5.0e-4:
        raise ValueError("Q2 dependency is not the fresh PAPER_A result")
    backcheck = sic_backcheck(module, bundle["sic"], q2)
    payload = {
        "schema_version": "run_02.q3.paper_a.v1",
        "status": "FROZEN",
        "method_source": "PAPER_A",
        "si_band_cm-1": list(SI_BAND),
        "formal_model": "Airy",
        "fixed_material_parameters": {
            "epsilon_inf": EPS_INF, "oscillators": OSCILLATORS,
            "effective_mass_ratio": MSTAR_RATIO,
        },
        "si_angle_results": si_fits,
        "si_primary_result": {
            "rule": "arithmetic_mean_of_independent_10deg_and_15deg_Airy_fits",
            "thickness_um": mean_thickness,
            "relative_distance_to_paper_a_percent": distance_percent,
            "five_percent_numerical_gate_pass": bool(distance_percent <= 5.0),
            "user_accepted_exception": True,
            "acceptance_date": "2026-08-06",
            "acceptance_reason": "固定硅背景参数，仅拟合厚度、衬底折射率、载流子浓度和碰撞率；保留诚实重算值，不以释放弱可辨识参数强贴范文数值。",
            "paper_a_reference_only": PAPER_A_TARGET,
        },
        "sic_backcheck": backcheck,
        "q2_dependency": {"path": str(args.q2_results.resolve()), "sha256": sha256(args.q2_results)},
        "inputs": [
            {"source": row.source, "path": str((args.data_dir / row.source).resolve()), "sha256": sha256(args.data_dir / row.source)}
            for row in bundle["si"]
        ],
        "disclosures": [
            "Silicon uses the Airy model as the formal PAPER_A route; the third-beam ratio is explanatory, not a model selector.",
            "Oscillator constants and effective mass are fixed; only d, n3, N and collision rate are fitted independently by angle.",
            "No angle gain, offset, finite-order Neumann expansion, AIC selector or joint-angle primary fit is used.",
            "The corrected attenuating propagation branch produces a mean thickness 5.85% above the paper's reported value; the user accepted the identifiable four-parameter recomputation as the frozen result.",
        ],
    }
    output = args.output.resolve() if args.output else project / "output" / "results" / "q3_paper_a_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["si_primary_result"], ensure_ascii=False))


if __name__ == "__main__":
    main()

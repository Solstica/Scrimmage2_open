"""Q3 conditional double-beam/Airy inversion for the 2025 CUMCM A problem.

The historical source folder is named ``prob25B`` because the A/B labels were
exchanged.  This module intentionally contains no finite-order Neumann model,
AIC selector, or empirical angle gain/bias.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

PROJECT = Path(__file__).resolve().parents[3]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from shared.code.data_io import Spectrum, load_official_bundle, select_band
from shared.code.materials import background_index, drude_substrate_permittivity, si_background_index

N_AIR = 1.0003
C0 = 299_792_458.0
EPS0 = 8.854_187_812_8e-12
E_CHARGE = 1.602_176_634e-19
M_E = 9.109_383_701_5e-31
MSTAR_SI = 0.28 * M_E
SI_BAND = (1500.0, 3500.0)
SIC_CRITERION_BAND = (2500.0, 3300.0)
THRESHOLD_PERCENT = 0.1
PARAMETER_NAMES = ("d_um", "n_substrate", "log10_N_cm-3", "log10_gamma_cm-1")
SI_BOUNDS = np.array(((2.5, 4.5), (2.8, 4.2), (14.0, 22.0), (-1.0, 5.0)), dtype=float)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _complex_index_from_eps(eps: np.ndarray) -> np.ndarray:
    """Return the positive-real, non-positive-imaginary root for exp(-ikz)."""
    root = np.sqrt(np.asarray(eps, dtype=complex) + 0j)
    root = np.where(np.real(root) < 0, -root, root)
    return np.where(np.imag(root) > 0, np.conjugate(root), root)


def si_permittivity(sigma_cm: np.ndarray, log_n: float, log_gamma: float) -> np.ndarray:
    """293 K Si background plus Drude term under the exp(-ikz) convention."""
    sigma = np.asarray(sigma_cm, dtype=float)
    density_m3 = 10.0**float(log_n) * 1.0e6
    plasma_cm = math.sqrt(density_m3 * E_CHARGE**2 / (EPS0 * MSTAR_SI)) / (2.0 * math.pi * C0 * 100.0)
    gamma_cm = 10.0**float(log_gamma)
    return si_background_index(sigma) ** 2 - plasma_cm**2 / (sigma * (sigma - 1j * gamma_cm))


def _admittance(n: np.ndarray, q: np.ndarray, polarization: str) -> np.ndarray:
    return q if polarization == "s" else n**2 / q


def _normal_component(n: np.ndarray, sin_incident: float, convention: str) -> np.ndarray:
    if convention == "complex_q":
        root = np.sqrt(n**2 - (N_AIR * sin_incident) ** 2 + 0j)
        return np.where(np.imag(root) > 0, -root, root)
    if convention != "real_angle":
        raise ValueError(f"Unknown refraction convention: {convention}")
    argument = N_AIR * sin_incident / np.maximum(np.abs(np.real(n)), 1.0e-12)
    theta = np.arcsin(np.clip(argument, -0.999_999, 0.999_999))
    return n * np.cos(theta)


def layer_components(
    sigma_cm: np.ndarray,
    angle_deg: float,
    d_um: float,
    film_n: np.ndarray,
    substrate_n: np.ndarray,
    *,
    convention: str = "real_angle",
) -> dict[str, dict[str, np.ndarray]]:
    """Surface beam, first internal beam, and one-round-trip multiplier."""
    sigma = np.asarray(sigma_cm, dtype=float)
    film_n = np.asarray(film_n, dtype=complex)
    substrate_n = np.broadcast_to(np.asarray(substrate_n, dtype=complex), film_n.shape)
    incident = math.radians(float(angle_deg))
    sin_i = math.sin(incident)
    q0 = np.full_like(film_n, N_AIR * math.cos(incident), dtype=complex)
    q1 = _normal_component(film_n, sin_i, convention)
    q2 = _normal_component(substrate_n, sin_i, convention)
    propagation = np.exp(-1j * 4.0 * math.pi * 1.0e-4 * sigma * float(d_um) * q1)
    result: dict[str, dict[str, np.ndarray]] = {}
    n0 = np.full_like(film_n, N_AIR, dtype=complex)
    for pol in ("s", "p"):
        y0 = _admittance(n0, q0, pol)
        y1 = _admittance(film_n, q1, pol)
        y2 = _admittance(substrate_n, q2, pol)
        r01 = (y0 - y1) / (y0 + y1)
        r10 = -r01
        r12 = (y1 - y2) / (y1 + y2)
        t01 = 2.0 * y0 / (y0 + y1)
        t10 = 2.0 * y1 / (y1 + y0)
        first = t01 * r12 * t10 * propagation
        loop = r10 * r12 * propagation
        result[pol] = {"surface": r01, "first": first, "loop": loop}
    return result


def reflectance_from_components(parts: dict[str, dict[str, np.ndarray]], model: str) -> np.ndarray:
    values = []
    for pol in ("s", "p"):
        block = parts[pol]
        if model == "double":
            amplitude = block["surface"] + block["first"]
        elif model == "airy":
            amplitude = block["surface"] + block["first"] / (1.0 - block["loop"])
        else:
            raise ValueError(f"Unknown model: {model}")
        values.append(np.abs(amplitude) ** 2)
    return 0.5 * (values[0] + values[1])


def third_beam_ratio(parts: dict[str, dict[str, np.ndarray]]) -> np.ndarray:
    surface = sum(np.abs(parts[p]["surface"]) ** 2 for p in ("s", "p"))
    third = sum(np.abs(parts[p]["first"] * parts[p]["loop"]) ** 2 for p in ("s", "p"))
    return third / np.maximum(surface, 1.0e-30)


def si_components(spectrum: Spectrum, parameters: np.ndarray, convention: str = "real_angle") -> dict[str, dict[str, np.ndarray]]:
    d_um, n_sub, log_n, log_gamma = map(float, parameters)
    film_n = _complex_index_from_eps(si_permittivity(spectrum.wavenumber_cm, log_n, log_gamma))
    substrate_n = np.full_like(film_n, n_sub, dtype=complex)
    return layer_components(spectrum.wavenumber_cm, spectrum.angle_deg, d_um, film_n, substrate_n, convention=convention)


def si_reflectance(spectrum: Spectrum, parameters: np.ndarray, model: str, convention: str = "real_angle") -> np.ndarray:
    return reflectance_from_components(si_components(spectrum, parameters, convention), model)


def metric_block(observation: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    residual = observation - prediction
    sse = float(np.sum(residual**2))
    sst = float(np.sum((observation - np.mean(observation)) ** 2))
    return {
        "rmse_fraction": float(np.sqrt(np.mean(residual**2))),
        "rmse_percentage_point": float(100.0 * np.sqrt(np.mean(residual**2))),
        "mae_percentage_point": float(100.0 * np.mean(np.abs(residual))),
        "r2": float(1.0 - sse / max(sst, 1.0e-30)),
    }


def _normalized_jacobian_diagnostics(jacobian: np.ndarray, x: np.ndarray) -> dict[str, object]:
    norms = np.linalg.norm(jacobian, axis=0)
    normalized = jacobian / np.maximum(norms, 1.0e-15)
    singular = np.linalg.svd(normalized, compute_uv=False)
    span = SI_BOUNDS[:, 1] - SI_BOUNDS[:, 0]
    proximity = np.minimum((x - SI_BOUNDS[:, 0]) / span, (SI_BOUNDS[:, 1] - x) / span)
    boundary = {name: bool(value < 1.0e-3) for name, value in zip(PARAMETER_NAMES, proximity)}
    return {
        "singular_values": singular.tolist(),
        "condition_number": float(singular[0] / max(singular[-1], 1.0e-15)),
        "column_norms": norms.tolist(),
        "boundary_flags": boundary,
        "nuisance_parameters_interpretable": bool(not boundary["log10_N_cm-3"] and not boundary["log10_gamma_cm-1"] and singular[-1] > 1.0e-3),
    }


def fit_si(spectra: tuple[Spectrum, ...], model: str, *, convention: str = "real_angle", extra_start: np.ndarray | None = None) -> dict[str, object]:
    lower, upper = SI_BOUNDS[:, 0], SI_BOUNDS[:, 1]
    starts = [
        [3.25, 3.35, 15.0, 0.0], [3.35, 3.45, 16.5, 1.0],
        [3.45, 3.55, 18.0, 2.0], [3.55, 3.65, 19.5, 3.0],
        [3.65, 3.75, 21.0, 4.0], [3.30, 3.90, 20.0, 0.5],
        [3.80, 3.10, 17.0, 4.5], [3.05, 3.60, 21.5, 2.5],
    ]
    if extra_start is not None:
        starts.insert(0, np.asarray(extra_start, dtype=float).tolist())

    def residual(p: np.ndarray) -> np.ndarray:
        return np.concatenate([si_reflectance(s, p, model, convention) - s.reflectance for s in spectra])

    solved = []
    for start in starts:
        answer = least_squares(
            residual, np.clip(np.asarray(start, dtype=float), lower, upper), bounds=(lower, upper),
            method="trf", loss="linear", x_scale="jac", max_nfev=5000,
            ftol=1.0e-11, xtol=1.0e-11, gtol=1.0e-11,
        )
        solved.append(answer)
    best = min(solved, key=lambda item: float(np.mean(item.fun**2)))
    observation = np.concatenate([s.reflectance for s in spectra])
    prediction = np.concatenate([si_reflectance(s, best.x, model, convention) for s in spectra])
    ranked = sorted(solved, key=lambda item: float(np.mean(item.fun**2)))
    diagnostics = _normalized_jacobian_diagnostics(best.jac, best.x)
    best_rmse = metric_block(observation, prediction)["rmse_percentage_point"]
    near = [r for r in ranked if 100.0 * np.sqrt(np.mean(r.fun**2)) <= best_rmse + 0.01]
    diagnostics["near_optimal_thickness_span_um"] = [float(min(r.x[0] for r in near)), float(max(r.x[0] for r in near))]
    return {
        "model": model,
        "refraction_convention": convention,
        "parameters": dict(zip(PARAMETER_NAMES, map(float, best.x))),
        "metrics": metric_block(observation, prediction),
        "success": bool(best.success),
        "diagnostics": diagnostics,
        "multistart": [
            {"d_um": float(r.x[0]), "rmse_percentage_point": float(100.0 * np.sqrt(np.mean(r.fun**2))), "success": bool(r.success)}
            for r in ranked
        ],
    }


def fit_parameter_array(fit: dict[str, object]) -> np.ndarray:
    return np.array([fit["parameters"][name] for name in PARAMETER_NAMES], dtype=float)


def q2_frozen_result(project: Path) -> tuple[dict[str, object], Path]:
    path = project / "output" / "results" / "analysis_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    q2 = data["Q2"]["main"]
    if abs(float(q2["thickness_um"]) - 7.384039253397902) > 5.0e-7:
        raise ValueError("Q2 official result does not match frozen R-Q2-D")
    return q2, path


def sic_criterion(bundle: dict[str, tuple[Spectrum, Spectrum]], q2: dict[str, object]) -> tuple[list[dict[str, object]], list[pd.DataFrame]]:
    rows: list[dict[str, object]] = []
    curves: list[pd.DataFrame] = []
    for raw in bundle["sic"]:
        spectrum = select_band(raw, SIC_CRITERION_BAND, smooth_window=31, step=1)
        sigma = spectrum.wavenumber_cm
        film_n = float(q2["index_scale"]) * background_index("sic", sigma)
        eps_sub_shared = drude_substrate_permittivity(
            "sic", sigma, float(q2["plasma_wavenumber_cm-1"]),
            float(q2["damping_wavenumber_cm-1"]), float(q2["index_scale"]),
        )
        substrate_n = _complex_index_from_eps(np.conjugate(eps_sub_shared))
        parts = layer_components(sigma, spectrum.angle_deg, float(q2["thickness_um"]), film_n, substrate_n, convention="real_angle")
        ratio = third_beam_ratio(parts)
        maximum = float(100.0 * np.max(ratio))
        rows.append({
            "material": "SiC", "angle_deg": spectrum.angle_deg,
            "band_cm-1": list(SIC_CRITERION_BAND), "third_beam_ratio_max_percent": maximum,
            "threshold_percent": THRESHOLD_PERCENT,
            "decision": "retain_q2_double_beam" if maximum < THRESHOLD_PERCENT else "refit_with_airy",
        })
        curves.append(pd.DataFrame({"wavenumber_cm-1": sigma, "angle_deg": spectrum.angle_deg, "third_beam_ratio_percent": 100.0 * ratio}))
    return rows, curves


def prediction_table(spectrum: Spectrum, double: dict[str, object], airy: dict[str, object], selected: str) -> pd.DataFrame:
    p_double = fit_parameter_array(double)
    p_airy = fit_parameter_array(airy)
    pred_double = si_reflectance(spectrum, p_double, "double")
    pred_airy = si_reflectance(spectrum, p_airy, "airy")
    return pd.DataFrame({
        "wavenumber_cm-1": spectrum.wavenumber_cm,
        "angle_deg": spectrum.angle_deg,
        "measured_reflectance_percent": 100.0 * spectrum.reflectance,
        "double_reflectance_percent": 100.0 * pred_double,
        "airy_reflectance_percent": 100.0 * pred_airy,
        "selected_model": selected,
        "selected_residual_percentage_point": 100.0 * ((pred_double if selected == "double" else pred_airy) - spectrum.reflectance),
    })


def run(data_dir: Path, project: Path) -> dict[str, object]:
    project = project.resolve()
    bundle = load_official_bundle(data_dir)
    si_spectra = tuple(select_band(s, SI_BAND, smooth_window=31, step=1) for s in bundle["si"])

    single_double = [fit_si((s,), "double") for s in si_spectra]
    criterion_rows = []
    for spectrum, fit in zip(si_spectra, single_double):
        ratio = third_beam_ratio(si_components(spectrum, fit_parameter_array(fit)))
        criterion_rows.append({
            "material": "Si", "angle_deg": spectrum.angle_deg, "band_cm-1": list(SI_BAND),
            "third_beam_ratio_max_percent": float(100.0 * np.max(ratio)),
            "threshold_percent": THRESHOLD_PERCENT,
        })
    maximum_si_ratio = max(row["third_beam_ratio_max_percent"] for row in criterion_rows)
    selected_model = "airy" if maximum_si_ratio >= THRESHOLD_PERCENT else "double"
    for row in criterion_rows:
        row["decision"] = selected_model

    single_airy = [fit_si((s,), "airy", extra_start=fit_parameter_array(d)) for s, d in zip(si_spectra, single_double)]
    selected_single = single_airy if selected_model == "airy" else single_double
    main_thickness = float(np.mean([fit["parameters"]["d_um"] for fit in selected_single]))
    angle_relative_difference = float(abs(selected_single[0]["parameters"]["d_um"] - selected_single[1]["parameters"]["d_um"]) / main_thickness)

    joint_double = fit_si(si_spectra, "double", extra_start=fit_parameter_array(single_double[0]))
    joint_airy = fit_si(si_spectra, "airy", extra_start=fit_parameter_array(single_airy[0]))
    joint_selected = joint_airy if selected_model == "airy" else joint_double
    joint_relative_difference = float(abs(joint_selected["parameters"]["d_um"] - main_thickness) / main_thickness)

    # A controlled implementation sensitivity check: refit the selected model
    # using the complex normal-wavevector convention instead of the locked
    # real-angle approximation.
    complex_angle_fits = [fit_si((s,), selected_model, convention="complex_q", extra_start=fit_parameter_array(f)) for s, f in zip(si_spectra, selected_single)]
    complex_angle_mean = float(np.mean([fit["parameters"]["d_um"] for fit in complex_angle_fits]))

    q2, q2_path = q2_frozen_result(project)
    sic_rows, sic_curves = sic_criterion(bundle, q2)
    retain_q2 = all(row["decision"] == "retain_q2_double_beam" for row in sic_rows)

    validation = {
        "threshold_sensitivity": [
            {"threshold_percent": threshold, "selected_model": "airy" if maximum_si_ratio >= threshold else "double"}
            for threshold in (0.05, 0.10, 0.20)
        ],
        "single_angle_relative_difference_percent": 100.0 * angle_relative_difference,
        "joint_vs_single_mean_relative_difference_percent": 100.0 * joint_relative_difference,
        "real_angle_vs_complex_q_thickness_difference_percent": 100.0 * abs(complex_angle_mean - main_thickness) / main_thickness,
        "nuisance_parameters_interpretable": bool(all(f["diagnostics"]["nuisance_parameters_interpretable"] for f in selected_single + [joint_selected])),
        "thickness_consistency_pass": bool(angle_relative_difference < 0.05 and joint_relative_difference < 0.05),
        "all_solvers_success": bool(all(f["success"] for f in single_double + single_airy + [joint_double, joint_airy] + complex_angle_fits)),
    }

    result: dict[str, object] = {
        "metadata": {
            "competition_problem": "CUMCM-2025-A",
            "historical_source_folder": str(data_dir),
            "si_band_cm-1": list(SI_BAND),
            "sic_criterion_band_cm-1": list(SIC_CRITERION_BAND),
            "threshold_percent": THRESHOLD_PERCENT,
            "refraction_convention": "angle from Re(n), complex n retained in Fresnel admittance and propagation",
            "model_exclusions": ["finite_order_Neumann", "AIC", "angle_gain", "angle_bias"],
        },
        "Si": {
            "criterion": criterion_rows,
            "selected_model": selected_model,
            "single_angle_double": single_double,
            "single_angle_airy": single_airy,
            "main_thickness_um": main_thickness,
            "joint_double": joint_double,
            "joint_airy": joint_airy,
            "joint_selected_thickness_um": float(joint_selected["parameters"]["d_um"]),
            "complex_q_sensitivity_mean_thickness_um": complex_angle_mean,
        },
        "SiC": {
            "q2_frozen_thickness_um": float(q2["thickness_um"]),
            "q2_source": str(q2_path.relative_to(project)),
            "q2_source_sha256": sha256(q2_path),
            "criterion": sic_rows,
            "retain_q2_result": retain_q2,
        },
        "validation": validation,
    }

    output_dir = project / "output" / "results"
    table_dir = project / "modules" / "40_q3" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "q3_analysis_results.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    pd.concat([prediction_table(s, d, a, selected_model) for s, d, a in zip(si_spectra, single_double, single_airy)], ignore_index=True).to_csv(table_dir / "q3_si_model_comparison.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(criterion_rows + sic_rows).to_csv(table_dir / "q3_third_beam_criterion.csv", index=False, encoding="utf-8-sig")
    pd.concat(sic_curves, ignore_index=True).to_csv(table_dir / "q3_sic_criterion_curve.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([
        {
            "angle_deg": s.angle_deg,
            "selected_model": selected_model,
            "d_um": f["parameters"]["d_um"],
            "rmse_percentage_point": f["metrics"]["rmse_percentage_point"],
            "r2": f["metrics"]["r2"],
            "log10_N_cm-3": f["parameters"]["log10_N_cm-3"],
            "log10_gamma_cm-1": f["parameters"]["log10_gamma_cm-1"],
            "jacobian_condition_number": f["diagnostics"]["condition_number"],
            "nuisance_parameters_interpretable": f["diagnostics"]["nuisance_parameters_interpretable"],
        }
        for s, f in zip(si_spectra, selected_single)
    ] + [{
        "angle_deg": "joint_validation", "selected_model": selected_model,
        "d_um": joint_selected["parameters"]["d_um"],
        "rmse_percentage_point": joint_selected["metrics"]["rmse_percentage_point"],
        "r2": joint_selected["metrics"]["r2"],
        "log10_N_cm-3": joint_selected["parameters"]["log10_N_cm-3"],
        "log10_gamma_cm-1": joint_selected["parameters"]["log10_gamma_cm-1"],
        "jacobian_condition_number": joint_selected["diagnostics"]["condition_number"],
        "nuisance_parameters_interpretable": joint_selected["diagnostics"]["nuisance_parameters_interpretable"],
    }]).to_csv(table_dir / "q3_si_results.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(validation["threshold_sensitivity"]).to_csv(table_dir / "q3_threshold_sensitivity.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve Q3 using the conditional third-beam criterion")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--project", default=PROJECT, type=Path)
    args = parser.parse_args()
    run(args.data_dir, args.project)


if __name__ == "__main__":
    main()

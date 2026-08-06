"""Profiled joint inverse solver and quantitative validation helpers."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import differential_evolution, least_squares, minimize_scalar
from scipy.signal import savgol_filter

from .data_io import Spectrum
from .materials import background_index, drude_substrate_permittivity
from .optics import layer_amplitudes, loop_metrics, unpolarized_reflectance


@dataclass
class JointFit:
    material: str
    order: int | float
    band: tuple[float, float]
    physical: np.ndarray
    calibration: list[np.ndarray]
    rmse: float
    mae: float
    r2: float
    residual: np.ndarray
    prediction: np.ndarray
    observation: np.ndarray
    success: bool


def physical_reflectance(material: str, spectrum: Spectrum, p: np.ndarray, order: int | float) -> np.ndarray:
    d_um, plasma, damping, scale = p
    film_n = scale * background_index(material, spectrum.wavenumber_cm)
    substrate_eps = drude_substrate_permittivity(material, spectrum.wavenumber_cm, plasma, damping, scale)
    return unpolarized_reflectance(spectrum.wavenumber_cm, spectrum.angle_deg, d_um, film_n, substrate_eps, order)


def affine_profile(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    design = np.column_stack([x, np.ones_like(x)])
    coefficient = np.linalg.lstsq(design, y, rcond=None)[0]
    prediction = design @ coefficient
    return coefficient, prediction, prediction - y


def profiled_residual(p: np.ndarray, material: str, spectra: tuple[Spectrum, Spectrum], order: int | float) -> np.ndarray:
    blocks = []
    for spectrum in spectra:
        model = physical_reflectance(material, spectrum, p, order)
        _, _, residual = affine_profile(model, spectrum.reflectance)
        blocks.append(residual)
    return np.concatenate(blocks)


def _assemble_fit(material: str, spectra: tuple[Spectrum, Spectrum], order: int | float, band: tuple[float, float], p: np.ndarray, success: bool) -> JointFit:
    calibrations, predictions, observations, residuals = [], [], [], []
    for spectrum in spectra:
        base = physical_reflectance(material, spectrum, p, order)
        coefficient, prediction, residual = affine_profile(base, spectrum.reflectance)
        calibrations.append(coefficient)
        predictions.append(prediction)
        observations.append(spectrum.reflectance)
        residuals.append(residual)
    prediction = np.concatenate(predictions)
    observation = np.concatenate(observations)
    residual = np.concatenate(residuals)
    sse = float(np.sum(residual**2))
    sst = float(np.sum((observation - np.mean(observation)) ** 2))
    return JointFit(material, order, band, p, calibrations, float(np.sqrt(np.mean(residual**2))), float(np.mean(np.abs(residual))), 1.0 - sse / sst, residual, prediction, observation, success)


def fit_joint(
    material: str,
    spectra: tuple[Spectrum, Spectrum],
    order: int | float,
    band: tuple[float, float],
    bounds: list[tuple[float, float]],
    *,
    seed: int,
    maxiter: int = 70,
) -> JointFit:
    objective = lambda p: float(np.mean(profiled_residual(p, material, spectra, order) ** 2))
    global_result = differential_evolution(objective, bounds, seed=seed, maxiter=maxiter, popsize=10, tol=1e-8, polish=False, workers=1, updating="immediate")
    lower, upper = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    local = least_squares(lambda p: profiled_residual(p, material, spectra, order), global_result.x, bounds=(lower, upper), loss="soft_l1", f_scale=0.003, xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=4000)
    return _assemble_fit(material, spectra, order, band, local.x, bool(local.success))


def refine_from(material: str, spectra: tuple[Spectrum, Spectrum], order: int | float, band: tuple[float, float], bounds: list[tuple[float, float]], initial: np.ndarray) -> JointFit:
    lower, upper = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    local = least_squares(lambda p: profiled_residual(p, material, spectra, order), np.clip(initial, lower, upper), bounds=(lower, upper), loss="soft_l1", f_scale=0.003, xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=4000)
    return _assemble_fit(material, spectra, order, band, local.x, bool(local.success))


def profile_thickness(fit: JointFit, spectra: tuple[Spectrum, Spectrum], bounds: list[tuple[float, float]], grid: np.ndarray) -> np.ndarray:
    rows = []
    nuisance_bounds = bounds[1:]
    for d in grid:
        lower = np.array([b[0] for b in nuisance_bounds])
        upper = np.array([b[1] for b in nuisance_bounds])
        initial = np.clip(fit.physical[1:], lower, upper)
        solution = least_squares(lambda q: profiled_residual(np.r_[d, q], fit.material, spectra, fit.order), initial, bounds=(lower, upper), max_nfev=1000)
        rows.append([d, float(np.sqrt(np.mean(solution.fun**2)))])
    return np.asarray(rows)


def normalized_jacobian_svd(fit: JointFit, spectra: tuple[Spectrum, Spectrum]) -> dict[str, object]:
    p = fit.physical.copy()
    scale = np.array([0.02, 50.0, 25.0, 2e-4])
    columns = []
    for j, h in enumerate(scale):
        plus, minus = p.copy(), p.copy()
        plus[j] += h
        minus[j] -= h
        columns.append((profiled_residual(plus, fit.material, spectra, fit.order) - profiled_residual(minus, fit.material, spectra, fit.order)) / (2.0 * h))
    jac = np.column_stack(columns)
    norms = np.linalg.norm(jac, axis=0)
    normalized = jac / np.maximum(norms, 1e-15)
    singular = np.linalg.svd(normalized, compute_uv=False)
    return {
        "singular_values": singular.tolist(),
        "condition_number": float(singular[0] / singular[-1]),
        "column_norms": norms.tolist(),
        "correlation": np.corrcoef(normalized, rowvar=False).tolist(),
    }


def block_bootstrap_thickness(fit: JointFit, spectra: tuple[Spectrum, Spectrum], *, replicates: int = 300, block: int = 24, seed: int = 2025) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base_models = [physical_reflectance(fit.material, s, fit.physical, fit.order) for s in spectra]
    calibrated = [fit.calibration[i][0] * base_models[i] + fit.calibration[i][1] for i in range(2)]
    residuals = [calibrated[i] - spectra[i].reflectance for i in range(2)]
    result = np.empty(replicates)
    for k in range(replicates):
        synthetic = []
        for i, spectrum in enumerate(spectra):
            n = spectrum.wavenumber_cm.size
            starts = rng.integers(0, max(1, n - block + 1), size=int(np.ceil(n / block)))
            sampled = np.concatenate([residuals[i][s:s + block] for s in starts])[:n]
            synthetic.append(Spectrum(spectrum.wavenumber_cm, calibrated[i] - sampled, spectrum.angle_deg, spectrum.source))
        objective = lambda d: float(np.mean(profiled_residual(np.r_[d, fit.physical[1:]], fit.material, tuple(synthetic), fit.order) ** 2))
        optimum = minimize_scalar(objective, bounds=(fit.physical[0] - 0.35, fit.physical[0] + 0.35), method="bounded", options={"xatol": 1e-6})
        result[k] = optimum.x
    return result


def continuous_phase_thickness(spectra: tuple[Spectrum, Spectrum], material: str, band: tuple[float, float]) -> dict[str, object]:
    """Independent matched-phase estimate without using the intensity model.

    Slowly varying baselines are removed first.  For each trial thickness the
    residual spectrum is projected on the dispersion-corrected complex phase;
    the two angle scores are normalized and summed.
    """
    prepared = []
    for spectrum in spectra:
        n = spectrum.wavenumber_cm.size
        window = min(251, n if n % 2 else n - 1)
        window = max(51, window if window % 2 else window - 1)
        baseline = savgol_filter(spectrum.reflectance, window, 3)
        oscillation = spectrum.reflectance - baseline
        q = np.real(np.sqrt(background_index(material, spectrum.wavenumber_cm) ** 2 - np.sin(np.deg2rad(spectrum.angle_deg)) ** 2 + 0j))
        coordinate = 2.0e-4 * spectrum.wavenumber_cm * q
        prepared.append((coordinate, oscillation, float(np.linalg.norm(oscillation))))

    def score(d_um: float) -> float:
        total = 0.0
        for coordinate, oscillation, norm in prepared:
            projection = np.sum(oscillation * np.exp(-2j * np.pi * d_um * coordinate))
            total += abs(projection) / max(norm * np.sqrt(oscillation.size), 1e-15)
        return float(total)

    grid = np.linspace(6.0 if material == "sic" else 2.0, 9.0 if material == "sic" else 5.0, 1201)
    values = np.array([score(d) for d in grid])
    index = int(np.argmax(values))
    left, right = grid[max(0, index - 2)], grid[min(grid.size - 1, index + 2)]
    optimum = minimize_scalar(lambda d: -score(d), bounds=(left, right), method="bounded", options={"xatol": 1e-9})
    per_angle = []
    for i, (coordinate, oscillation, norm) in enumerate(prepared):
        local = lambda d: -float(abs(np.sum(oscillation * np.exp(-2j * np.pi * d * coordinate))) / max(norm * np.sqrt(oscillation.size), 1e-15))
        loc_grid = np.array([-local(d) for d in grid])
        j = int(np.argmax(loc_grid))
        local_opt = minimize_scalar(local, bounds=(grid[max(0,j-2)], grid[min(grid.size-1,j+2)]), method="bounded")
        per_angle.append({"angle_deg": spectra[i].angle_deg, "thickness_um": float(local_opt.x), "coherence": float(-local_opt.fun)})
    return {"thickness_um": float(optimum.x), "joint_coherence": float(-optimum.fun), "per_angle": per_angle, "band_cm-1": list(band)}


def fit_loop_metrics(fit: JointFit, spectra: tuple[Spectrum, Spectrum]) -> dict[str, float]:
    metrics = []
    d, plasma, damping, scale = fit.physical
    for spectrum in spectra:
        film_n = scale * background_index(fit.material, spectrum.wavenumber_cm)
        eps = drude_substrate_permittivity(fit.material, spectrum.wavenumber_cm, plasma, damping, scale)
        metrics.append(loop_metrics(layer_amplitudes(spectrum.wavenumber_cm, spectrum.angle_deg, d, film_n, eps)))
    return {key: float(max(m[key] for m in metrics)) if key.endswith("max") else float(np.median([m[key] for m in metrics])) for key in metrics[0]}


def information_criteria(fit: JointFit, k: int = 8) -> dict[str, float]:
    n = fit.residual.size
    sse = float(np.sum(fit.residual**2))
    return {"AIC": float(n * np.log(sse / n) + 2 * k), "BIC": float(n * np.log(sse / n) + k * np.log(n))}

"""Reproduce every numerical result used by the run_02 true-problem analysis."""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from shared.code.data_io import Spectrum, load_official_bundle, select_band
from shared.code.inversion import (
    JointFit,
    block_bootstrap_thickness,
    continuous_phase_thickness,
    fit_joint,
    fit_loop_metrics,
    information_criteria,
    normalized_jacobian_svd,
    physical_reflectance,
    profile_thickness,
    refine_from,
)
from shared.code.materials import background_index, drude_substrate_permittivity
from shared.code.optics import unpolarized_reflectance


# The background-dispersion scale is anchored to its registered source in the
# principal inversion.  Its ±2% uncertainty is propagated separately below;
# freely fitting it makes only the optical thickness identifiable.
SIC_BOUNDS = [(6.5, 8.5), (20.0, 5000.0), (5.0, 4000.0), (0.999999, 1.000001)]
SI_BOUNDS = [(2.5, 4.5), (500.0, 25000.0), (10.0, 8000.0), (0.999999, 1.000001)]


def fit_dict(fit: JointFit) -> dict[str, object]:
    return {
        "material": fit.material,
        "order": "infinity" if math.isinf(fit.order) else int(fit.order),
        "band_cm-1": list(fit.band),
        "thickness_um": float(fit.physical[0]),
        "plasma_wavenumber_cm-1": float(fit.physical[1]),
        "damping_wavenumber_cm-1": float(fit.physical[2]),
        "index_scale": float(fit.physical[3]),
        "calibration": [c.tolist() for c in fit.calibration],
        "rmse_fraction": fit.rmse,
        "rmse_percentage_point": 100.0 * fit.rmse,
        "mae_fraction": fit.mae,
        "r2": fit.r2,
        "AIC_BIC": information_criteria(fit),
        "success": fit.success,
    }


def save_csv(path: Path, header: str, array: np.ndarray) -> None:
    np.savetxt(path, array, delimiter=",", header=header, comments="", fmt="%.10g")


def plot_joint_fit(path: Path, spectra: tuple[Spectrum, Spectrum], fits: list[tuple[str, JointFit]], title: str) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.6), sharex=True)
    for axis, spectrum, index in zip(axes, spectra, range(2)):
        axis.plot(spectrum.wavenumber_cm, 100 * spectrum.reflectance, color="#333333", lw=1.0, label="Observed")
        for label, fit in fits:
            base = physical_reflectance(fit.material, spectrum, fit.physical, fit.order)
            prediction = fit.calibration[index][0] * base + fit.calibration[index][1]
            axis.plot(spectrum.wavenumber_cm, 100 * prediction, lw=1.2, label=label)
        axis.set_ylabel(f"R at {spectrum.angle_deg:.0f} deg (%)")
        axis.grid(alpha=0.25)
    axes[0].legend(ncol=max(1, len(fits) + 1), fontsize=8)
    axes[-1].set_xlabel("Wavenumber (cm$^{-1}$)")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=240)
    plt.close(fig)


def synthetic_recovery(seed: int = 2025) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    x = np.linspace(1200.0, 3000.0, 700)
    true = np.array([7.35, 1700.0, 620.0, 1.0])
    spectra = []
    for angle, gain, bias in ((10.0, 1.08, 0.015), (15.0, 0.96, 0.025)):
        n1 = true[3] * background_index("sic", x)
        eps2 = drude_substrate_permittivity("sic", x, true[1], true[2], true[3])
        base = unpolarized_reflectance(x, angle, true[0], n1, eps2, 1)
        y = gain * base + bias + rng.normal(0.0, 8e-4, x.size)
        spectra.append(Spectrum(x, y, angle, "synthetic"))
    recovered = refine_from("sic", tuple(spectra), 1, (1200.0, 3000.0), SIC_BOUNDS, np.array([7.0, 1400.0, 900.0, 1.0]))
    error = recovered.physical - true
    return {
        "true": true.tolist(),
        "recovered": recovered.physical.tolist(),
        "absolute_error": np.abs(error).tolist(),
        "relative_error": (np.abs(error) / true).tolist(),
        "thickness_absolute_error_um": float(abs(error[0])),
        "rmse_percentage_point": float(100 * recovered.rmse),
    }


def choose_multistart(material: str, spectra: tuple[Spectrum, Spectrum], order: int | float, band: tuple[float, float], bounds: list[tuple[float, float]], seeds: list[int], maxiter: int) -> tuple[JointFit, list[dict[str, float]]]:
    fits, rows = [], []
    for seed in seeds:
        fit = fit_joint(material, spectra, order, band, bounds, seed=seed, maxiter=maxiter)
        fits.append(fit)
        rows.append({"seed": seed, "thickness_um": float(fit.physical[0]), "rmse": fit.rmse})
    return min(fits, key=lambda item: item.rmse), rows


def run(data_dir: Path, project: Path, quick: bool) -> dict[str, object]:
    out = project / "output" / "results"
    q2_figs = project / "modules" / "30_q2" / "figures"
    q3_figs = project / "modules" / "40_q3" / "figures"
    q2_tabs = project / "modules" / "30_q2" / "tables"
    q3_tabs = project / "modules" / "40_q3" / "tables"
    for directory in (out, q2_figs, q3_figs, q2_tabs, q3_tabs):
        directory.mkdir(parents=True, exist_ok=True)
    bundle = load_official_bundle(data_dir)
    step = 8 if quick else 4
    iterations = 35 if quick else 75
    seeds = [2025, 2026] if quick else [2025, 2026, 2027]

    # Q1 numerical consistency evidence.
    synthetic = synthetic_recovery()

    # Q2: 2000-3900 cm^-1 is selected after comparing the reviewed papers'
    # bands and the stability plateau; all alternatives use identical loss
    # and parameter definitions.
    q2_band = (2000.0, 3900.0)
    q2_spectra = tuple(select_band(s, q2_band, smooth_window=31, step=step) for s in bundle["sic"])
    q2_fit, q2_multistart = choose_multistart("sic", q2_spectra, 1, q2_band, SIC_BOUNDS, seeds, iterations)
    q2_phase = continuous_phase_thickness(q2_spectra, "sic", q2_band)
    q2_svd = normalized_jacobian_svd(q2_fit, q2_spectra)
    profile_grid = np.linspace(max(SIC_BOUNDS[0][0], q2_fit.physical[0] - 0.35), min(SIC_BOUNDS[0][1], q2_fit.physical[0] + 0.35), 31 if quick else 61)
    q2_profile = profile_thickness(q2_fit, q2_spectra, SIC_BOUNDS, profile_grid)
    q2_boot = block_bootstrap_thickness(q2_fit, q2_spectra, replicates=60 if quick else 300, block=16 if quick else 24)
    q2_bands = [(1200.0, 3000.0), (1500.0, 3300.0), (1800.0, 3500.0), (2000.0, 3900.0), (2500.0, 3300.0)]
    q2_band_rows = []
    q2_band_fits = []
    for band in q2_bands:
        spectra = tuple(select_band(s, band, smooth_window=31, step=step) for s in bundle["sic"])
        fit = q2_fit if band == q2_band else refine_from("sic", spectra, 1, band, SIC_BOUNDS, q2_fit.physical)
        q2_band_fits.append(fit)
        q2_band_rows.append([band[0], band[1], fit.physical[0], 100 * fit.rmse, fit.r2, fit.physical[3]])
    q2_band_array = np.asarray(q2_band_rows)
    q2_scale_rows = []
    for fixed_scale in (0.98, 0.99, 1.00, 1.01, 1.02):
        fixed_bounds = SIC_BOUNDS[:-1] + [(fixed_scale - 1e-7, fixed_scale + 1e-7)]
        initial = q2_fit.physical.copy()
        initial[0] *= q2_fit.physical[3] / fixed_scale
        initial[3] = fixed_scale
        fit = refine_from("sic", q2_spectra, 1, q2_band, fixed_bounds, initial)
        q2_scale_rows.append([fixed_scale, fit.physical[0], 100 * fit.rmse])
    q2_scale_array = np.asarray(q2_scale_rows)

    # Q3 SiC rollback comparison: nested order-one and Airy models, same band,
    # data, parameters, loss, smoothing, and calibration.
    sic_multi = refine_from("sic", q2_spectra, math.inf, q2_band, SIC_BOUNDS, q2_fit.physical)
    sic_orders = []
    for order in (1, 2, 3, 4, 6):
        fit = q2_fit if order == 1 else refine_from("sic", q2_spectra, order, q2_band, SIC_BOUNDS, sic_multi.physical)
        sic_orders.append([order, fit.physical[0], 100 * fit.rmse, information_criteria(fit)["AIC"]])
    sic_orders.append([np.inf, sic_multi.physical[0], 100 * sic_multi.rmse, information_criteria(sic_multi)["AIC"]])

    # Q3 Si: the free-carrier response is informative in 750-1800 cm^-1.
    si_band = (750.0, 1800.0)
    si_spectra = tuple(select_band(s, si_band, smooth_window=21, step=step) for s in bundle["si"])
    si_multi, si_multistart = choose_multistart("si", si_spectra, math.inf, si_band, SI_BOUNDS, seeds, iterations)
    si_double = refine_from("si", si_spectra, 1, si_band, SI_BOUNDS, si_multi.physical)
    si_orders = []
    for order in (1, 2, 3, 4, 6):
        initial = si_double.physical if order == 1 else si_multi.physical
        fit = si_double if order == 1 else refine_from("si", si_spectra, order, si_band, SI_BOUNDS, initial)
        si_orders.append([order, fit.physical[0], 100 * fit.rmse, information_criteria(fit)["AIC"]])
    si_orders.append([np.inf, si_multi.physical[0], 100 * si_multi.rmse, information_criteria(si_multi)["AIC"]])
    si_band_rows = []
    for band in ((650.0, 1600.0), (750.0, 1800.0), (800.0, 2000.0), (900.0, 2200.0)):
        spectra = tuple(select_band(s, band, smooth_window=21, step=step) for s in bundle["si"])
        fit = si_multi if band == si_band else refine_from("si", spectra, math.inf, band, SI_BOUNDS, si_multi.physical)
        si_band_rows.append([band[0], band[1], fit.physical[0], 100 * fit.rmse, fit.r2, fit.physical[3]])
    si_band_array = np.asarray(si_band_rows)

    # Persist exact tables.
    save_csv(q2_tabs / "q2_band_sensitivity.csv", "lower_cm-1,upper_cm-1,d_um,rmse_percentage_point,r2,index_scale", q2_band_array)
    save_csv(q2_tabs / "q2_thickness_profile.csv", "d_um,profile_rmse_fraction", q2_profile)
    save_csv(q2_tabs / "q2_block_bootstrap.csv", "d_um", q2_boot[:, None])
    save_csv(q2_tabs / "q2_index_scale_sensitivity.csv", "index_scale,d_um,rmse_percentage_point", q2_scale_array)
    save_csv(q3_tabs / "q3_sic_order_convergence.csv", "order,d_um,rmse_percentage_point,AIC", np.asarray(sic_orders))
    save_csv(q3_tabs / "q3_si_order_convergence.csv", "order,d_um,rmse_percentage_point,AIC", np.asarray(si_orders))
    save_csv(q3_tabs / "q3_si_band_sensitivity.csv", "lower_cm-1,upper_cm-1,d_um,rmse_percentage_point,r2,index_scale", si_band_array)

    # Figures used by the report and paper.
    plot_joint_fit(q2_figs / "q2_sic_joint_fit.png", q2_spectra, [("Double-beam", q2_fit)], "SiC double-angle joint inversion")
    plot_joint_fit(q3_figs / "q3_sic_model_comparison.png", q2_spectra, [("Double-beam", q2_fit), ("Airy", sic_multi)], "SiC nested-model comparison")
    plot_joint_fit(q3_figs / "q3_si_model_comparison.png", si_spectra, [("Double-beam", si_double), ("Airy", si_multi)], "Si nested-model comparison")

    fig, axis = plt.subplots(figsize=(7.2, 4.4)); axis.plot(q2_profile[:, 0], 100 * q2_profile[:, 1], "o-", ms=3); axis.axvline(q2_fit.physical[0], color="#c23b23", ls="--"); axis.set(xlabel="SiC thickness (um)", ylabel="Profile RMSE (percentage point)", title="Thickness profile objective"); axis.grid(alpha=.3); fig.tight_layout(); fig.savefig(q2_figs / "q2_thickness_profile.png", dpi=240); plt.close(fig)
    fig, axis = plt.subplots(figsize=(7.2, 4.4)); axis.hist(q2_boot, bins=24, color="#4c78a8", edgecolor="white"); axis.axvline(q2_fit.physical[0], color="#c23b23", ls="--"); axis.set(xlabel="SiC thickness (um)", ylabel="Bootstrap count", title="Moving-block bootstrap"); fig.tight_layout(); fig.savefig(q2_figs / "q2_block_bootstrap.png", dpi=240); plt.close(fig)
    fig, axis = plt.subplots(figsize=(7.2, 4.4)); labels=[f"{int(a)}-{int(b)}" for a,b in q2_band_array[:,:2]]; axis.plot(labels, q2_band_array[:,2], "o-"); axis.set(xlabel="Band (cm$^{-1}$)", ylabel="Thickness (um)", title="SiC band sensitivity"); axis.grid(alpha=.3); fig.tight_layout(); fig.savefig(q2_figs / "q2_band_sensitivity.png", dpi=240); plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(9.2,4.0)); si_arr=np.asarray(si_orders); axes[0].plot(["1","2","3","4","6","Airy"],si_arr[:,1],"o-"); axes[1].plot(["1","2","3","4","6","Airy"],si_arr[:,2],"o-"); axes[0].set_ylabel("Thickness (um)"); axes[1].set_ylabel("RMSE (percentage point)"); [ax.set_xlabel("Retained internal beams") for ax in axes]; [ax.grid(alpha=.3) for ax in axes]; fig.suptitle("Si finite-order convergence"); fig.tight_layout(); fig.savefig(q3_figs / "q3_si_order_convergence.png", dpi=240); plt.close(fig)

    boot_ci = np.quantile(q2_boot, [0.025, 0.5, 0.975])
    result = {
        "run": {"mode": "quick" if quick else "full", "random_seeds": seeds, "official_data_dir": str(data_dir)},
        "Q1": {"synthetic_recovery": synthetic},
        "Q2": {
            "main": fit_dict(q2_fit),
            "phase_cross_validation": q2_phase,
            "multistart": q2_multistart,
            "identifiability": q2_svd,
            "profile": {"minimum_um": float(q2_profile[np.argmin(q2_profile[:,1]),0]), "grid_span_um": [float(q2_profile[0,0]), float(q2_profile[-1,0])]},
            "block_bootstrap": {"replicates": int(q2_boot.size), "block_length": 16 if quick else 24, "quantile_2.5_50_97.5_um": boot_ci.tolist(), "std_um": float(np.std(q2_boot, ddof=1))},
            "band_sensitivity": {"thickness_min_um": float(q2_band_array[:,2].min()), "thickness_max_um": float(q2_band_array[:,2].max()), "rows": q2_band_array.tolist()},
            "index_scale_sensitivity": {"thickness_min_um": float(q2_scale_array[:,1].min()), "thickness_max_um": float(q2_scale_array[:,1].max()), "rows": q2_scale_array.tolist()},
        },
        "Q3": {
            "SiC": {"double": fit_dict(q2_fit), "Airy": fit_dict(sic_multi), "loop": fit_loop_metrics(sic_multi, q2_spectra), "delta_d_Airy_minus_double_um": float(sic_multi.physical[0]-q2_fit.physical[0]), "order_convergence": np.asarray(sic_orders).tolist()},
            "Si": {"double": fit_dict(si_double), "Airy": fit_dict(si_multi), "loop": fit_loop_metrics(si_multi, si_spectra), "delta_d_Airy_minus_double_um": float(si_multi.physical[0]-si_double.physical[0]), "multistart": si_multistart, "order_convergence": np.asarray(si_orders).tolist(), "band_sensitivity": {"thickness_min_um": float(si_band_array[:,2].min()), "thickness_max_um": float(si_band_array[:,2].max()), "rows": si_band_array.tolist()}},
        },
    }
    (out / ("analysis_quick.json" if quick else "analysis_results.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.data_dir, args.project, args.quick)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

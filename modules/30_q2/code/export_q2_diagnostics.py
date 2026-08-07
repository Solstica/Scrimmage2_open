"""Export Q2 multistart/basin diagnostics without changing the frozen solver.

The diagnostic source is the frozen PAPER_A fit tables already committed in the
repository. They contain exactly the 2500--3300 cm^-1 observations used by the
formal solver, so no external official-data directory is required.

This script mirrors solve_q2_paper_a.fit_one_angle:
1. 90 stage-I starts with fixed Sellmeier parameters;
2. select up to eight distinct representative attraction basins;
3. refine the full 10-parameter model independently for each angle.

It only exports validation data. It never performs a joint/shared-angle fit and
it verifies that the best solutions reproduce q2_paper_a_results.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

MODULE = Path(__file__).resolve().parents[1]
PROJECT = Path(__file__).resolve().parents[3]
CODE = MODULE / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import solve_q2_paper_a as q2


def spectrum_from_frozen_table(label: str, angle: float) -> dict[str, object]:
    path = MODULE / "tables" / f"q2_{label}_paper_a_fit.csv"
    frame = pd.read_csv(path)
    return {
        "wavenumber": frame["wavenumber_cm-1"].to_numpy(float),
        "reflectance": frame["observed_reflectance_fraction"].to_numpy(float),
        "angle_deg": float(angle),
        "source": str(path),
        "source_sha256": "committed_frozen_fit_table",
    }


def nearest_representative_assignments(stage1_rows, candidates):
    if not candidates:
        return [-1] * len(stage1_rows)
    reps = np.asarray(candidates, dtype=float)
    span = np.maximum(q2.STAGE1_UPPER - q2.STAGE1_LOWER, 1e-12)
    assignments = []
    for row in stage1_rows:
        point = np.array([
            row["d_stage1_um"], row["log10N_stage1"], row["n3_stage1"]
        ], dtype=float)
        d2 = np.sum(((reps - point) / span) ** 2, axis=1)
        assignments.append(int(np.argmin(d2)) + 1)
    return assignments


def diagnose_one_angle(spectrum):
    stage1_rows = []
    stage1_rankable = []
    starts = product(
        np.linspace(6.6, 8.4, 10),
        (15.5, 18.0, 20.0),
        (2.35, 2.75, 3.10),
    )
    for seed_id, (d0, log_n0, n30) in enumerate(starts, start=1):
        fit = least_squares(
            lambda p: q2.residual_full(np.r_[p, q2.SELL_REF], spectrum),
            np.array([d0, log_n0, n30]),
            bounds=(q2.STAGE1_LOWER, q2.STAGE1_UPPER),
            x_scale="jac", max_nfev=2500,
            ftol=1e-11, xtol=1e-11, gtol=1e-11,
        )
        rmse = float(np.sqrt(np.mean(fit.fun**2)))
        raw_key = (round(float(fit.x[0]), 3), round(float(fit.x[1]), 2))
        stage1_rankable.append((rmse, fit.x.copy()))
        stage1_rows.append({
            "angle_deg": float(spectrum["angle_deg"]),
            "seed_id": seed_id,
            "d_init_um": float(d0),
            "log10N_init": float(log_n0),
            "n3_init": float(n30),
            "d_stage1_um": float(fit.x[0]),
            "log10N_stage1": float(fit.x[1]),
            "n3_stage1": float(fit.x[2]),
            "rmse_stage1": rmse,
            "success": bool(fit.success),
            "nfev": int(fit.nfev),
            "raw_basin_key": f"{raw_key[0]:.3f}|{raw_key[1]:.2f}",
        })

    candidates, seen = [], set()
    for _, parameters in sorted(stage1_rankable, key=lambda row: row[0]):
        key = (round(float(parameters[0]), 3), round(float(parameters[1]), 2))
        if key not in seen:
            candidates.append(parameters.copy())
            seen.add(key)
        if len(candidates) == 8:
            break

    assignments = nearest_representative_assignments(stage1_rows, candidates)
    for row, basin_id in zip(stage1_rows, assignments):
        row["representative_basin_id"] = basin_id
    support = {i: assignments.count(i) for i in range(1, len(candidates) + 1)}

    refined = []
    for basin_id, parameters in enumerate(candidates, start=1):
        fit = least_squares(
            q2.residual_full, np.r_[parameters, q2.SELL_REF], args=(spectrum,),
            bounds=(q2.FULL_LOWER, q2.FULL_UPPER), x_scale="jac",
            max_nfev=5000, ftol=1e-12, xtol=1e-12, gtol=1e-12,
        )
        fitted = q2.reflectance(
            np.asarray(spectrum["wavenumber"]),
            float(spectrum["angle_deg"]), fit.x,
        )
        metric = q2.metrics(np.asarray(spectrum["reflectance"]), fitted)
        hits = q2.boundary_hits(fit.x)
        refined.append({
            "basin_id": basin_id,
            "support_count_stage1": support.get(basin_id, 0),
            "parameters": fit.x.copy(),
            "rmse": float(np.sqrt(np.mean(fit.fun**2))),
            "mae": float(metric["mae_fraction"]),
            "r2": float(metric["r2"]),
            "success": bool(fit.success),
            "nfev": int(fit.nfev),
            "boundary_hits": hits,
        })
    refined.sort(key=lambda row: float(row["rmse"]))

    refined_rows = []
    for rank, row in enumerate(refined, start=1):
        p = np.asarray(row["parameters"])
        refined_rows.append({
            "angle_deg": float(spectrum["angle_deg"]),
            "rank_by_rmse": rank,
            "basin_id": int(row["basin_id"]),
            "support_count_stage1": int(row["support_count_stage1"]),
            "thickness_um": float(p[0]),
            "log10N": float(p[1]),
            "substrate_index": float(p[2]),
            "rmse": float(row["rmse"]),
            "mae": float(row["mae"]),
            "r2": float(row["r2"]),
            "success": bool(row["success"]),
            "nfev": int(row["nfev"]),
            "boundary_hit_count": len(row["boundary_hits"]),
            "boundary_hits": ";".join(row["boundary_hits"]),
        })
    return np.asarray(refined[0]["parameters"]), stage1_rows, refined_rows


def summary_row(angle, stage1_rows, refined_rows):
    best = refined_rows[0]
    second = refined_rows[1] if len(refined_rows) > 1 else None
    best_rmse = float(best["rmse"])
    second_rmse = float(second["rmse"]) if second else np.nan
    return {
        "angle_deg": float(angle),
        "best_basin_id": int(best["basin_id"]),
        "best_thickness_um": float(best["thickness_um"]),
        "best_rmse": best_rmse,
        "second_best_thickness_um": float(second["thickness_um"]) if second else np.nan,
        "second_best_rmse": second_rmse,
        "rmse_gap_relative": float((second_rmse-best_rmse)/best_rmse) if second else np.nan,
        "sse_ratio_second_to_best": float((second_rmse/best_rmse)**2) if second else np.nan,
        "best_basin_support_count": int(best["support_count_stage1"]),
        "best_basin_support_fraction": float(best["support_count_stage1"])/len(stage1_rows),
        "total_stage1_starts": len(stage1_rows),
        "raw_stage1_basin_key_count": len({row["raw_basin_key"] for row in stage1_rows}),
        "refined_basin_count": len(refined_rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=PROJECT)
    args = parser.parse_args()
    project = args.project.resolve()
    module = project / "modules" / "30_q2"
    tables = module / "tables"
    frozen = json.loads((project / "output/results/q2_paper_a_results.json").read_text(encoding="utf-8"))

    all_stage1, all_refined, all_summary = [], [], []
    recomputed = []
    for label, _, angle in q2.FILES:
        spectrum = spectrum_from_frozen_table(label, angle)
        best, stage1, refined = diagnose_one_angle(spectrum)
        recomputed.append(float(best[0]))
        all_stage1.extend(stage1)
        all_refined.extend(refined)
        all_summary.append(summary_row(angle, stage1, refined))

    frozen_angles = [float(row["thickness_um"]) for row in frozen["angle_results"]]
    if not np.allclose(recomputed, frozen_angles, atol=5e-6, rtol=0.0):
        raise RuntimeError(f"Q2 diagnostic drift: recomputed={recomputed}, frozen={frozen_angles}")
    frozen_mean = float(frozen["primary_result"]["thickness_um"])
    if abs(float(np.mean(recomputed)) - frozen_mean) > 5e-6:
        raise RuntimeError("Q2 diagnostic mean drifted from frozen result")

    pd.DataFrame(all_stage1).to_csv(tables / "q2_multistart_stage1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(all_refined).to_csv(tables / "q2_multistart_refined.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(all_summary).to_csv(tables / "q2_multistart_summary.csv", index=False, encoding="utf-8-sig")
    print(json.dumps({
        "status": "PASS",
        "frozen_angle_thickness_um": frozen_angles,
        "recomputed_angle_thickness_um": recomputed,
        "frozen_mean_thickness_um": frozen_mean,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

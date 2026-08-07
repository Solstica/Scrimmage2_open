"""Export reproducible Q2/Q3 tables for the retained Origin templates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
Q2_TARGET = np.array([7.856635820616846, 7.622957415253701, 7.739796617935274])
Q3_TARGET = np.array([3.2479974169771597, 3.1875196790859226, 3.217758548031541])
BANNED_TEXT = ("7.384039", "3.308745", "joint_fit", "shared_fit")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(frame: pd.DataFrame, path: Path, records: list[dict[str, object]], project: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    records.append({
        "path": str(path.relative_to(project)).replace("\\", "/"),
        "rows": int(frame.shape[0]),
        "columns": list(frame.columns),
        "sha256": sha256(path),
    })


def export_existing_csv(
    source: Path, destination: Path, records: list[dict[str, object]], project: Path,
) -> None:
    """Copy a canonical diagnostic table through the same CSV pipeline."""
    write_csv(pd.read_csv(source), destination, records, project)


def read_raw(path: Path, angle: float, low: float, high: float) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=0, usecols=[0, 1], engine="openpyxl")
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    values = frame.to_numpy(float)
    values = values[np.isfinite(values).all(axis=1) & (values[:, 0] > 0.0)]
    values = values[np.argsort(values[:, 0])]
    return pd.DataFrame({
        "wavenumber_cm1": values[:, 0],
        "reflectance_observed": values[:, 1] / 100.0,
        "angle_deg": angle,
        "in_fit_band": ((values[:, 0] >= low) & (values[:, 0] <= high)).astype(int),
    })


def cluster_basins(values: np.ndarray, tolerance: float = 0.01) -> list[str]:
    order = np.argsort(values)
    labels = [""] * len(values)
    basin = 0
    center = None
    for index in order:
        value = float(values[index])
        if center is None or abs(value - center) > tolerance:
            basin += 1
            center = value
        labels[index] = f"B{basin:02d}"
    return labels


def residual_histogram(fits: dict[float, pd.DataFrame], bins: int = 30) -> pd.DataFrame:
    maximum = max(float(np.max(np.abs(frame["residual_signed"]))) for frame in fits.values())
    edges = np.linspace(-maximum, maximum, bins + 1)
    output = pd.DataFrame({
        "bin_left": edges[:-1],
        "bin_right": edges[1:],
        "bin_center": 0.5 * (edges[:-1] + edges[1:]),
    })
    for angle, frame in fits.items():
        counts, _ = np.histogram(frame["residual_signed"], bins=edges)
        output[f"count_{int(angle)}deg"] = counts
        output[f"fraction_{int(angle)}deg"] = counts / max(int(counts.sum()), 1)
    return output


def residual_boxplot(fits: dict[float, pd.DataFrame]) -> pd.DataFrame:
    count = max(frame.shape[0] for frame in fits.values())
    output = pd.DataFrame({"sample_id": np.arange(1, count + 1)})
    for angle, frame in fits.items():
        output[f"residual_{int(angle)}deg"] = pd.Series(frame["residual_signed"].to_numpy())
    return output


def residual_heatmap(
    fits: dict[float, pd.DataFrame], low: float, high: float, bins: int = 40,
) -> pd.DataFrame:
    edges = np.linspace(low, high, bins + 1)
    rows = []
    for angle, frame in fits.items():
        wave = frame["wavenumber_cm1"].to_numpy(float)
        residual = frame["residual_signed"].to_numpy(float)
        bucket = np.clip(np.digitize(wave, edges) - 1, 0, bins - 1)
        for index in range(bins):
            selected = residual[bucket == index]
            rows.append({
                "angle_deg": angle,
                "bin_left_cm1": edges[index],
                "bin_right_cm1": edges[index + 1],
                "bin_center_cm1": 0.5 * (edges[index] + edges[index + 1]),
                "residual_mean": float(np.mean(selected)) if selected.size else np.nan,
                "sample_count": int(selected.size),
            })
    return pd.DataFrame(rows)


def residual_ecdf(fits: dict[float, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for angle, frame in fits.items():
        values = np.sort(frame["residual_abs"].to_numpy(float))
        for index, value in enumerate(values, start=1):
            rows.append({
                "angle_deg": angle,
                "residual_abs": value,
                "ecdf": index / values.size,
            })
    return pd.DataFrame(rows)


def standardize_q2_fit(path: Path, angle: float) -> pd.DataFrame:
    source = pd.read_csv(path)
    return pd.DataFrame({
        "wavenumber_cm1": source["wavenumber_cm-1"],
        "reflectance_observed": source["observed_reflectance_fraction"],
        "reflectance_fitted": source["fitted_reflectance_fraction"],
        "residual_signed": source["residual_fraction"],
        "residual_abs": source["residual_fraction"].abs(),
        "angle_deg": angle,
    })


def standardize_q3_fit(path: Path, angle: float) -> pd.DataFrame:
    source = pd.read_csv(path)
    return pd.DataFrame({
        "wavenumber_cm1": source["wavenumber_cm-1"],
        "reflectance_observed": source["observed_reflectance_fraction"],
        "reflectance_airy": source["airy_reflectance_fraction"],
        "reflectance_double_same_params": source["double_beam_comparison_fraction"],
        "residual_signed": source["airy_residual_fraction"],
        "residual_abs": source["airy_residual_fraction"].abs(),
        "eta3_percent": source["third_beam_ratio_percent"],
        "angle_deg": angle,
    })


def q2_tables(
    project: Path, data_dir: Path, diagnostic: dict[str, object], frozen: dict[str, object],
    records: list[dict[str, object]],
) -> None:
    output = project / "modules/30_q2/figures/editable/origin_data/csv"
    fits = {
        10.0: standardize_q2_fit(project / "modules/30_q2/tables/q2_10deg_paper_a_fit.csv", 10.0),
        15.0: standardize_q2_fit(project / "modules/30_q2/tables/q2_15deg_paper_a_fit.csv", 15.0),
    }
    write_csv(read_raw(data_dir / "附件1.xlsx", 10.0, 2500.0, 3300.0), output / "q2_raw_10deg.csv", records, project)
    write_csv(read_raw(data_dir / "附件2.xlsx", 15.0, 2500.0, 3300.0), output / "q2_raw_15deg.csv", records, project)
    for angle, frame in fits.items():
        write_csv(frame, output / f"q2_fit_{int(angle)}deg.csv", records, project)

    summary_rows = []
    for index, (angle, frame) in enumerate(fits.items()):
        row = diagnostic["angle_results"][index]
        frozen_row = frozen["angle_results"][index]
        observed = frame["reflectance_observed"].to_numpy(float)
        residual = frame["residual_signed"].to_numpy(float)
        stable_mape = bool(np.min(np.abs(observed)) > 1.0e-6)
        summary_rows.append({
            "result_type": "independent_angle_fit",
            "angle_deg": angle,
            "thickness_um": frozen_row["thickness_um"],
            "rmse_fraction": row["metrics"]["rmse_fraction"],
            "r2": row["metrics"]["r2"],
            "mae_fraction": float(np.mean(np.abs(residual))),
            "mape_percent": float(100.0 * np.mean(np.abs(residual / observed))) if stable_mape else np.nan,
            "mape_defined": stable_mape,
            "boundary_hits": ";".join(row["boundary_hits"]),
        })
    summary_rows.append({
        "result_type": "arithmetic_mean",
        "angle_deg": np.nan,
        "thickness_um": frozen["primary_result"]["thickness_um"],
        "rmse_fraction": np.nan,
        "r2": np.nan,
        "mae_fraction": np.nan,
        "mape_percent": np.nan,
        "mape_defined": False,
        "boundary_hits": "",
    })
    summary = pd.DataFrame(summary_rows)
    write_csv(summary, output / "q2_summary.csv", records, project)

    multistart_rows = []
    for angle_index, angle in enumerate((10.0, 15.0)):
        for row in diagnostic["angle_results"][angle_index]["multistart"]:
            initial = row["initial"]
            final = row["parameters"]
            multistart_rows.append({
                "angle_deg": angle,
                "seed_id": row["seed_id"],
                "d_init_um": initial["thickness_um"],
                "log10N_init_cm3": initial["log10_carrier_cm3"],
                "N_init_cm3": 10.0 ** initial["log10_carrier_cm3"],
                "n3_init": initial["substrate_index"],
                "d_final_um": final["thickness_um"],
                "rmse_final": row["rmse_fraction"],
                "success": row["success"],
                "boundary_hits": ";".join(row["boundary_hits"]),
            })
    multistart = pd.DataFrame(multistart_rows)
    multistart["basin_id"] = ""
    for angle in (10.0, 15.0):
        mask = multistart["angle_deg"] == angle
        multistart.loc[mask, "basin_id"] = cluster_basins(multistart.loc[mask, "d_final_um"].to_numpy())
    write_csv(multistart, output / "q2_multistart.csv", records, project)
    write_csv(residual_histogram(fits), output / "q2_residual_histogram.csv", records, project)
    write_csv(residual_boxplot(fits), output / "q2_residual_boxplot.csv", records, project)
    write_csv(residual_heatmap(fits, 2500.0, 3300.0), output / "q2_residual_heatmap.csv", records, project)
    write_csv(residual_ecdf(fits), output / "q2_residual_ecdf.csv", records, project)
    diagnostic_tables = project / "modules/30_q2/tables"
    for source_name, output_name in (
        ("q2_multistart_stage1.csv", "q2_basin_stage1.csv"),
        ("q2_multistart_refined.csv", "q2_basin_refined.csv"),
        ("q2_multistart_summary.csv", "q2_basin_summary.csv"),
    ):
        export_existing_csv(diagnostic_tables / source_name, output / output_name, records, project)


def q3_tables(
    project: Path, diagnostic: dict[str, object], frozen: dict[str, object],
    records: list[dict[str, object]],
) -> None:
    output = project / "modules/40_q3/figures/editable/origin_data/csv"
    fits = {
        10.0: standardize_q3_fit(project / "modules/40_q3/tables/q3_si_10deg_paper_a.csv", 10.0),
        15.0: standardize_q3_fit(project / "modules/40_q3/tables/q3_si_15deg_paper_a.csv", 15.0),
    }
    for angle, frame in fits.items():
        write_csv(frame, output / f"q3_fit_{int(angle)}deg.csv", records, project)

    summary_rows = []
    for index, angle in enumerate((10.0, 15.0)):
        row = diagnostic["si_angle_results"][index]
        frozen_row = frozen["si_angle_results"][index]
        summary_rows.append({
            "result_type": "independent_airy_fit",
            "angle_deg": angle,
            "thickness_um": frozen_row["parameters"]["thickness_um"],
            "rmse_fraction": row["metrics"]["rmse_fraction"],
            "rmse_percentage_point": row["metrics"]["rmse_percentage_point"],
            "r2": row["metrics"]["r2"],
            "log10N_cm3": row["parameters"]["log10_carrier_cm3"],
            "log10Gamma_s1": row["parameters"]["log10_collision_s-1"],
            "n3": row["parameters"]["substrate_index"],
            "boundary_hits": ";".join(row["boundary_hits"]),
            "jacobian_condition_number": row["jacobian_condition_number"],
            "jacobian_sigma_min": row["jacobian_sigma_min"],
        })
    summary_rows.append({
        "result_type": "arithmetic_mean",
        "angle_deg": np.nan,
        "thickness_um": frozen["si_primary_result"]["thickness_um"],
    })
    summary = pd.DataFrame(summary_rows)
    write_csv(summary, output / "q3_summary.csv", records, project)

    multistart_rows = []
    for angle_index, angle in enumerate((10.0, 15.0)):
        for row in diagnostic["si_angle_results"][angle_index]["multistart"]:
            initial = row["initial"]
            final = row["parameters"]
            multistart_rows.append({
                "angle_deg": angle,
                "seed_id": row["seed_id"],
                "d_init_um": initial["thickness_um"],
                "n3_init": initial["substrate_index"],
                "log10N_init_cm3": initial["log10_carrier_cm3"],
                "log10Gamma_init_s1": initial["log10_collision_s-1"],
                "d_final_um": final["thickness_um"],
                "rmse_final_percentage_point": row["rmse_percentage_point"],
                "success": row["success"],
                "boundary_hits": ";".join(row["boundary_hits"]),
            })
    multistart = pd.DataFrame(multistart_rows)
    multistart["basin_id"] = ""
    for angle in (10.0, 15.0):
        mask = multistart["angle_deg"] == angle
        multistart.loc[mask, "basin_id"] = cluster_basins(multistart.loc[mask, "d_final_um"].to_numpy())
    counts = multistart.groupby(["angle_deg", "basin_id"])["seed_id"].transform("count")
    multistart["basin_count"] = counts.astype(int)
    write_csv(multistart, output / "q3_multistart.csv", records, project)

    source = pd.read_csv(project / "modules/40_q3/tables/q3_sic_paper_a_backcheck.csv")
    blocks = []
    for angle in (10.0, 15.0):
        block = source[source["angle_deg"] == angle][["wavenumber_cm-1", "third_beam_ratio_percent"]].copy()
        block.columns = ["wavenumber_cm1", f"eta3_{int(angle)}deg_percent"]
        blocks.append(block)
    backcheck = blocks[0].merge(blocks[1], on="wavenumber_cm1", how="outer").sort_values("wavenumber_cm1")
    backcheck["engineering_threshold_percent"] = 0.1
    write_csv(backcheck, output / "q3_sic_backcheck.csv", records, project)
    write_csv(residual_boxplot(fits), output / "q3_residual_boxplot.csv", records, project)
    write_csv(residual_heatmap(fits, 1500.0, 3500.0), output / "q3_residual_heatmap.csv", records, project)

    thickness = pd.DataFrame([
        {"result_type": "10deg_airy", "thickness_um": Q3_TARGET[0], "role": "frozen_result"},
        {"result_type": "15deg_airy", "thickness_um": Q3_TARGET[1], "role": "frozen_result"},
        {"result_type": "angle_mean", "thickness_um": Q3_TARGET[2], "role": "frozen_result"},
        {"result_type": "paper_a_reference", "thickness_um": 3.040, "role": "external_reference_only"},
    ])
    write_csv(thickness, output / "q3_thickness.csv", records, project)
    identifiability = summary.iloc[:2][[
        "angle_deg", "rmse_percentage_point", "jacobian_condition_number",
        "jacobian_sigma_min", "boundary_hits",
    ]].copy()
    identifiability["log10_jacobian_condition_number"] = np.log10(
        identifiability["jacobian_condition_number"].astype(float)
    )
    identifiability["boundary_hit_count"] = identifiability["boundary_hits"].map(
        lambda text: len([item for item in str(text).split(";") if item])
    )
    write_csv(identifiability, output / "q3_identifiability.csv", records, project)

    context_rows = []
    for threshold in (0.05, 0.1, 0.2):
        for angle, frame in fits.items():
            maximum = float(frame["eta3_percent"].max())
            context_rows.append({
                "angle_deg": angle,
                "engineering_threshold_percent": threshold,
                "eta3_max_percent": maximum,
                "eta3_to_threshold_ratio": maximum / threshold,
                "usage": "engineering_context_only",
            })
    write_csv(pd.DataFrame(context_rows), output / "q3_threshold_context.csv", records, project)
    validation = pd.DataFrame([
        {"metric": "angle_difference_um", "value": abs(Q3_TARGET[0] - Q3_TARGET[1]), "unit": "um"},
        {"metric": "half_range_um", "value": abs(Q3_TARGET[0] - Q3_TARGET[1]) / 2.0, "unit": "um"},
        {
            "metric": "mean_vs_paper_a_percent",
            "value": frozen["si_primary_result"]["relative_distance_to_paper_a_percent"],
            "unit": "percent",
        },
    ])
    write_csv(validation, output / "q3_validation_comparison.csv", records, project)
    diagnostic_tables = project / "modules/40_q3/tables"
    for source_name, output_name in (
        ("q3_identifiability_summary.csv", "q3_identifiability_summary_detailed.csv"),
        ("q3_identifiability_parameters.csv", "q3_identifiability_parameters.csv"),
        ("q3_identifiability_correlation.csv", "q3_identifiability_correlation.csv"),
        ("q3_multistart.csv", "q3_multistart_diagnostics.csv"),
        ("q3_extended_jacobian_summary.csv", "q3_extended_jacobian_summary.csv"),
        ("q3_extended_jacobian_parameters.csv", "q3_extended_jacobian_parameters.csv"),
    ):
        export_existing_csv(diagnostic_tables / source_name, output / output_name, records, project)


def validate_results(
    q2_diagnostic: dict[str, object], q3_diagnostic: dict[str, object],
    q2_frozen: dict[str, object], q3_frozen: dict[str, object],
) -> None:
    q2_values = np.array([
        q2_diagnostic["angle_results"][0]["thickness_um"],
        q2_diagnostic["angle_results"][1]["thickness_um"],
        q2_diagnostic["primary_result"]["thickness_um"],
    ])
    q3_values = np.array([
        q3_diagnostic["si_angle_results"][0]["parameters"]["thickness_um"],
        q3_diagnostic["si_angle_results"][1]["parameters"]["thickness_um"],
        q3_diagnostic["si_primary_result"]["thickness_um"],
    ])
    if np.max(np.abs(q2_values - Q2_TARGET)) > 1.0e-6:
        raise ValueError(f"Q2 recomputation drifted from frozen results: {q2_values}")
    if np.max(np.abs(q3_values - Q3_TARGET)) > 1.0e-6:
        raise ValueError(f"Q3 recomputation drifted from frozen results: {q3_values}")
    if q2_frozen["status"] != "FROZEN" or q3_frozen["status"] != "FROZEN":
        raise ValueError("Official Q2/Q3 results are not frozen")
    if q3_frozen["formal_model"] != "Airy":
        raise ValueError("Q3 formal model must remain Airy")
    if q2_frozen["primary_result"]["rule"] != "arithmetic_mean_of_independent_10deg_and_15deg_fits":
        raise ValueError("Q2 route must remain independent fits followed by an arithmetic mean")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--q2-diagnostics", type=Path, required=True)
    parser.add_argument("--q3-diagnostics", type=Path, required=True)
    parser.add_argument("--q2-frozen", type=Path)
    parser.add_argument("--q3-frozen", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    q2_frozen_path = (args.q2_frozen or project / "output/results/q2_paper_a_results.json").resolve()
    q3_frozen_path = (args.q3_frozen or project / "output/results/q3_paper_a_results.json").resolve()
    q2_diagnostic = load_json(args.q2_diagnostics.resolve())
    q3_diagnostic = load_json(args.q3_diagnostics.resolve())
    q2_frozen = load_json(q2_frozen_path)
    q3_frozen = load_json(q3_frozen_path)
    validate_results(q2_diagnostic, q3_diagnostic, q2_frozen, q3_frozen)

    records: list[dict[str, object]] = []
    q2_tables(project, args.data_dir.resolve(), q2_diagnostic, q2_frozen, records)
    q3_tables(project, q3_diagnostic, q3_frozen, records)
    manifest = {
        "schema_version": "origin_data.paper_a.v1",
        "routes": {
            "q2": "independent angle fits followed by arithmetic mean",
            "q3": "Airy independent angle fits; double beam is same-parameter comparison only",
        },
        "frozen_values_um": {
            "q2": Q2_TARGET.tolist(),
            "q3": Q3_TARGET.tolist(),
        },
        "sources": {
            "q2_frozen_sha256": sha256(q2_frozen_path),
            "q3_frozen_sha256": sha256(q3_frozen_path),
            "attachments": {
                f"attachment_{number}": sha256(args.data_dir.resolve() / f"附件{number}.xlsx")
                for number in (1, 2, 3, 4)
            },
        },
        "files": records,
    }
    manifest_paths = [
        project / "modules/30_q2/figures/editable/origin_data/manifest.json",
        project / "modules/40_q3/figures/editable/origin_data/manifest.json",
    ]
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    lowered = manifest_text.lower()
    for banned in BANNED_TEXT:
        if banned.lower() in lowered:
            raise ValueError(f"Banned legacy route text found: {banned}")
    for path in manifest_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(manifest_text, encoding="utf-8")
    print(json.dumps({"status": "PASS", "csv_files": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

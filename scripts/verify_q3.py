"""Fail-closed numerical and file-consistency checks for Q3."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    sys.path.insert(0, str(project / "modules/40_q3/code"))
    from solve_q3 import PARAMETER_NAMES, layer_components

    result_path = project / "output/results/q3_analysis_results.json"
    data = json.loads(result_path.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, evidence: object) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})

    si = data["Si"]
    validation = data["validation"]
    maximum = max(row["third_beam_ratio_max_percent"] for row in si["criterion"])
    expected = "airy" if maximum >= data["metadata"]["threshold_percent"] else "double"
    selected_fits = si["single_angle_airy"] if expected == "airy" else si["single_angle_double"]
    mean_d = float(np.mean([fit["parameters"]["d_um"] for fit in selected_fits]))

    check("problem_label_after_ab_exchange", data["metadata"]["competition_problem"] == "CUMCM-2025-A", data["metadata"])
    check("si_criterion_uses_full_band", all(row["band_cm-1"] == [1500.0, 3500.0] for row in si["criterion"]), si["criterion"])
    check("criterion_controls_model_branch", si["selected_model"] == expected, {"maximum_percent": maximum, "expected": expected, "actual": si["selected_model"]})
    check("main_thickness_is_selected_angle_mean", abs(si["main_thickness_um"] - mean_d) < 1.0e-10, {"registered": si["main_thickness_um"], "recomputed": mean_d})
    check("threshold_sensitivity_stable", len({row["selected_model"] for row in validation["threshold_sensitivity"]}) == 1, validation["threshold_sensitivity"])
    check("angle_and_joint_consistency", validation["thickness_consistency_pass"], validation)
    check("solvers_converged", validation["all_solvers_success"], validation)
    check("unidentifiable_nuisance_not_interpreted", not validation["nuisance_parameters_interpretable"], [fit["diagnostics"] for fit in selected_fits])
    check("sic_reads_frozen_q2", abs(data["SiC"]["q2_frozen_thickness_um"] - 7.384039253397902) < 5.0e-7 and data["SiC"]["retain_q2_result"], data["SiC"])
    check("forbidden_old_selectors_absent", data["metadata"]["model_exclusions"] == ["finite_order_Neumann", "AIC", "angle_gain", "angle_bias"], data["metadata"]["model_exclusions"])

    # Formula-code-unit-scaling quartet for the locked real-angle propagation.
    sigma = np.array([1500.0, 2500.0, 3500.0])
    film = np.full(3, 3.45 - 2.0e-4j)
    substrate = np.full(3, 3.50 + 0j)
    p1 = layer_components(sigma, 10.0, 3.0, film, substrate)["s"]["loop"]
    p2 = layer_components(sigma, 10.0, 4.0, film, substrate)["s"]["loop"]
    theta = np.arcsin(1.0003 * np.sin(np.deg2rad(10.0)) / np.real(film))
    q = film * np.cos(theta)
    expected_phase = np.exp(-4j * np.pi * 1.0e-4 * sigma * q)
    phase_error = float(np.max(np.abs(p2 / p1 - expected_phase)))
    check("formula_code_unit_scaling_quartet", phase_error < 1.0e-10, {"formula": "exp(-i*4*pi*sigma*d_um*1e-4*n*cos(theta))", "unit": "d_cm=d_um*1e-4", "max_error": phase_error})

    required = [
        project / "modules/40_q3/tables/q3_si_model_comparison.csv",
        project / "modules/40_q3/tables/q3_third_beam_criterion.csv",
        project / "modules/40_q3/tables/q3_si_results.csv",
        project / "modules/40_q3/figures/q3_si_model_comparison.png",
        project / "modules/40_q3/figures/q3_third_beam_criterion.png",
        project / "modules/40_q3/figures/q3_thickness_consistency.png",
        project / "modules/40_q3/figures/q3_algorithm_flow.pdf",
    ]
    check("registered_outputs_exist", all(path.exists() and path.stat().st_size > 100 for path in required), [str(path) for path in required])
    report = {
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "q3_results_sha256": sha256(result_path),
        "selected_model": si["selected_model"],
        "main_thickness_um": si["main_thickness_um"],
        "checks": checks,
    }
    report_path = project / "reports/q3_verification.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()

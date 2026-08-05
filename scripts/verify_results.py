"""Fail-closed checks for formula-code-unit-scaling and output consistency."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from shared.code.materials import background_index, drude_substrate_permittivity
from shared.code.optics import layer_amplitudes, reflected_amplitude, unpolarized_reflectance


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project
    result_path = project / "output" / "results" / "analysis_results.json"
    data = json.loads(result_path.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, condition: bool, evidence: object) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})

    q2 = data["Q2"]["main"]
    si_d = data["Q3"]["Si"]["Airy"]
    si_1 = data["Q3"]["Si"]["double"]
    check("official_full_run", data["run"]["mode"] == "full", data["run"])
    check("q2_three_seed_agreement", np.ptp([x["thickness_um"] for x in data["Q2"]["multistart"]]) < 2e-6, data["Q2"]["multistart"])
    check("q2_bootstrap_contains_main", data["Q2"]["block_bootstrap"]["quantile_2.5_50_97.5_um"][0] < q2["thickness_um"] < data["Q2"]["block_bootstrap"]["quantile_2.5_50_97.5_um"][2], data["Q2"]["block_bootstrap"])
    reduction = 100.0 * (si_1["rmse_percentage_point"] - si_d["rmse_percentage_point"]) / si_1["rmse_percentage_point"]
    check("si_multibeam_rmse_reduction", reduction > 60.0, reduction)
    convergence = np.asarray(data["Q3"]["Si"]["order_convergence"], dtype=float)
    check("si_six_beam_convergence", abs(convergence[-2, 1] - convergence[-1, 1]) < 1e-4 and abs(convergence[-2, 2] - convergence[-1, 2]) < 1e-3, convergence[-2:].tolist())
    check("sic_multibeam_negligible", abs(data["Q3"]["SiC"]["delta_d_Airy_minus_double_um"]) < 1e-3 and data["Q3"]["SiC"]["loop"]["rho_intensity_max"] < 1e-3, data["Q3"]["SiC"])

    # Formula-code-unit-scaling quartet: a 1 um increase must add the phase
    # 4*pi*sigma*q*1e-4; the same forward operator is evaluated directly.
    sigma = np.array([1500.0, 2500.0, 3500.0])
    n = background_index("sic", sigma)
    eps = drude_substrate_permittivity("sic", sigma, 1000.0, 560.0, 1.0)
    p1 = layer_amplitudes(sigma, 10.0, 7.0, n, eps)["s"]["loop"]
    p2 = layer_amplitudes(sigma, 10.0, 8.0, n, eps)["s"]["loop"]
    q = np.sqrt(n**2 - np.sin(np.deg2rad(10.0))**2 + 0j)
    expected = np.exp(4j * np.pi * sigma * q * 1e-4)
    check("formula_code_unit_scaling_quartet", float(np.max(np.abs(p2 / p1 - expected))) < 1e-10, {"formula": "exp(4*pi*i*sigma*d_cm*q)", "code": "optics.layer_amplitudes", "unit": "d_cm=d_um*1e-4", "max_error": float(np.max(np.abs(p2 / p1 - expected)))})

    required = [
        project / "modules" / "30_q2" / "tables" / "q2_block_bootstrap.csv",
        project / "modules" / "40_q3" / "tables" / "q3_si_order_convergence.csv",
        project / "modules" / "30_q2" / "figures" / "q2_sic_joint_fit.png",
        project / "modules" / "40_q3" / "figures" / "q3_si_model_comparison.png",
    ]
    check("registered_outputs_exist", all(p.exists() and p.stat().st_size > 100 for p in required), [str(p) for p in required])
    report = {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "analysis_results_sha256": sha256(result_path),
        "rmse_reduction_si_percent": reduction,
        "checks": checks,
    }
    report_path = project / "reports" / "numerical_verification.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()

"""Fail-closed verification for the active PAPER_A result chain."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = {
        "q1": ROOT / "output/results/q1_validation.json",
        "q2": ROOT / "output/results/q2_paper_a_results.json",
        "q3": ROOT / "output/results/q3_paper_a_results.json",
    }
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}
    hashes = {name: digest(path) for name, path in paths.items()}

    q3_mean = data["q3"]["si_primary_result"]["thickness_um"]
    checks = {
        "q1_frozen": data["q1"]["status"] == "FROZEN" and all(data["q1"]["checks"].values()),
        "q2_frozen": data["q2"]["status"] == "FROZEN",
        "q2_value": abs(data["q2"]["primary_result"]["thickness_um"] - 7.739796617935274) < 1.0e-10,
        "q2_angle_r2": all(row["metrics"]["r2"] > 0.95 for row in data["q2"]["angle_results"]),
        "q3_value": abs(q3_mean - 3.217455302969201) < 1.0e-10,
        "q3_physics": (
            data["q3"]["formal_model"] == "Airy"
            and abs(data["q3"]["fixed_material_parameters"]["air_refractive_index"] - 1.0003) < 1.0e-12
            and all(row["propagation_max_abs"] <= 1.0 + 1.0e-12 for row in data["q3"]["si_angle_results"])
        ),
        "q3_q2_hash": data["q3"]["q2_dependency"]["sha256"] == hashes["q2"],
        "q3_sic_backcheck": (
            data["q3"]["sic_backcheck"]["retain_q2_result"]
            and abs(data["q3"]["sic_backcheck"]["q2_thickness_um"] - data["q2"]["primary_result"]["thickness_um"]) < 1.0e-12
        ),
        "q3_frozen_with_disclosed_exception": (
            data["q3"]["status"] == "FROZEN"
            and not data["q3"]["si_primary_result"]["five_percent_numerical_gate_pass"]
            and data["q3"]["si_primary_result"]["user_accepted_exception"]
        ),
        "old_active_result_removed": not (ROOT / "output/results/analysis_results.json").exists(),
    }

    registry_path = ROOT / "work/result_registry.csv"
    registry_rows = list(csv.DictReader(registry_path.open(encoding="utf-8", newline="")))
    expected_files = {
        "q1": "output/results/q1_validation.json",
        "q2": "output/results/q2_paper_a_results.json",
        "q3": "output/results/q3_paper_a_results.json",
    }
    for label, expected_hash in hashes.items():
        prefix = expected_files[label] + "#sha256="
        relevant = [
            row for row in registry_rows
            if row["status"] != "STALE" and row["source_output"].startswith(prefix)
        ]
        checks[f"registry_{label}_hash"] = bool(relevant) and all(
            row["source_output"] == prefix + expected_hash for row in relevant
        )

    report = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "hashes": hashes}
    output = ROOT / "reports/paper_a_verification.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if report["status"] != "PASS":
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
    print("PAPER_A result-chain verification PASS; Q1-Q3 results are frozen")


if __name__ == "__main__":
    main()

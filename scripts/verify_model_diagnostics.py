"""Verify the reproducible Q2/Q3 diagnostic data against frozen PAPER_A results."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def f(row, key):
    return float(row[key])


q2 = json.loads((ROOT / "output/results/q2_paper_a_results.json").read_text(encoding="utf-8"))
q2s = rows(ROOT / "modules/30_q2/tables/q2_multistart_summary.csv")
assert len(q2s) == 2
for summary, frozen in zip(q2s, q2["angle_results"]):
    assert abs(f(summary, "best_thickness_um") - float(frozen["thickness_um"])) < 5e-6
    assert f(summary, "second_best_rmse") > f(summary, "best_rmse")
assert abs(sum(f(row, "best_thickness_um") for row in q2s) / 2 - q2["primary_result"]["thickness_um"]) < 5e-6

q3 = json.loads((ROOT / "output/results/q3_paper_a_results.json").read_text(encoding="utf-8"))
q3s = rows(ROOT / "modules/40_q3/tables/q3_identifiability_summary.csv")
q3p = rows(ROOT / "modules/40_q3/tables/q3_identifiability_parameters.csv")
exts = rows(ROOT / "modules/40_q3/tables/q3_extended_jacobian_summary.csv")
assert len(q3s) == 2 and len(exts) == 2
for summary, frozen in zip(q3s, q3["si_angle_results"]):
    assert abs(f(summary, "thickness_um") - float(frozen["parameters"]["thickness_um"])) < 5e-5
for angle in ("10.0", "15.0"):
    p = [row for row in q3p if row["angle_deg"] == angle]
    sensitivity = {row["parameter"]: f(row, "relative_sensitivity") for row in p}
    assert sensitivity["thickness_um"] > sensitivity["log10_carrier_cm3"]
    assert sensitivity["thickness_um"] > sensitivity["log10_collision_s-1"]
    base = next(row for row in q3s if row["angle_deg"] == angle)
    ext = next(row for row in exts if row["angle_deg"] == angle)
    assert f(ext, "condition_column_normalized") > f(base, "jacobian_cond_column_normalized")

assert 3.21 < q3["si_primary_result"]["thickness_um"] < 3.23
print("MODEL DIAGNOSTICS verification PASS")

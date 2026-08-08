"""Fail-closed checks for active prose, citations, figure evidence and float control."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTION_FILES = [
    ROOT / "modules/20_q1/paper/q1.tex",
    ROOT / "modules/30_q2/paper/q2.tex",
    ROOT / "modules/40_q3/paper/q3.tex",
]
RESTATEMENT = ROOT / "modules/10_restatement/paper/restatement.tex"
REFERENCES = ROOT / "modules/60_references/paper/references.tex"
ACTIVE_TEX = QUESTION_FILES + [
    ROOT / "modules/00_abstract/paper/abstract.tex",
    ROOT / "modules/50_evaluation/paper/evaluation.tex",
]
TEMPLATE_PHRASES = [
    "主模型统一使用", "该方法仅用于", "进一步提升了模型的稳定性",
    "为后续研究提供了", "形成完整证据链", "保证模型的科学性与可靠性",
    "从而实现", "不仅", "综合上述分析",
]
STALE_MARKERS = ["7.3840", "3.3960", "3.2178", "双角度共享参数复反射率联合反演"]


def main() -> None:
    checks: dict[str, bool] = {}
    joined = "\n".join(path.read_text(encoding="utf-8") for path in ACTIVE_TEX)
    checks["no_repeated_ai_templates"] = all(joined.count(p) <= 1 for p in TEMPLATE_PHRASES)
    checks["no_stale_primary_results"] = all(marker not in joined for marker in STALE_MARKERS)
    checks["named_model_sections"] = all(
        "\\subsection{模型建立}" not in path.read_text(encoding="utf-8")
        for path in QUESTION_FILES
    )
    checks["no_forced_H_in_questions"] = all("[H]" not in path.read_text(encoding="utf-8") for path in QUESTION_FILES)
    checks["float_barrier_per_question"] = all("\\FloatBarrier" in path.read_text(encoding="utf-8") for path in QUESTION_FILES)

    bibliography = REFERENCES.read_text(encoding="utf-8")
    bib_labels = set(re.findall(r"\\bibitem\{([^}]+)\}", bibliography))
    citation_text = "\n".join(
        path.read_text(encoding="utf-8") for path in QUESTION_FILES + [RESTATEMENT]
    )
    cited_labels: set[str] = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", citation_text):
        cited_labels.update(label.strip() for label in group.split(",") if label.strip())
    checks["all_references_cited"] = bool(bib_labels) and bib_labels <= cited_labels
    checks["no_unknown_citations"] = cited_labels <= bib_labels

    registry_path = ROOT / "work/figure_registry.csv"
    rows = list(csv.DictReader(registry_path.open(encoding="utf-8", newline="")))
    required = {"question_answered_zh", "data_source", "first_reference_location"}
    checks["figure_registry_required_fields"] = bool(rows) and all(all(row[key].strip() for key in required) for row in rows)

    paths_ok = True
    for row in rows:
        for field in ("file_path", "data_source"):
            for item in row[field].split("|"):
                if item in {"ANALYTIC_GEOMETRY"} or item.startswith("shared/code/"):
                    continue
                if not (ROOT / item).exists():
                    paths_ok = False
    checks["figure_sources_exist"] = paths_ok

    body_figures: set[str] = set()
    include_pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{\\ProjectRoot/([^}]+)\}")
    for path in QUESTION_FILES:
        body_figures.update(include_pattern.findall(path.read_text(encoding="utf-8")))
    registered = {
        item for row in rows for item in row["file_path"].split("|") if item.strip()
    }
    checks["body_figures_registered"] = body_figures == registered

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "bibliography_labels": sorted(bib_labels),
        "cited_labels": sorted(cited_labels),
        "body_figures": sorted(body_figures),
    }
    output = ROOT / "reports/writing_quality_gate.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
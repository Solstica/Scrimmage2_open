#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final manuscript preflight for the temporary merged paper.

This script is intentionally conservative: hard failures are limited to stale
formal results, broken citations/labels and structural pagination errors.
Style/internal-word findings are warnings so that the checker does not compete
with the paper writer.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORMAL_FILES = [
    ROOT / "modules/00_abstract/paper/abstract.tex",
    ROOT / "modules/10_restatement/paper/restatement.tex",
    ROOT / "modules/11_notation/paper/notation.tex",
    ROOT / "modules/12_assumptions/paper/assumptions.tex",
    ROOT / "modules/20_q1/paper/q1.tex",
    ROOT / "modules/30_q2/paper/q2.tex",
    ROOT / "modules/40_q3/paper/q3.tex",
    ROOT / "modules/50_evaluation/paper/evaluation.tex",
    ROOT / "modules/60_references/paper/references.tex",
    ROOT / "modules/70_appendix/paper/appendix_code.tex",
    ROOT / "modules/80_ai_report/paper/ai_report.tex",
]

STALE_RESULTS = {
    "7.3840": "旧版SiC厚度",
    "7.3747": "旧版SiC Bootstrap区间",
    "7.3943": "旧版SiC Bootstrap区间",
    "3.3960": "旧版Si厚度",
    "3.2178": "旧版Si平均厚度",
    "0.000088": "旧版SiC多光束修正量",
}

INTERNAL_WORDS = {
    "PAPER_A": "开发标签",
    "冻结参数": "开发/版本口吻",
    "冻结状态": "开发/版本口吻",
    "回溯证据": "内部审稿口吻",
    "回溯检验": "内部审稿口吻",
    "模型切换判据": "内部选模口吻",
    "模型切换阈值": "内部选模口吻",
    "可靠性证据": "内部审稿口吻",
    "门禁": "工程管理口吻",
    "贴合参考": "内部对标口吻",
    "诚实重算": "内部自证口吻",
}

REFS = ROOT / "modules/60_references/paper/references.tex"
ENTRY_CANDIDATES = [ROOT / "paper/main.tex", ROOT / "paper/paper_template.tex"]
APPENDIX = ROOT / "modules/70_appendix/paper/appendix_code.tex"
Q3 = ROOT / "modules/40_q3/paper/q3.tex"
PHASE_SCRIPT = ROOT / "modules/40_q3/code/export_q3_phase_alignment.py"
PHASE_TABLE = ROOT / "modules/40_q3/tables/q3_phase_alignment.csv"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def formal_texts() -> dict[Path, str]:
    return {p: read(p) for p in FORMAL_FILES if p.exists()}


def check_stale_and_internal(texts, errors, warns):
    for path, text in texts.items():
        if path == REFS:
            continue
        for token, meaning in STALE_RESULTS.items():
            for m in re.finditer(re.escape(token), text):
                errors.append(f"{rel(path)}:{line_no(text,m.start())}: 发现{meaning} {token}")
        for token, meaning in INTERNAL_WORDS.items():
            for m in re.finditer(re.escape(token), text):
                warns.append(f"{rel(path)}:{line_no(text,m.start())}: {meaning}“{token}”")
        for pat, desc in [(r"\?\?", "未解析交叉引用??"), (r"\[\?\]", "未解析引用[?]")]:
            for m in re.finditer(pat, text):
                errors.append(f"{rel(path)}:{line_no(text,m.start())}: {desc}")


def check_citations(texts, errors):
    bib = read(REFS)
    bibkeys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cites = defaultdict(list)
    for path, text in texts.items():
        if path == REFS:
            continue
        for m in re.finditer(r"\\cite\{([^}]+)\}", text):
            for key in m.group(1).split(","):
                key = key.strip()
                if key:
                    cites[key].append((path, line_no(text, m.start())))
    missing = sorted(set(cites) - bibkeys)
    for key in missing:
        locations = ", ".join(f"{rel(p)}:{ln}" for p, ln in cites[key][:3])
        errors.append(f"引用键 {key!r} 未在参考文献中定义（{locations}）")


def check_labels(texts, errors, warns):
    labels = defaultdict(list)
    refs = defaultdict(list)
    for path, text in texts.items():
        for m in re.finditer(r"\\label\{([^}]+)\}", text):
            labels[m.group(1)].append((path, line_no(text, m.start())))
        for m in re.finditer(r"\\(?:ref|eqref)\{([^}]+)\}", text):
            refs[m.group(1)].append((path, line_no(text, m.start())))
    for key, locs in labels.items():
        if len(locs) > 1:
            where = ", ".join(f"{rel(p)}:{ln}" for p, ln in locs)
            errors.append(f"重复label {key!r}: {where}")
    for key, locs in refs.items():
        if key not in labels:
            where = ", ".join(f"{rel(p)}:{ln}" for p, ln in locs[:3])
            warns.append(f"引用了未在正式模块中发现的label {key!r}: {where}")


def active_entry() -> tuple[Path | None, str]:
    for path in ENTRY_CANDIDATES:
        if path.exists():
            return path, read(path)
    return None, ""


def check_structure(errors, warns):
    path, text = active_entry()
    if path is None:
        errors.append("找不到 paper/main.tex 或 paper/paper_template.tex")
        return
    required = ["\\pagenumbering{gobble}", "\\tableofcontents", "\\pagenumbering{arabic}", "\\setcounter{page}{1}"]
    for item in required:
        if item not in text:
            errors.append(f"{rel(path)} 缺少分页控制 {item}")
    positions = [text.find(x) for x in required]
    if all(x >= 0 for x in positions) and positions != sorted(positions):
        errors.append(f"{rel(path)} 的摘要/目录/正文页码控制顺序异常")

    markers = [
        "\\input{../modules/60_references/paper/references.tex}",
        "\\section*{附录：程序及结果文件说明}",
        "\\section*{AI使用报告}",
    ]
    for marker in markers:
        pos = text.find(marker)
        if pos < 0:
            errors.append(f"{rel(path)} 缺少结构标记：{marker}")
            continue
        prefix = text[max(0, pos - 100):pos]
        if "\\clearpage" not in prefix:
            errors.append(f"{rel(path)} 中“{marker}”前未明确另起一页（缺少\\clearpage）")

    appendix_text = read(APPENDIX)
    if re.search(r"\\subsection\*?\{", appendix_text):
        errors.append(f"{rel(APPENDIX)} 仍含二级标题；附录目录只应保留一级项")


def check_figure_width(warns, errors):
    text = read(Q3)
    # Figure 19 is already a 10°/15° two-panel PNG and must occupy 0.88 text width.
    for line_idx, line in enumerate(text.splitlines(), start=1):
        if "19_Si参数可辨识性气泡图" in line and "includegraphics" in line:
            if re.search(r"width\s*=\s*\.?(?:88|0\.88)\\textwidth", line):
                return
            errors.append(f"{rel(Q3)}:{line_idx}: 双面板可辨识性图应为0.88\\textwidth")
            return
    warns.append("未在Q3正文中定位到“19_Si参数可辨识性气泡图”的includegraphics行")


def run_existing_writing_checker(infos, warns):
    checker = ROOT / "scripts/check_writing_quality.py"
    if not checker.exists():
        return
    proc = subprocess.run([sys.executable, str(checker)], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        infos.append("现有写作/图表登记检查通过")
    else:
        tail = "\n".join((proc.stdout + "\n" + proc.stderr).strip().splitlines()[-10:])
        warns.append("现有 check_writing_quality.py 未通过：\n" + tail)


def run_phase_diagnostic(infos, warns):
    if not PHASE_SCRIPT.exists():
        warns.append("未找到Q3峰谷位置诊断脚本")
        return
    try:
        proc = subprocess.run([sys.executable, str(PHASE_SCRIPT)], cwd=ROOT, text=True, capture_output=True, timeout=90)
    except Exception as exc:
        warns.append(f"Q3峰谷位置诊断未执行：{exc}")
        return
    if proc.returncode != 0:
        last = "\n".join((proc.stdout + "\n" + proc.stderr).strip().splitlines()[-6:])
        warns.append("Q3峰谷位置诊断未成功（不作为预检失败）：\n" + last)
        return
    if not PHASE_TABLE.exists():
        warns.append("Q3峰谷位置诊断脚本运行后未生成结果表")
        return
    rows = list(csv.DictReader(PHASE_TABLE.open(encoding="utf-8-sig")))
    if not rows:
        warns.append("Q3峰谷位置诊断结果表为空")
        return
    infos.append("Q3峰谷/相位位置诊断（仅诊断，不改变拟合参数）：")
    for row in rows:
        infos.append(
            "  {angle} {kind}: matched={n_matched}, MAE={mae_cm1} cm^-1, max={max_abs_cm1} cm^-1".format(**row)
        )


def check_build_log(errors, warns, infos):
    log = ROOT / "paper/main.log"
    if log.exists():
        text = read(log)
        patterns = [
            (r"Citation [`']?[^\n]+ undefined", "LaTeX存在未定义引用"),
            (r"Reference [`']?[^\n]+ undefined", "LaTeX存在未定义交叉引用"),
            (r"There were undefined references", "LaTeX报告未定义引用"),
        ]
        for pat, desc in patterns:
            if re.search(pat, text, flags=re.I):
                errors.append(desc + "（见 paper/main.log）")
        if "Overfull \\hbox" in text:
            warns.append("paper/main.log 存在 Overfull \\hbox，请目视检查对应页面")

    toc = ROOT / "paper/main.toc"
    if toc.exists():
        text = read(toc)
        def page_of(label: str):
            for line in text.splitlines():
                if label in line:
                    m = re.search(r"\}\{(\d+)\}\{", line)
                    if m:
                        return int(m.group(1))
            return None
        ref_page = page_of("参考文献")
        appendix_page = page_of("附录：程序及结果文件说明")
        ai_page = page_of("AI使用报告")
        if ref_page is not None:
            body_pages = ref_page - 1
            infos.append(f"目录记录：参考文献始于正文页码 {ref_page}，参考文献前正文约 {body_pages} 页")
            if body_pages > 27:
                warns.append(f"正文约 {body_pages} 页，超过当前27页目标")
        if None not in (ref_page, appendix_page, ai_page):
            if not (ref_page < appendix_page < ai_page):
                errors.append("参考文献、附录、AI使用报告未分别落在后续独立页面")
            else:
                infos.append(f"后置章节分页：参考文献p.{ref_page} → 附录p.{appendix_page} → AI报告p.{ai_page}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-build", action="store_true", help="also inspect main.log/main.toc")
    parser.add_argument("--skip-phase", action="store_true", help="do not run optional Q3 peak/trough diagnostic")
    args = parser.parse_args()

    errors, warns, infos = [], [], []
    texts = formal_texts()
    check_stale_and_internal(texts, errors, warns)
    check_citations(texts, errors)
    check_labels(texts, errors, warns)
    check_structure(errors, warns)
    check_figure_width(warns, errors)
    run_existing_writing_checker(infos, warns)
    if not args.skip_phase:
        run_phase_diagnostic(infos, warns)
    if args.post_build:
        check_build_log(errors, warns, infos)

    print("\n========== FINAL PREFLIGHT ==========")
    for item in infos:
        print("[INFO]", item)
    for item in warns:
        print("[WARN]", item)
    for item in errors:
        print("[FAIL]", item)
    print(f"summary: {len(errors)} fail / {len(warns)} warn / {len(infos)} info")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

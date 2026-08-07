#!/usr/bin/env python3
"""
Lightweight repository structure guard for CUCCM2026 run_02.

Purpose:
- Keep main protected by PR.
- Prevent accidental creation of a second repository/paper structure.
- Do NOT police normal edits inside existing modules.

Typical GitHub Actions usage:
    python scripts/structure_guard.py --base <base_sha> --head <head_sha>

Local usage:
    python scripts/structure_guard.py --base origin/main --head HEAD
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import PurePosixPath

# ---------------------------------------------------------------------------
# Intentionally small, explicit policy.
# If the team genuinely needs a new top-level directory/module later,
# the captain updates this list in one reviewed commit.
# ---------------------------------------------------------------------------

ALLOWED_ROOT_DIRS = {
    ".github",
    "code",
    "docs",
    "fix",
    "modules",
    "output",
    "paper",
    "reports",
    "scripts",
    "shared",
    "training",
    "work",
}

ALLOWED_MODULE_DIRS = {
    "00_abstract",
    "10_restatement",
    "11_notation",
    "12_assumptions",
    "20_q1",
    "30_q2",
    "40_q3",
    "50_evaluation",
    "60_references",
    "70_appendix",
    "80_ai_report",
}

# Names that historically caused a second "full paper" source tree.
# Matching is case-insensitive for ASCII names.
FORBIDDEN_DIR_NAMES = {
    "paper汇总",
    "论文汇总",
    "总论文",
    "论文总稿",
    "最终论文",
    "final_paper",
    "paper_final",
    "full_paper",
    "finalpaper",
}

FORBIDDEN_TEX_BASENAMES = {
    "document.tex",
    "document2.tex",
    "final.tex",
    "final_paper.tex",
    "paper_final.tex",
    "full_paper.tex",
    "总论文.tex",
    "论文总稿.tex",
    "论文汇总.tex",
    "最终论文.tex",
    "最终版.tex",
}

# These must still exist in the PR head.
REQUIRED_CANONICAL_SOURCES = {
    "paper/main.tex",
    "modules/00_abstract/paper/abstract.tex",
    "modules/10_restatement/paper/restatement.tex",
    "modules/11_notation/paper/notation.tex",
    "modules/12_assumptions/paper/assumptions.tex",
    "modules/20_q1/paper/q1.tex",
    "modules/30_q2/paper/q2.tex",
    "modules/40_q3/paper/q3.tex",
    "modules/50_evaluation/paper/evaluation.tex",
    "modules/60_references/paper/references.tex",
    "modules/70_appendix/paper/appendix_code.tex",
    "modules/80_ai_report/paper/ai_report.tex",
}

# Historical material may legitimately contain old directory/file names.
# New work under archive is not treated as active structure.
ARCHIVE_PREFIXES = (
    "work/archive/",
    "work/legacy/",
)


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def is_archive(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ARCHIVE_PREFIXES)


def parse_changed_paths(base: str, head: str):
    """
    Return list of (status, destination_path).

    For renames/copies, only the destination path is checked for creation
    of forbidden active structure.
    """
    raw = git(
        "diff",
        "--name-status",
        "-z",
        "--find-renames",
        "--find-copies",
        f"{base}...{head}",
    )
    fields = raw.split("\0")
    out = []
    i = 0
    while i < len(fields):
        if not fields[i]:
            break
        status = fields[i]
        i += 1

        if status.startswith(("R", "C")):
            if i + 1 >= len(fields):
                break
            _old = normalize(fields[i])
            new = normalize(fields[i + 1])
            i += 2
            out.append((status, new))
        else:
            if i >= len(fields):
                break
            path = normalize(fields[i])
            i += 1
            out.append((status, path))
    return out


def head_tree_paths(head: str) -> set[str]:
    raw = git("ls-tree", "-r", "--name-only", "-z", head)
    return {normalize(p) for p in raw.split("\0") if p}


def check_changed_path(status: str, path: str) -> list[str]:
    errors: list[str] = []

    # Deletions do not create a new structure. Required-file deletion is
    # caught separately by REQUIRED_CANONICAL_SOURCES.
    if status.startswith("D"):
        return errors

    if is_archive(path):
        return errors

    p = PurePosixPath(path)
    parts = p.parts
    if not parts:
        return errors

    # 1) No unknown root directory.
    if len(parts) >= 2:
        root = parts[0]
        if root not in ALLOWED_ROOT_DIRS:
            errors.append(
                f"新增/修改了未授权的仓库一级目录：{root}/  （文件：{path}）"
            )

    # 2) modules/ may only contain canonical module directories.
    if len(parts) >= 2 and parts[0] == "modules":
        module = parts[1]
        if len(parts) >= 3 and module not in ALLOWED_MODULE_DIRS:
            errors.append(
                f"modules/ 下出现未授权一级模块目录：modules/{module}/  （文件：{path}）"
            )

        # New/modified TeX directly under modules/ is almost certainly a
        # second aggregate source such as modules/q1_q2.tex.
        if len(parts) == 2 and p.suffix.lower() == ".tex":
            errors.append(
                f"禁止在 modules/ 根部新增或修改汇总 TeX：{path}"
            )

    # 3) No second "full paper" directory anywhere in active tree.
    for part in parts[:-1]:
        if part.lower() in {x.lower() for x in FORBIDDEN_DIR_NAMES}:
            errors.append(
                f"禁止创建/继续使用第二套全文目录：{path}"
            )
            break

    # 4) No suspicious new aggregate TeX source.
    basename = p.name.lower()
    forbidden_files = {x.lower() for x in FORBIDDEN_TEX_BASENAMES}
    if basename in forbidden_files:
        errors.append(
            f"禁止新增/修改第二套全文入口：{path}；全文唯一入口是 paper/main.tex"
        )

    # Any TeX at repository root is also forbidden; active TeX belongs in
    # paper/ or modules/<module>/.
    if len(parts) == 1 and p.suffix.lower() == ".tex":
        errors.append(
            f"禁止在仓库根目录新增/修改 TeX 入口：{path}"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="PR base SHA/ref")
    parser.add_argument("--head", required=True, help="PR head SHA/ref")
    args = parser.parse_args()

    # Make sure both refs are usable.
    git("cat-file", "-e", f"{args.base}^{{commit}}")
    git("cat-file", "-e", f"{args.head}^{{commit}}")

    changed = parse_changed_paths(args.base, args.head)
    errors: list[str] = []

    for status, path in changed:
        errors.extend(check_changed_path(status, path))

    # 5) Canonical source files must not disappear.
    tree = head_tree_paths(args.head)
    for required in sorted(REQUIRED_CANONICAL_SOURCES):
        if required not in tree:
            errors.append(
                f"关键 canonical source 缺失：{required}"
            )

    if errors:
        print("\nSTRUCTURE GUARD FAILED\n")
        for idx, err in enumerate(dict.fromkeys(errors), start=1):
            print(f"{idx}. {err}")
        print(
            "\n本检查只锁工程骨架；正常修改已有模块内部文件不受限制。\n"
            "如果确实需要新增一级目录/模块，请先由队长更新 "
            "scripts/structure_guard.py 中的允许列表。"
        )
        return 1

    print("STRUCTURE GUARD PASS")
    print(f"Checked {len(changed)} changed path(s): {args.base}...{args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

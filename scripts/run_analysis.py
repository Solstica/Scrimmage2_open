"""Run only the active PAPER_A Q1 validation and Q2 reproduction."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    subprocess.run([sys.executable, str(project / "scripts" / "validate_q1_paper_a.py")], cwd=project, check=True)
    subprocess.run([
        sys.executable, str(project / "modules" / "30_q2" / "code" / "solve_q2_paper_a.py"),
        "--data-dir", str(args.data_dir.resolve()), "--project", str(project),
    ], cwd=project, check=True)
    print("Active Q1-Q2 PAPER_A pipeline PASS. Run solve_q3_paper_a.py separately after Q2 freezes.")


if __name__ == "__main__":
    main()

"""Regenerate only route-level PAPER_A diagrams; solvers own result figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def flow(path: Path, title: str, labels: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(10, 2.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    centers = np.linspace(0.12, 0.88, len(labels))
    colors = ["#FCE8D5", "#DCEAF7", "#E1F2E5", "#E9E1F2"]
    for index, (x, label) in enumerate(zip(centers, labels)):
        box = patches.FancyBboxPatch(
            (x - 0.095, 0.33), 0.19, 0.34, boxstyle="round,pad=0.015",
            fc=colors[index % len(colors)], ec="#4c5b66", lw=1.3,
        )
        ax.add_patch(box)
        ax.text(x, 0.50, label, ha="center", va="center", fontsize=10)
        if index < len(labels) - 1:
            ax.annotate("", xy=(centers[index + 1] - 0.105, 0.50), xytext=(x + 0.105, 0.50), arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "#2F75B5"})
    ax.text(0.5, 0.88, title, ha="center", va="center", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    q1 = ROOT / "modules" / "20_q1" / "figures"
    q1.mkdir(parents=True, exist_ok=True)
    flow(q1 / "q1_model_flow.pdf", "Q1: PAPER_A double-beam model", [
        "Sellmeier--Drude\ndispersion", "Real-angle signed\ns/p Fresnel terms",
        "Surface plus first\ninternal reflection", "Unpolarized\nreflectance",
    ])


if __name__ == "__main__":
    main()

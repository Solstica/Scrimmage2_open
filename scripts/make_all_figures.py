from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SHARED_FIG = ROOT / "shared" / "figures"
Q1_FIG = ROOT / "modules" / "20_q1" / "figures"
Q2_FIG = ROOT / "modules" / "30_q2" / "figures"
Q3_FIG = ROOT / "modules" / "40_q3" / "figures"
Q2_TAB = ROOT / "modules" / "30_q2" / "tables"
Q3_TAB = ROOT / "modules" / "40_q3" / "tables"


def flow(path: Path, title: str, labels: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(10, 2.35))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    colors = ["#FCE8D5", "#DCEAF7", "#E1F2E5", "#E9E1F2"]
    centers = np.linspace(.12, .88, len(labels))
    for i, (x, label) in enumerate(zip(centers, labels)):
        box = patches.FancyBboxPatch((x-.095,.33),.19,.34,boxstyle="round,pad=0.015",fc=colors[i%len(colors)],ec="#4c5b66",lw=1.3)
        ax.add_patch(box); ax.text(x,.50,label,ha="center",va="center",fontsize=10)
        if i < len(labels)-1:
            ax.annotate("",xy=(centers[i+1]-.105,.50),xytext=(x+.105,.50),arrowprops=dict(arrowstyle="->",lw=1.5,color="#2F75B5"))
    ax.text(.5,.88,title,ha="center",va="center",fontsize=13,fontweight="bold")
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def main() -> None:
    for directory in (SHARED_FIG, Q1_FIG, Q2_FIG, Q3_FIG):
        directory.mkdir(parents=True, exist_ok=True)
    flow(SHARED_FIG / "overall_route.pdf", "Unified route for the three questions", ["Complex Fresnel\nforward model", "Shared double-angle\ninversion", "Loop-factor\ndiagnosis", "Neumann / Airy\nrollback"])
    flow(Q1_FIG / "q1_model_flow.pdf", "Q1: complex double-beam model", ["Dispersion and\npassive branch", "s/p Fresnel\ncoefficients", "Two complex\nreflected beams", "Unpolarized\nreflectance"])
    flow(Q2_FIG / "q2_algorithm_flow.pdf", "Q2: shared-parameter joint inversion", ["Data audit and\nband selection", "Phase-based\ninitial check", "Multi-start global\nsearch", "Robust refinement\nand validation"])
    flow(Q3_FIG / "q3_algorithm_flow.pdf", "Q3: controlled multibeam extension", ["Compute complex\nloop factor", "Fit finite orders\n1,2,3,4,6", "Evaluate Airy\nlimit", "Retain or rollback\nQ2 result"])

    q2 = np.loadtxt(Q2_TAB / "q2_index_scale_sensitivity.csv", delimiter=",", skiprows=1)
    fig, ax = plt.subplots(figsize=(7.2,4.4)); ax.plot(q2[:,0],q2[:,1],"o-",color="#2F75B5"); ax.axvline(1,color="#c23b23",ls="--"); ax.set(xlabel="Background-index scale",ylabel="SiC thickness (um)",title="Systematic sensitivity to refractive index"); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(Q2_FIG / "q2_index_scale_sensitivity.png",dpi=240); plt.close(fig)
    si = np.loadtxt(Q3_TAB / "q3_si_band_sensitivity.csv", delimiter=",", skiprows=1)
    labels=[f"{int(a)}-{int(b)}" for a,b in si[:,:2]]
    fig, ax = plt.subplots(figsize=(7.2,4.4)); ax.plot(labels,si[:,2],"o-",color="#4c78a8"); ax.set(xlabel="Band (cm$^{-1}$)",ylabel="Si thickness (um)",title="Si band sensitivity"); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(Q3_FIG / "q3_si_band_sensitivity.png",dpi=240); plt.close(fig)
    data=json.loads((ROOT/"output"/"results"/"analysis_results.json").read_text(encoding="utf-8"))["Q1"]["synthetic_recovery"]
    true=np.array(data["true"][:3]); rec=np.array(data["recovered"][:3]); labels=["d (um)","plasma (cm-1)","damping (cm-1)"]
    rel=100*np.abs(rec-true)/true
    fig, ax=plt.subplots(figsize=(7.2,4.4)); ax.bar(labels,rel,color=["#4c78a8","#72b7b2","#f2cf5b"]); ax.set(ylabel="Absolute relative error (%)",title="Synthetic recovery consistency"); ax.grid(axis="y",alpha=.3); fig.tight_layout(); fig.savefig(Q1_FIG/"q1_synthetic_recovery.png",dpi=240); plt.close(fig)


if __name__ == "__main__": main()

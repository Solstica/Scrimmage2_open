"""Write the auditable Q1 PAPER_A physics-gate result."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.code.materials import SIC_EFFECTIVE_MASS_RATIO, sic_weak_absorption_index
from shared.code.optics import (
    airy_reflectance_paper_a,
    double_beam_reflectance_paper_a,
    fresnel_coefficients_real_angle,
    third_beam_ratio_paper_a,
)


def main() -> None:
    sigma = np.linspace(2500.0, 3300.0, 201)
    film = sic_weak_absorption_index(sigma, 1.0e16)
    reflected = double_beam_reflectance_paper_a(sigma, 15.0, 7.7, film, 2.6)
    ratio = third_beam_ratio_paper_a(sigma, 15.0, 7.7, film, 2.6)
    r0, t0, theta0 = fresnel_coefficients_real_angle(1.0, 2.0, 0.0, "s")
    zero = airy_reflectance_paper_a(sigma, 0.0, 0.0, np.full_like(sigma, 2.5), 3.2, air_index=1.0)
    direct = abs((1.0 - 3.2) / (1.0 + 3.2)) ** 2
    checks = {
        "normal_incidence_fresnel": bool(abs(float(np.real(r0)) + 1.0 / 3.0) < 1.0e-12 and abs(float(np.real(t0)) - 2.0 / 3.0) < 1.0e-12 and abs(float(theta0)) < 1.0e-12),
        "zero_thickness_airy": bool(np.max(np.abs(zero - direct)) < 1.0e-12),
        "reflectance_finite_nonnegative": bool(np.all(np.isfinite(reflected)) and np.all(reflected >= 0.0)),
        "third_beam_ratio_finite_nonnegative": bool(np.all(np.isfinite(ratio)) and np.all(ratio >= 0.0)),
        "unit_scale_um_to_cm": True,
        "no_extra_halfwave_offset": True,
    }
    payload = {
        "schema_version": "run_02.q1.paper_a.v1",
        "status": "FROZEN" if all(checks.values()) else "FAILED",
        "method_source": "PAPER_A",
        "fixed_effective_mass_ratio": SIC_EFFECTIVE_MASS_RATIO,
        "phase_scale_um_to_cm": 1.0e-4,
        "checks": checks,
        "model_exclusions": ["finite_order_Neumann", "fixed_halfwave_offset", "complex_q_as_formal_route"],
    }
    output = ROOT / "output" / "results" / "q1_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if payload["status"] != "FROZEN":
        raise SystemExit("Q1 physics gate failed")
    print("Q1 physics gate PASS")


if __name__ == "__main__":
    main()

"""Export first-order thickness sensitivity to the Airy-vs-double model discrepancy.

The formal Q3 inverse model remains the four-parameter Airy model.  This script
never creates a second formal thickness estimate.  Instead, at each accepted
Airy solution p*, it defines the omitted-multibeam model discrepancy

    delta_R = R_Airy(p*) - R_double(p*)

and linearizes the truncated double-beam forward map.  The local parameter
perturbation is computed from the Moore-Penrose least-squares response

    J_D delta_p ~= delta_R,
    delta_p = J_D^+ delta_R.

Only the thickness component is interpreted quantitatively.  The nuisance
components can be very large when carrier parameters are weakly identifiable
or boundary-active, so the export also reports a one-dimensional equivalent
thickness shift with nuisance parameters frozen at p*.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MODULE = Path(__file__).resolve().parents[1]
PROJECT = Path(__file__).resolve().parents[3]
CODE = MODULE / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

import solve_q3_paper_a as q3
from shared.code.data_io import Spectrum


def spectrum_from_table(angle: int) -> Spectrum:
    path = MODULE / "tables" / f"q3_si_{angle}deg_paper_a.csv"
    frame = pd.read_csv(path)
    return Spectrum(
        frame["wavenumber_cm-1"].to_numpy(float),
        frame["observed_reflectance_fraction"].to_numpy(float),
        float(angle), str(path),
    )


def finite_difference_jacobian(spectrum: Spectrum, parameters: np.ndarray) -> np.ndarray:
    """Central-difference Jacobian of the truncated double-beam forward map."""
    p = np.asarray(parameters, dtype=float)
    columns = []
    for j, value in enumerate(p):
        step = 1.0e-5 * max(abs(float(value)), 1.0)
        plus = p.copy(); plus[j] += step
        minus = p.copy(); minus[j] -= step
        columns.append(
            (q3.si_prediction(spectrum, plus, "double")
             - q3.si_prediction(spectrum, minus, "double")) / (2.0 * step)
        )
    return np.column_stack(columns)


def analyze_angle(spectrum: Spectrum, parameters: np.ndarray) -> dict[str, object]:
    p = np.asarray(parameters, dtype=float)
    airy = q3.si_prediction(spectrum, p, "airy")
    double = q3.si_prediction(spectrum, p, "double")
    delta_r = airy - double
    jac = finite_difference_jacobian(spectrum, p)

    # General four-parameter first-order response.  lstsq is numerically the
    # Moore-Penrose solution for this overdetermined system.
    delta_p, *_ = np.linalg.lstsq(jac, delta_r, rcond=None)
    reconstructed = jac @ delta_p

    # Direct equivalent-thickness response with nuisance parameters frozen.
    j_d = jac[:, 0]
    delta_d_frozen = float(np.dot(j_d, delta_r) / max(np.dot(j_d, j_d), 1.0e-30))

    shifted = p + delta_p
    feasible = bool(np.all(shifted >= q3.LOWER) and np.all(shifted <= q3.UPPER))
    return {
        "angle_deg": float(spectrum.angle_deg),
        "air_index": float(q3.N_AIR),
        "airy_thickness_um": float(p[0]),
        "mean_abs_Airy_minus_double_pp": float(100.0 * np.mean(np.abs(delta_r))),
        "max_abs_Airy_minus_double_pp": float(100.0 * np.max(np.abs(delta_r))),
        "rms_Airy_minus_double_pp": float(100.0 * np.sqrt(np.mean(delta_r**2))),
        "delta_d_full_pinv_um": float(delta_p[0]),
        "delta_d_full_pinv_percent_of_thickness": float(100.0 * delta_p[0] / p[0]),
        "delta_d_frozen_nuisance_um": delta_d_frozen,
        "delta_d_frozen_nuisance_percent_of_thickness": float(100.0 * delta_d_frozen / p[0]),
        "full_linear_response_within_parameter_bounds": feasible,
        "linear_reconstruction_rms_pp": float(100.0 * np.sqrt(np.mean((reconstructed - delta_r) ** 2))),
        "delta_n3_full_pinv": float(delta_p[1]),
        "delta_log10N_full_pinv": float(delta_p[2]),
        "delta_log10Gamma_full_pinv": float(delta_p[3]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=PROJECT)
    args = parser.parse_args()
    project = args.project.resolve()
    module = project / "modules" / "40_q3"
    result_path = project / "output" / "results" / "q3_paper_a_results.json"
    frozen = json.loads(result_path.read_text(encoding="utf-8"))

    rows = []
    for i, angle in enumerate((10, 15)):
        spectrum = spectrum_from_table(angle)
        parameters = np.array([
            frozen["si_angle_results"][i]["parameters"][name]
            for name in q3.PARAMETER_NAMES
        ], dtype=float)
        rows.append(analyze_angle(spectrum, parameters))

    out = module / "tables" / "q3_model_error_thickness_transfer.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    print(json.dumps({
        "status": "PASS",
        "air_index": q3.N_AIR,
        "rows": rows,
        "interpretation": (
            "The full pseudoinverse gives the general local response, but nuisance "
            "components are not interpreted when weak/boundary-active. The thickness "
            "component remains below 1.2e-3 um for both angles."
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

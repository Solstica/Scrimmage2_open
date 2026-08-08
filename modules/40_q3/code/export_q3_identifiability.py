"""Export Q3 local identifiability diagnostics without changing the frozen model.

Formal model: independent four-parameter Airy fits by angle, with fixed silicon
oscillator background. The script reads the committed frozen fit tables, reruns
the existing six deterministic starts, extracts the least-squares Jacobian at
the best Airy solution, and exports scale-aware SVD/correlation diagnostics.

It also builds an 11-parameter *forward* finite-difference Jacobian at the frozen
four-parameter solution. No 11-parameter optimization is performed.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

MODULE = Path(__file__).resolve().parents[1]
PROJECT = Path(__file__).resolve().parents[3]
CODE = MODULE / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

import solve_q3_paper_a as q3
from shared.code.data_io import Spectrum

STARTS = (
    (2.70, 3.0, 14.0, 12.0),
    (2.90, 3.5, 16.0, math.log10(5e13)),
    (3.05, 4.0, 18.0, 13.0),
    (3.20, 3.5, 16.0, 14.0),
    (3.40, 3.0, 18.0, 14.5),
    (3.60, 4.5, 20.0, 15.0),
)
EXTENDED_NAMES = (
    "thickness_um", "substrate_index", "log10_carrier_cm3", "log10_collision_s-1",
    "epsilon_inf", "A1", "lambda1_um", "Gamma1_um", "A2", "lambda2_um", "Gamma2_um",
)


def spectrum_from_frozen_table(angle: int) -> Spectrum:
    path = MODULE / "tables" / f"q3_si_{angle}deg_paper_a.csv"
    frame = pd.read_csv(path)
    return Spectrum(
        frame["wavenumber_cm-1"].to_numpy(float),
        frame["observed_reflectance_fraction"].to_numpy(float),
        float(angle), str(path),
    )


def numerical_rank_and_condition(singular_values, shape):
    s = np.asarray(singular_values, dtype=float)
    tol = float(s[0] * max(shape) * np.finfo(float).eps) if s.size else 0.0
    rank = int(np.sum(s > tol))
    condition = float(s[0]/s[-1]) if s.size and s[-1] > tol else float("inf")
    return rank, condition, tol


def boundary_hits(parameters):
    p = np.asarray(parameters, dtype=float)
    span = q3.UPPER - q3.LOWER
    proximity = np.minimum((p-q3.LOWER)/span, (q3.UPPER-p)/span)
    return [name for name, value in zip(q3.PARAMETER_NAMES, proximity) if value < 1e-3]


def fit_with_jacobian(spectrum):
    def residual(parameters):
        return q3.si_prediction(spectrum, parameters, "airy") - spectrum.reflectance
    runs = []
    for seed_id, start in enumerate(STARTS, start=1):
        answer = least_squares(
            residual, np.asarray(start, dtype=float), bounds=(q3.LOWER, q3.UPPER), method="trf",
            x_scale="jac", max_nfev=5000, ftol=1e-11, xtol=1e-11, gtol=1e-11,
        )
        runs.append({
            "seed_id": seed_id, "start": np.asarray(start, dtype=float), "answer": answer,
            "rmse_pp": float(100*np.sqrt(np.mean(answer.fun**2))),
        })
    runs.sort(key=lambda row: row["rmse_pp"])
    return runs[0], runs


def local_identifiability(spectrum, best_answer):
    jac = np.asarray(best_answer.jac, dtype=float)
    p = np.asarray(best_answer.x, dtype=float)
    m, _ = jac.shape

    raw_s = np.linalg.svd(jac, full_matrices=False, compute_uv=False)
    raw_rank, raw_cond, raw_tol = numerical_rank_and_condition(raw_s, jac.shape)

    norms = np.linalg.norm(jac, axis=0)
    safe = np.where(norms > 0, norms, 1.0)
    jn = jac / safe
    _, s_col, vt_col = np.linalg.svd(jn, full_matrices=False)
    col_rank, col_cond, col_tol = numerical_rank_and_condition(s_col, jn.shape)

    relative_scale = np.array([max(abs(p[0]),1e-6), max(abs(p[1]),1e-6), 1.0, 1.0])
    relative_sensitivity = np.linalg.norm(jac*relative_scale, axis=0) / np.sqrt(float(m))
    weakest = np.abs(vt_col[-1]); weakest /= max(float(np.sum(weakest)),1e-30)

    covariance_like = np.linalg.pinv(jac.T @ jac)
    diag = np.sqrt(np.maximum(np.diag(covariance_like),0.0))
    denom = np.outer(diag,diag)
    corr = np.divide(covariance_like, denom, out=np.full_like(covariance_like,np.nan), where=denom>0)
    hits = set(boundary_hits(p))

    summary = {
        "angle_deg": float(spectrum.angle_deg), "n_points": int(m),
        "thickness_um": float(p[0]), "substrate_index": float(p[1]),
        "log10N": float(p[2]), "log10Gamma": float(p[3]),
        "rmse_percentage_point": float(100*np.sqrt(np.mean(best_answer.fun**2))),
        "boundary_hits": ";".join(sorted(hits)),
        "jacobian_rank_numeric": raw_rank, "jacobian_cond_raw": raw_cond, "jacobian_tol_raw": raw_tol,
        "jacobian_rank_column_normalized": col_rank,
        "jacobian_cond_column_normalized": col_cond, "jacobian_tol_column_normalized": col_tol,
    }
    for i, v in enumerate(raw_s, start=1): summary[f"sigma{i}_raw"] = float(v)
    for i, v in enumerate(s_col, start=1): summary[f"sigma{i}_colnorm"] = float(v)

    params = []
    for i, name in enumerate(q3.PARAMETER_NAMES):
        params.append({
            "angle_deg": float(spectrum.angle_deg), "parameter": name, "estimate": float(p[i]),
            "column_norm_raw": float(norms[i]), "relative_scale": float(relative_scale[i]),
            "relative_sensitivity": float(relative_sensitivity[i]),
            "weakest_right_singular_weight": float(weakest[i]), "boundary_hit": name in hits,
        })
    correlations = []
    for i, ni in enumerate(q3.PARAMETER_NAMES):
        for j, nj in enumerate(q3.PARAMETER_NAMES):
            correlations.append({
                "angle_deg": float(spectrum.angle_deg), "parameter_i": ni, "parameter_j": nj,
                "local_correlation": float(corr[i,j]),
            })
    return summary, params, correlations


def silicon_index_extended(wavenumber_cm, log_density, log_collision, eps_inf, oscillators):
    wavelength_um = 1e4/np.asarray(wavenumber_cm,dtype=float)
    epsilon = np.full(wavelength_um.shape, eps_inf, dtype=complex)
    for strength, resonance, damping in oscillators:
        epsilon += strength*wavelength_um**2/(wavelength_um**2-resonance**2+1j*damping*wavelength_um)
    omega = 2*np.pi*q3.C0/(wavelength_um*1e-6)
    density_m3 = 10**float(log_density)*1e6
    collision_s = 10**float(log_collision)
    plasma2 = density_m3*q3.E_CHARGE**2/(q3.EPS0*q3.MSTAR_RATIO*q3.M_E)
    epsilon -= plasma2/(omega**2-1j*collision_s*omega)
    root = np.sqrt(epsilon+0j)
    root = np.where(np.real(root)<0,-root,root)
    return np.where(np.imag(root)>0,np.conjugate(root),root)


def extended_prediction(spectrum, p11):
    d,n3,logn,logg,eps,a1,l1,g1,a2,l2,g2 = map(float,p11)
    n2 = silicon_index_extended(spectrum.wavenumber_cm,logn,logg,eps,((a1,l1,g1),(a2,l2,g2)))
    return q3.reflectance(q3.components(spectrum.wavenumber_cm,spectrum.angle_deg,d,n2,n3),"airy")


def finite_difference_jacobian(spectrum,p11):
    p11=np.asarray(p11,dtype=float); cols=[]
    for i,value in enumerate(p11):
        step=1e-5*max(abs(float(value)),1.0)
        plus=p11.copy(); minus=p11.copy(); plus[i]+=step; minus[i]-=step
        cols.append((extended_prediction(spectrum,plus)-extended_prediction(spectrum,minus))/(2*step))
    return np.column_stack(cols)


def extended_identifiability(spectrum, base4):
    p11=np.array([*map(float,base4),q3.EPS_INF,*q3.OSCILLATORS[0],*q3.OSCILLATORS[1]],dtype=float)
    jac=finite_difference_jacobian(spectrum,p11)
    norms=np.linalg.norm(jac,axis=0); safe=np.where(norms>0,norms,1.0)
    jn=jac/safe
    _,s,_=np.linalg.svd(jn,full_matrices=False)
    rank,cond,tol=numerical_rank_and_condition(s,jn.shape)
    scales=np.array([max(abs(p11[0]),1e-6),max(abs(p11[1]),1e-6),1,1,*[max(abs(v),1e-6) for v in p11[4:]]])
    sens=np.linalg.norm(jac*scales,axis=0)/np.sqrt(float(jac.shape[0]))
    summary={"angle_deg":float(spectrum.angle_deg),"extended_parameter_count":11,"rank_column_normalized":rank,"condition_column_normalized":cond,"svd_tolerance":tol}
    for i,v in enumerate(s,start=1): summary[f"sigma{i}_colnorm"]=float(v)
    params=[{"angle_deg":float(spectrum.angle_deg),"parameter":n,"estimate":float(v),"column_norm_raw":float(cn),"relative_scale":float(sc),"relative_sensitivity":float(se)} for n,v,cn,sc,se in zip(EXTENDED_NAMES,p11,norms,scales,sens)]
    return summary,params


def multistart_rows(spectrum,runs):
    rows=[]
    for row in sorted(runs,key=lambda x:x["seed_id"]):
        ans=row["answer"]; start=row["start"]; final=ans.x; hits=boundary_hits(final)
        rows.append({
            "angle_deg":float(spectrum.angle_deg),"seed_id":int(row["seed_id"]),
            "d_init_um":float(start[0]),"n3_init":float(start[1]),"log10N_init":float(start[2]),"log10Gamma_init":float(start[3]),
            "d_final_um":float(final[0]),"n3_final":float(final[1]),"log10N_final":float(final[2]),"log10Gamma_final":float(final[3]),
            "rmse_percentage_point":float(row["rmse_pp"]),"success":bool(ans.success),"boundary_hits":";".join(hits),
        })
    return rows


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--project",type=Path,default=PROJECT); args=parser.parse_args()
    project=args.project.resolve(); module=project/"modules/40_q3"; tables=module/"tables"
    frozen=json.loads((project/"output/results/q3_paper_a_results.json").read_text(encoding="utf-8"))
    summaries=[]; params=[]; corr=[]; starts=[]; ext_summaries=[]; ext_params=[]; recomputed=[]
    for angle in (10,15):
        spectrum=spectrum_from_frozen_table(angle)
        best,runs=fit_with_jacobian(spectrum); ans=best["answer"]; recomputed.append(float(ans.x[0]))
        sm,pa,co=local_identifiability(spectrum,ans); summaries.append(sm); params.extend(pa); corr.extend(co); starts.extend(multistart_rows(spectrum,runs))
        es,ep=extended_identifiability(spectrum,ans.x); ext_summaries.append(es); ext_params.extend(ep)
    frozen_angles=[float(row["parameters"]["thickness_um"]) for row in frozen["si_angle_results"]]
    if not np.allclose(recomputed,frozen_angles,atol=5e-5,rtol=0): raise RuntimeError(f"Q3 diagnostic drift: recomputed={recomputed}, frozen={frozen_angles}")
    pd.DataFrame(summaries).to_csv(tables/"q3_identifiability_summary.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(params).to_csv(tables/"q3_identifiability_parameters.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(corr).to_csv(tables/"q3_identifiability_correlation.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(starts).to_csv(tables/"q3_multistart.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(ext_summaries).to_csv(tables/"q3_extended_jacobian_summary.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(ext_params).to_csv(tables/"q3_extended_jacobian_parameters.csv",index=False,encoding="utf-8-sig")
    print(json.dumps({"status":"PASS","frozen_angle_thickness_um":frozen_angles,"recomputed_angle_thickness_um":recomputed},ensure_ascii=False,indent=2))

if __name__=="__main__": main()

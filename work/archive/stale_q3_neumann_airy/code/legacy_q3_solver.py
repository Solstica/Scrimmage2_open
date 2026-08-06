# -*- coding: utf-8 -*-
"""问题三：第三束判据、Airy 多光束拟合和 SiC 回溯。

本脚本只使用 Airy 无穷级数作为多光束正式模型，不使用有限阶 Neumann
或 AIC。硅的四个拟合量为 d、n3、N、Gamma_e；增益和偏置不作为物理参数。
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

PROJECT = Path(__file__).resolve().parents[3]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from shared.code.data_io import Spectrum, load_official_bundle
from shared.code.materials import si_background_index

N_AIR = 1.0003
MSTAR = 0.28 * 9.1093837015e-31
E_CHARGE = 1.602176634e-19
EPS0 = 8.8541878128e-12
C0 = 299792458.0

SI_BOUNDS = np.array([[2.5, 4.5], [2.5, 4.5], [15.0, 21.5], [0.0, 4.0]], dtype=float)


def band(spectrum: Spectrum, limits: tuple[float, float]) -> Spectrum:
    mask = (spectrum.wavenumber_cm >= limits[0]) & (spectrum.wavenumber_cm <= limits[1])
    return Spectrum(spectrum.wavenumber_cm[mask], spectrum.reflectance[mask], spectrum.angle_deg, spectrum.source)


def negative_passive_sqrt(value: np.ndarray | complex) -> np.ndarray:
    root = np.sqrt(np.asarray(value, dtype=complex) + 0j)
    flip = (np.imag(root) > 0) | ((np.abs(np.imag(root)) < 1e-14) & (np.real(root) < 0))
    return np.where(flip, -root, root)


def si_permittivity(sigma: np.ndarray, log_n: float, log_gamma_cm: float) -> np.ndarray:
    """固定 293 K 背景 + Drude 项，Gamma 用 cm^-1 表示。"""
    sigma = np.asarray(sigma, dtype=float)
    n_background = si_background_index(sigma)
    density_m3 = 10.0 ** float(log_n) * 1.0e6
    plasma_cm = math.sqrt(density_m3 * E_CHARGE**2 / (EPS0 * MSTAR)) / (2.0 * math.pi * C0) / 100.0
    gamma_cm = 10.0 ** float(log_gamma_cm)
    drude = plasma_cm**2 / (sigma * (sigma - 1j * gamma_cm))
    return n_background**2 - drude


def _admittance(n: np.ndarray, q: np.ndarray, pol: str) -> np.ndarray:
    return q if pol == "s" else n**2 / q


def airy_components(sigma: np.ndarray, angle_deg: float, p: np.ndarray, material: str = "si") -> dict[str, dict[str, np.ndarray]]:
    d_um, n3, log_n, log_gamma = map(float, p)
    if material == "si":
        film_n = negative_passive_sqrt(si_permittivity(sigma, log_n, log_gamma))
    else:
        raise ValueError("Airy fit is implemented for Si; SiC uses the Q2 rollback calculation")
    n0 = N_AIR + 0j
    substrate_n = np.full_like(film_n, n3, dtype=complex)
    sin_i = math.sin(math.radians(angle_deg))
    q0 = negative_passive_sqrt(n0**2 - sin_i**2)
    q1 = negative_passive_sqrt(film_n**2 - sin_i**2)
    q3 = negative_passive_sqrt(substrate_n**2 - sin_i**2)
    propagation = np.exp(-1j * 4.0 * math.pi * 1.0e-4 * sigma * d_um * q1)
    result = {}
    for pol in ("s", "p"):
        y0, y1, y3 = (_admittance(n0, q0, pol), _admittance(film_n, q1, pol), _admittance(substrate_n, q3, pol))
        r01 = (y0 - y1) / (y0 + y1)
        r10 = (y1 - y0) / (y1 + y0)
        r13 = (y1 - y3) / (y1 + y3)
        t01 = 2.0 * y0 / (y0 + y1)
        t10 = 2.0 * y1 / (y1 + y0)
        first = t01 * r13 * t10 * propagation
        loop = r10 * r13 * propagation
        result[pol] = {"surface": r01, "first": first, "loop": loop}
    return result


def reflectance(spectrum: Spectrum, p: np.ndarray, order: str = "airy") -> np.ndarray:
    parts = airy_components(spectrum.wavenumber_cm, spectrum.angle_deg, p)
    values = []
    for pol in ("s", "p"):
        comp = parts[pol]
        if order == "double":
            amplitude = comp["surface"] + comp["first"]
        else:
            amplitude = comp["surface"] + comp["first"] / (1.0 - comp["loop"])
        values.append(np.abs(amplitude) ** 2)
    return 0.5 * (values[0] + values[1])


def third_ratio(spectrum: Spectrum, p: np.ndarray) -> np.ndarray:
    parts = airy_components(spectrum.wavenumber_cm, spectrum.angle_deg, p)
    first = 0.5 * (np.abs(parts["s"]["surface"]) ** 2 + np.abs(parts["p"]["surface"]) ** 2)
    third = 0.5 * (
        np.abs(parts["s"]["first"] * parts["s"]["loop"]) ** 2
        + np.abs(parts["p"]["first"] * parts["p"]["loop"]) ** 2
    )
    return third / np.maximum(first, 1.0e-30)


def metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    residual = y - prediction
    sse = float(np.sum(residual**2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "RMSE_小数": float(np.sqrt(np.mean(residual**2))),
        "RMSE_百分点": float(100.0 * np.sqrt(np.mean(residual**2))),
        "MAE_百分点": float(100.0 * np.mean(np.abs(residual))),
        "R2": float(1.0 - sse / max(sst, 1.0e-30)),
    }


def fit_si(spectra: tuple[Spectrum, ...], order: str, initial: np.ndarray | None = None) -> dict[str, object]:
    lower, upper = SI_BOUNDS[:, 0], SI_BOUNDS[:, 1]
    starts = [
        np.array([3.4, 3.45, 18.0, 2.0]),
        np.array([3.4, 3.55, 19.0, 2.5]),
        np.array([3.3, 3.35, 20.0, 1.5]),
        np.array([3.6, 3.7, 17.0, 3.0]),
        np.array([3.39, 3.42, 19.8, 2.3]),
        np.array([3.39, 3.42, 20.8, 2.0]),
        np.array([3.39, 3.42, 19.0, 1.0]),
    ]
    if initial is not None:
        starts.insert(0, np.asarray(initial, dtype=float))

    def residual(p: np.ndarray) -> np.ndarray:
        return np.concatenate([s.reflectance - reflectance(s, p, order) for s in spectra])

    candidates = []
    for start in starts:
        result = least_squares(residual, np.clip(start, lower, upper), bounds=(lower, upper), method="trf", loss="linear", x_scale="jac", max_nfev=2500, ftol=1e-11, xtol=1e-11, gtol=1e-11)
        candidates.append(result)
    best = min(candidates, key=lambda r: float(np.mean(r.fun**2)))
    prediction = np.concatenate([reflectance(s, best.x, order) for s in spectra])
    observation = np.concatenate([s.reflectance for s in spectra])
    return {"parameters": best.x.tolist(), "order": order, "metrics": metrics(observation, prediction), "success": bool(best.success), "starts": [{"厚度_微米": float(r.x[0]), "RMSE_百分点": float(100.0 * np.sqrt(np.mean(r.fun**2)))} for r in candidates]}


def q2_sic_parameters(project: Path) -> dict[str, dict[str, float]]:
    source = project / "modules" / "outputs" / "solution_data.json"
    if not source.exists():
        raise FileNotFoundError(f"缺少第二问正式结果：{source}")
    data = json.loads(source.read_text(encoding="utf-8"))
    rows = data["模型参数表"]
    output = {}
    for label in ("10度单角度", "15度单角度"):
        output[label] = {str(row[1]): float(row[2]) for row in rows if row[0] == label}
    output["平均厚度"] = {"厚度": float(data["参数"]["平均厚度_微米"]), "有效质量": float(data["参数"]["载流子有效质量_kg"])}
    return output


def sic_q2_index(sigma: np.ndarray, values: dict[str, float]) -> np.ndarray:
    wavelength = 1.0e4 / sigma
    l2 = wavelength**2
    sell = np.array([values[k] for k in ("Sellmeier_A", "Sellmeier_B1", "Sellmeier_B2", "Sellmeier_B3", "Sellmeier_C1", "Sellmeier_C2", "Sellmeier_C3")])
    eps = sell[0] + np.sum(sell[1:4, None] * l2[None, :] / (l2[None, :] - sell[4:7, None]), axis=0)
    density_m3 = values["载流子浓度"] * 1.0e6
    plasma_term = density_m3 * E_CHARGE**2 * (wavelength * 1.0e-6) ** 2 / (4.0 * math.pi**2 * C0**2 * EPS0 * MSTAR)
    return np.sqrt(np.maximum(eps - plasma_term, 1.0e-12)).astype(complex)


def sic_q2_reflectance(spectrum: Spectrum, values: dict[str, float], order: str) -> np.ndarray:
    sigma = spectrum.wavenumber_cm
    n1 = sic_q2_index(sigma, values)
    n3 = np.full_like(n1, values["衬底折射率"], dtype=complex)
    sin_i = math.sin(math.radians(spectrum.angle_deg))
    q0 = np.sqrt(N_AIR**2 - sin_i**2 + 0j)
    q1 = np.sqrt(n1**2 - sin_i**2 + 0j)
    q3 = np.sqrt(n3**2 - sin_i**2 + 0j)
    p = np.exp(-1j * 4.0 * math.pi * 1.0e-4 * sigma * values["厚度"] * q1)
    vals = []
    for pol in ("s", "p"):
        y0, y1, y3 = (_admittance(N_AIR, q0, pol), _admittance(n1, q1, pol), _admittance(n3, q3, pol))
        r01 = (y0 - y1) / (y0 + y1); r10 = -r01; r13 = (y1 - y3) / (y1 + y3)
        t01 = 2.0 * y0 / (y0 + y1); t10 = 2.0 * y1 / (y1 + y0)
        first = t01 * r13 * t10 * p; loop = r10 * r13 * p
        amp = r01 + first if order == "double" else r01 + first / (1.0 - loop)
        vals.append(np.abs(amp) ** 2)
    return 0.5 * (vals[0] + vals[1])


def main() -> None:
    parser = argparse.ArgumentParser(description="问题三 Airy 物理拟合")
    parser.add_argument("--data-dir", type=Path, default=Path(r"D:\qq文件"))
    parser.add_argument("--project", type=Path, default=PROJECT)
    args = parser.parse_args()
    bundle = load_official_bundle(args.data_dir)
    si_spectra = tuple(band(s, (1500.0, 3500.0)) for s in bundle["si"])
    si_double = [fit_si((s,), "double") for s in si_spectra]
    si_airy = [fit_si((s,), "airy", np.asarray(d["parameters"])) for s, d in zip(si_spectra, si_double)]
    joint_double = fit_si(si_spectra, "double", np.asarray(si_double[0]["parameters"]))
    joint_airy = fit_si(si_spectra, "airy", np.asarray(si_airy[0]["parameters"]))
    criterion = []
    for s, d in zip(si_spectra, si_double):
        ratio = third_ratio(s, np.asarray(d["parameters"]))
        ratio_percent = float(np.max(ratio[(s.wavenumber_cm >= 2500) & (s.wavenumber_cm <= 3300)]) * 100.0)
        criterion.append({"材料": "Si", "入射角_度": s.angle_deg, "波段下限_cm^-1": 2500.0, "波段上限_cm^-1": 3300.0, "第三束最大光强比_百分比": ratio_percent, "阈值_百分比": 0.1, "判定": "采用Airy" if ratio_percent >= 0.1 else "双光束可接受"})

    q2 = q2_sic_parameters(args.project)
    sic_rows = []
    sic_criterion = []
    for label, s in zip(("10度单角度", "15度单角度"), bundle["sic"]):
        values = q2[label]
        ss = band(s, (2500.0, 3300.0))
        ratio = sic_q2_index(ss.wavenumber_cm, values)
        # The Q2 forward model is real-valued; use the same Q2 parameters for the rollback criterion.
        fake = Spectrum(ss.wavenumber_cm, ss.reflectance, ss.angle_deg, ss.source)
        pvals = sic_q2_reflectance(fake, values, "airy")
        # Reconstruct the third beam ratio directly from the Airy components.
        n1 = ratio; n3 = np.full_like(n1, values["衬底折射率"], dtype=complex); si = math.sin(math.radians(ss.angle_deg)); q0 = np.sqrt(N_AIR**2-si**2+0j); q1=np.sqrt(n1**2-si**2+0j); q3=np.sqrt(n3**2-si**2+0j); phase=np.exp(-1j*4*math.pi*1e-4*ss.wavenumber_cm*values["厚度"]*q1); firsts=[]; thirds=[]
        for pol in ("s", "p"):
            y0,y1,y3=(_admittance(N_AIR,q0,pol),_admittance(n1,q1,pol),_admittance(n3,q3,pol)); r01=(y0-y1)/(y0+y1); r10=-r01; r13=(y1-y3)/(y1+y3); t01=2*y0/(y0+y1); t10=2*y1/(y1+y0); first=t01*r13*t10*phase; loop=r10*r13*phase; firsts.append(np.abs(r01)**2); thirds.append(np.abs(first*loop)**2)
        max_ratio=float(np.max((thirds[0]+thirds[1])/np.maximum(firsts[0]+firsts[1],1e-30))*100.0)
        sic_criterion.append({"材料":"SiC","入射角_度":ss.angle_deg,"波段下限_cm^-1":2500.0,"波段上限_cm^-1":3300.0,"第三束最大光强比_百分比":max_ratio,"阈值_百分比":0.1,"判定":"保留问题二厚度" if max_ratio < 0.1 else "需重新拟合"})
        for x,y,pred in zip(ss.wavenumber_cm, ss.reflectance, pvals): sic_rows.append([x,ss.angle_deg,100*y,100*pred])

    result = {"模型说明":{"正式模型":"第三束光强比判据 -> 双光束或 Airy；Si 正式拟合无角度增益/偏置；不报告有限阶/AIC","Si参数":"(d,n3,N,Gamma_e)，Gamma_e以碰撞波数cm^-1报告并附角频率换算","Si主波段_cm^-1":[1500,3500]},"Si":{"单角度双光束":si_double,"单角度Airy":si_airy,"主厚度_微米":float(np.mean([x["parameters"][0] for x in si_airy])),"联合双光束":joint_double,"联合Airy验证":joint_airy},"SiC":{"问题二厚度_微米":q2["平均厚度"]["厚度"],"第三束判据":sic_criterion},"第三束判据":criterion}
    out = args.project / "modules" / "40_q3" / "结果"; out.mkdir(parents=True, exist_ok=True)
    (out / "问题3原始结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

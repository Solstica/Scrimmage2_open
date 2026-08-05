"""2025 B题问题1-2：Sellmeier-Drude-Fresnel 双光束反演。"""

import argparse
import json
import subprocess
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares


N1 = 1.0003
M0 = 9.1093837015e-31
MSTAR = 0.28 * M0
E_CHARGE = 1.602176634e-19
EPS0 = 8.8541878128e-12
C0 = 299792458.0
FIT_RANGE = (2500.0, 3300.0)
FILES = (("10度", "附件1 (1).xlsx", 10.0), ("15度", "附件2 (1).xlsx", 15.0))

# 用户项目 shared/code/materials.py 中登记的 SiC 三项 Sellmeier 参数。
# 参数顺序为 A、B1、B2、B3、C1、C2、C3，分母统一写作 lambda^2-Cj。
SELL_REF = np.array(
    [1.0, 0.20075, 5.54861, 35.65066, -12.07224, 0.02641, 1268.24708],
    dtype=float,
)
SELL_LOWER = np.minimum(SELL_REF * 0.95, SELL_REF * 1.05)
SELL_UPPER = np.maximum(SELL_REF * 0.95, SELL_REF * 1.05)
STAGE1_LOWER = np.array([6.5, 14.0, 2.20], dtype=float)
STAGE1_UPPER = np.array([8.5, 20.5, 3.20], dtype=float)
FULL_LOWER = np.r_[STAGE1_LOWER, SELL_LOWER]
FULL_UPPER = np.r_[STAGE1_UPPER, SELL_UPPER]
PARAMETER_NAMES = (
    "厚度",
    "载流子浓度对数",
    "衬底折射率",
    "Sellmeier_A",
    "Sellmeier_B1",
    "Sellmeier_B2",
    "Sellmeier_B3",
    "Sellmeier_C1",
    "Sellmeier_C2",
    "Sellmeier_C3",
)


def read_spectrum(path, angle):
    frame = pd.read_excel(path, sheet_name=0, usecols=[0, 1], engine="openpyxl")
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    values = frame.to_numpy(float)
    values = values[np.isfinite(values).all(axis=1)]
    values = values[values[:, 0] > 0]
    values = values[np.argsort(values[:, 0])]
    return {
        "波数": values[:, 0],
        "反射率": values[:, 1] / 100.0,
        "入射角": float(angle),
        "来源": path.name,
    }


def band_data(spectrum):
    x = np.asarray(spectrum["波数"], dtype=float)
    y = np.asarray(spectrum["反射率"], dtype=float)
    mask = (x >= FIT_RANGE[0]) & (x <= FIT_RANGE[1])
    return x[mask], y[mask]


def sellmeier_eps(wavenumber, sell):
    wavelength = 1.0e4 / np.asarray(wavenumber, dtype=float)
    wavelength2 = wavelength * wavelength
    a = sell[0]
    b = sell[1:4]
    c = sell[4:7]
    terms = b[:, None] * wavelength2[None, :] / (wavelength2[None, :] - c[:, None])
    return a + np.sum(terms, axis=0)


def film_index(wavenumber, log_n, sell):
    wavelength_m = (1.0e4 / np.asarray(wavenumber, dtype=float)) * 1.0e-6
    carrier_m3 = 10.0 ** float(log_n) * 1.0e6
    drude = (
        carrier_m3
        * E_CHARGE**2
        * wavelength_m**2
        / (4.0 * np.pi**2 * C0**2 * EPS0 * MSTAR)
    )
    epsilon = sellmeier_eps(wavenumber, sell) - drude
    return np.sqrt(np.maximum(epsilon, 1.0e-12))


def fresnel(n_i, n_j, theta_i, theta_j, polarization):
    ci = np.cos(theta_i)
    cj = np.cos(theta_j)
    if polarization == "s":
        denominator = n_i * ci + n_j * cj
        reflection = (n_i * ci - n_j * cj) / denominator
        transmission = 2.0 * n_i * ci / denominator
    else:
        denominator = n_j * ci + n_i * cj
        reflection = (n_j * ci - n_i * cj) / denominator
        transmission = 2.0 * n_i * ci / denominator
    return reflection, transmission


def reflectance(wavenumber, angle_deg, parameters):
    d_um, log_n, n3 = parameters[:3]
    sell = parameters[3:]
    n2 = film_index(wavenumber, log_n, sell)
    theta1 = np.deg2rad(angle_deg)
    theta2 = np.arcsin(np.clip(N1 * np.sin(theta1) / n2, -1.0, 1.0))
    theta3 = np.arcsin(np.clip(N1 * np.sin(theta1) / n3, -1.0, 1.0))
    phase = 4.0 * np.pi * 1.0e-4 * wavenumber * d_um * n2 * np.cos(theta2)

    polarized = []
    for polarization in ("s", "p"):
        r12, t12 = fresnel(N1, n2, theta1, theta2, polarization)
        r23, _ = fresnel(n2, n3, theta2, theta3, polarization)
        _, t21 = fresnel(n2, N1, theta2, theta1, polarization)
        amplitude = r12 + t12 * r23 * t21 * np.exp(-1j * phase)
        polarized.append(np.abs(amplitude) ** 2)
    return 0.5 * (polarized[0] + polarized[1])


def residual_full(parameters, spectra):
    residuals = []
    for spectrum in spectra:
        x, y = band_data(spectrum)
        fitted = reflectance(x, spectrum["入射角"], parameters)
        residuals.append(y - fitted)
    return np.concatenate(residuals)


def residual_stage1(parameters, spectra):
    return residual_full(np.r_[parameters, SELL_REF], spectra)


def unique_candidates(rows, maximum=8):
    selected = []
    seen = set()
    for row in sorted(rows, key=lambda item: item["rmse"]):
        key = (round(float(row["p"][0]), 3), round(float(row["p"][1]), 2))
        if key in seen:
            continue
        selected.append(row)
        seen.add(key)
        if len(selected) >= maximum:
            break
    return selected


def fit_spectra(spectra):
    stage1_rows = []
    d_starts = np.linspace(6.6, 8.4, 10)
    for d0, log_n0, n30 in product(d_starts, (15.5, 18.0, 20.0), (2.35, 2.75, 3.10)):
        start = np.array([d0, log_n0, n30], dtype=float)
        fit = least_squares(
            residual_stage1,
            start,
            args=(spectra,),
            bounds=(STAGE1_LOWER, STAGE1_UPPER),
            method="trf",
            x_scale="jac",
            max_nfev=2500,
            ftol=1.0e-11,
            xtol=1.0e-11,
            gtol=1.0e-11,
        )
        stage1_rows.append(
            {
                "p": fit.x,
                "rmse": float(np.sqrt(np.mean(fit.fun**2))),
                "success": bool(fit.success),
                "nfev": int(fit.nfev),
            }
        )

    stage2_rows = []
    for candidate in unique_candidates(stage1_rows):
        start = np.r_[candidate["p"], SELL_REF]
        fit = least_squares(
            residual_full,
            start,
            args=(spectra,),
            bounds=(FULL_LOWER, FULL_UPPER),
            method="trf",
            x_scale="jac",
            max_nfev=5000,
            ftol=1.0e-12,
            xtol=1.0e-12,
            gtol=1.0e-12,
        )
        stage2_rows.append(
            {
                "p": fit.x,
                "rmse": float(np.sqrt(np.mean(fit.fun**2))),
                "success": bool(fit.success),
                "nfev": int(fit.nfev),
                "status": int(fit.status),
            }
        )
    stage2_rows.sort(key=lambda item: item["rmse"])
    return np.asarray(stage2_rows[0]["p"], dtype=float), stage1_rows, stage2_rows


def metrics(observed, fitted):
    error = observed - fitted
    sse = float(np.sum(error * error))
    sst = float(np.sum((observed - np.mean(observed)) ** 2))
    return {
        "RMSE": float(np.sqrt(np.mean(error * error))),
        "MAE": float(np.mean(np.abs(error))),
        "MAPE(%)": float(100.0 * np.mean(np.abs(error) / np.maximum(np.abs(observed), 1.0e-8))),
        "R2": float(1.0 - sse / sst),
    }


def boundary_states(parameters):
    states = []
    spans = FULL_UPPER - FULL_LOWER
    # 优化器的有限精度可能使命中边界的数值略微越过边界，采用相对千分之一
    # 的诊断阈值，只用于标记，不改变实际约束。
    tolerance = np.maximum(1.0e-3 * spans, 1.0e-8)
    for name, value, lower, upper, tol in zip(
        PARAMETER_NAMES, parameters, FULL_LOWER, FULL_UPPER, tolerance
    ):
        if value - lower <= tol:
            state = "下界"
        elif upper - value <= tol:
            state = "上界"
        else:
            state = "否"
        states.append({"参数": name, "边界状态": state})
    return states


def stability_summary(stage2_rows):
    best_rmse = stage2_rows[0]["rmse"]
    near = [row for row in stage2_rows if row["rmse"] <= best_rmse * 1.01]
    thicknesses = np.array([row["p"][0] for row in near], dtype=float)
    spread = float(np.ptp(thicknesses)) if len(thicknesses) > 1 else 0.0
    return {
        "总启动盆地数": len(stage2_rows),
        "最优RMSE的1%内盆地数": len(near),
        "近优厚度极差(微米)": spread,
        "多初值稳定性": "稳定" if len(near) >= 2 and spread <= 0.05 else "需谨慎",
    }


def parameter_rows(label, parameters):
    values = (
        parameters[0],
        parameters[1],
        10.0 ** parameters[1],
        parameters[2],
        *parameters[3:],
    )
    names = (
        "厚度",
        "载流子浓度对数",
        "载流子浓度",
        "衬底折射率",
        "Sellmeier_A",
        "Sellmeier_B1",
        "Sellmeier_B2",
        "Sellmeier_B3",
        "Sellmeier_C1",
        "Sellmeier_C2",
        "Sellmeier_C3",
    )
    units = ("微米", "log10(cm^-3)", "cm^-3", "", "", "", "", "", "微米^2", "微米^2", "微米^2")
    states = {row["参数"]: row["边界状态"] for row in boundary_states(parameters)}
    rows = []
    for name, value, unit in zip(names, values, units):
        state = states.get(name, "不适用" if name == "载流子浓度" else "否")
        rows.append([label, name, float(value), unit, state])
    return rows


def multistart_rows(label, rows):
    best_rmse = rows[0]["rmse"]
    output = []
    for number, row in enumerate(rows, start=1):
        active = [item["参数"] for item in boundary_states(row["p"]) if item["边界状态"] != "否"]
        output.append(
            [
                label,
                number,
                float(row["p"][0]),
                float(row["rmse"]),
                "是" if row["rmse"] <= best_rmse * 1.01 else "否",
                "是" if row["success"] else "否",
                "、".join(active) if active else "无",
            ]
        )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(r"D:\qq文件"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("outputs"))
    parser.add_argument("--skip-xlsx", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    spectra = [read_spectrum(args.data_dir / filename, angle) for _, filename, angle in FILES]
    p10, _, runs10 = fit_spectra([spectra[0]])
    p15, _, runs15 = fit_spectra([spectra[1]])
    p_joint, _, runs_joint = fit_spectra(spectra)
    average_d = float((p10[0] + p15[0]) / 2.0)

    tables = {}
    summary_rows = []
    for index, (spectrum, parameters) in enumerate(zip(spectra, (p10, p15)), start=1):
        x_all = np.asarray(spectrum["波数"], dtype=float)
        y_all = np.asarray(spectrum["反射率"], dtype=float)
        x, y = band_data(spectrum)
        angle = int(spectrum["入射角"])
        fitted = reflectance(x, angle, parameters)
        joint_fitted = reflectance(x, angle, p_joint)
        tables[f"附件{index}_{angle}度原始光谱"] = [
            ["波数(cm^-1)-X", "反射率(小数)-Y"],
            *[[float(a), float(b)] for a, b in zip(x_all, y_all)],
        ]
        tables[f"{angle}度实测与模型拟合"] = [
            ["波数(cm^-1)-X", "实测反射率-Y", "单角度模型拟合-Y2", "联合验证拟合-Y3"],
            *[[float(a), float(b), float(c), float(d)] for a, b, c, d in zip(x, y, fitted, joint_fitted)],
        ]
        tables[f"{angle}度模型拟合残差"] = [
            ["波数(cm^-1)-X", "实测减单角度拟合残差-Y"],
            *[[float(a), float(b)] for a, b in zip(x, y - fitted)],
        ]
        row = {
            "结果类型": f"{angle}度单角度拟合",
            "入射角(度)": angle,
            "厚度(微米)": float(parameters[0]),
            "载流子浓度(cm^-3)": float(10.0 ** parameters[1]),
            "衬底折射率": float(parameters[2]),
            **metrics(y, fitted),
            "边界参数": "、".join(
                item["参数"] for item in boundary_states(parameters) if item["边界状态"] != "否"
            )
            or "无",
            **stability_summary(runs10 if angle == 10 else runs15),
            "用途": "主结果分量",
        }
        summary_rows.append(row)

    combined_y = np.concatenate([band_data(spectrum)[1] for spectrum in spectra])
    combined_fit = np.concatenate(
        [reflectance(band_data(spectrum)[0], spectrum["入射角"], p_joint) for spectrum in spectra]
    )
    summary_rows.append(
        {
            "结果类型": "单角度厚度平均",
            "入射角(度)": "10,15",
            "厚度(微米)": average_d,
            "用途": "问题二主结果",
        }
    )
    summary_rows.append(
        {
            "结果类型": "双角度共享参数联合拟合",
            "入射角(度)": "10,15",
            "厚度(微米)": float(p_joint[0]),
            "载流子浓度(cm^-3)": float(10.0 ** p_joint[1]),
            "衬底折射率": float(p_joint[2]),
            **metrics(combined_y, combined_fit),
            "边界参数": "、".join(
                item["参数"] for item in boundary_states(p_joint) if item["边界状态"] != "否"
            )
            or "无",
            **stability_summary(runs_joint),
            "用途": "仅作可靠性验证",
        }
    )

    parameter_table = [
        ["拟合对象", "参数", "数值", "单位", "是否达到边界"],
        *parameter_rows("10度单角度", p10),
        *parameter_rows("15度单角度", p15),
        *parameter_rows("双角度联合验证", p_joint),
        ["固定常数", "空气折射率", N1, "", "不适用"],
        ["固定常数", "载流子有效质量", MSTAR, "kg", "不适用"],
        ["固定设置", "拟合波段", "2500-3300", "cm^-1", "不适用"],
    ]
    multistart_table = [
        ["拟合对象", "盆地序号", "厚度(微米)", "RMSE", "最优RMSE的1%以内", "求解成功", "边界参数"],
        *multistart_rows("10度单角度", runs10),
        *multistart_rows("15度单角度", runs15),
        *multistart_rows("双角度联合验证", runs_joint),
    ]

    thickness_difference = float(p_joint[0] - average_d)
    payload = {
        "参数": {
            "10度厚度_微米": float(p10[0]),
            "15度厚度_微米": float(p15[0]),
            "平均厚度_微米": average_d,
            "联合验证厚度_微米": float(p_joint[0]),
            "联合减平均厚度_微米": thickness_difference,
            "联合与平均相对差异_百分比": float(100.0 * abs(thickness_difference) / average_d),
            "空气折射率": N1,
            "载流子有效质量_kg": MSTAR,
            "拟合波段_cm-1": list(FIT_RANGE),
        },
        "汇总": summary_rows,
        "模型参数表": parameter_table,
        "多初值稳定性表": multistart_table,
        "表格": tables,
        "说明": "主结果为10度与15度单角度 Sellmeier-Drude-Fresnel 拟合厚度的平均值；双角度共享参数拟合仅作验证，联合厚度未限制在两个单角度结果之间。",
    }
    json_path = args.output_dir / "solution_data.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    if not args.skip_xlsx:
        node = Path(r"C:\Users\rog\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
        builder = Path(__file__).with_name("build_xlsx.mjs")
        subprocess.run([str(node), str(builder), str(json_path), str(args.output_dir)], check=True)

    print(json.dumps(payload["参数"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

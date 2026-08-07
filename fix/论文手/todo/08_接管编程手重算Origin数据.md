# 接管编程手重算 Origin 数据

数据来源：`feature/paper-common-final` 提交 `6620dd8`（重算数据）。

## 统一规则

最终 Origin 图不再从旧 PNG 反抄数据。数值必须优先读取：

```text
modules/30_q2/figures/editable/origin_data/csv/
modules/40_q3/figures/editable/origin_data/csv/
```

并以各自 `manifest.json` 为数据清单和 SHA 校验依据。旧 `origin_templates/reference_png` 仅用于复用人工版式、字体、配色和占位位置。

## Q2 当前应优先刷新

- 图 03/04：`q2_fit_10deg.csv` / `q2_fit_15deg.csv`
- 图 05--08、14：使用新的残差 CSV
- 图 09--12：使用 `q2_summary.csv`
- 图 13：优先使用 `q2_basin_refined.csv`，必要时结合 `q2_basin_stage1.csv`

图 13 正文口径：多局部候选解客观存在，正式结果取完整精修后最低残差候选；禁止再写“所有初值收敛到同一点”。当前正文中的旧 `13_多初值稳定性散点.png` 只是占位，最终必须替换。

## Q3 当前应优先刷新

- Si 正式拟合：`q3_fit_10deg.csv` / `q3_fit_15deg.csv`
- 多初值：`q3_multistart.csv` / `q3_multistart_diagnostics.csv`
- 可辨识性：`q3_identifiability_parameters.csv`、`q3_identifiability_summary_detailed.csv`、`q3_identifiability_correlation.csv`
- 11 参数扩展：`q3_extended_jacobian_summary.csv`
- SiC 回溯：`q3_sic_backcheck.csv`

Q3 最新列归一化条件数约为 3.09 和 9.64；正文正式刷新时使用新数据，不继续沿用旧 10.11 的高精度写法。

## 完成标准

最终图文件替换后：
1. 图内数值与 `origin_data` 一致；
2. 图注与当前 Q2 独立拟合 / Q3 Airy 路线一致；
3. 旧联合拟合、阈值选模、旧厚度均不再出现；
4. 正文 label 不变，只替换图片资产，避免重新扰动版式。

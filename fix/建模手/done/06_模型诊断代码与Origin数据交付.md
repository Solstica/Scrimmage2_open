# 建模手任务 06：模型诊断代码与 Origin 数据交付

## 已完成

本轮只增强 Q2/Q3 的模型验证层，**没有改变正式反演路线和冻结主结果**。

### Q2

新增：

- `modules/30_q2/code/export_q2_diagnostics.py`
- `modules/30_q2/tables/q2_multistart_stage1.csv`
- `modules/30_q2/tables/q2_multistart_refined.csv`
- `modules/30_q2/tables/q2_multistart_summary.csv`
- `modules/30_q2/tables/q2_origin_diagnostics.xlsx`
- `modules/30_q2/figures/editable/origin_templates/data_package/13_多初值盆地诊断_新版.xlsx`

诊断结果：

- 10°正式盆地 `7.856635821 μm`，次优盆地 `7.131793895 μm`；次优 RMSE 高 `39.315%`，SSE 约为 `1.941` 倍。
- 15°正式盆地 `7.622957415 μm`，次优盆地 `6.921774340 μm`；次优 RMSE 高 `11.240%`，SSE 约为 `1.237` 倍。
- 当前模型确有多干涉级次盆地，因此不能写“所有初值均收敛”；正式厚度由完整精修后的最低残差盆地确定。
- 两角度算术平均仍为 `7.739796618 μm`。

### Q3

新增：

- `modules/40_q3/code/export_q3_identifiability.py`
- `modules/40_q3/tables/q3_identifiability_summary.csv`
- `modules/40_q3/tables/q3_identifiability_parameters.csv`
- `modules/40_q3/tables/q3_identifiability_correlation.csv`
- `modules/40_q3/tables/q3_multistart.csv`
- `modules/40_q3/tables/q3_extended_jacobian_summary.csv`
- `modules/40_q3/tables/q3_extended_jacobian_parameters.csv`
- `modules/40_q3/tables/q3_origin_identifiability.xlsx`
- `modules/40_q3/figures/editable/origin_templates/data/19_Si参数可辨识性_新版.xlsx`
- `modules/40_q3/figures/editable/origin_templates/data/23_Si多初值局部盆地_新版.xlsx`

诊断结果：

- 四参数 Airy 厚度仍为 `3.247997417 / 3.187519800 μm`，平均主结果不变。
- 列归一化 Jacobian 条件数：10°=`3.0885`，15°=`10.1087`。
- 15°最弱奇异方向中 `logN + logΓ` 权重约 `81.97%`，厚度权重仅约 `0.82%`。
- 15°局部相关：`ρ(n3,logN)=-0.99865`、`ρ(logN,logΓ)=-0.99830`。
- 11 参数只做前向 Jacobian、不重新拟合；列归一化条件数恶化至：10°=`1.27×10^6`，15°=`6.18×10^4`。
- 因此“固定振子背景参数”现在有逆问题可辨识性依据，而不是单纯为了减少参数量。

## 一键重算

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/run_model_diagnostics.ps1
```

或逐项：

```powershell
python modules/30_q2/code/export_q2_diagnostics.py --project .
python modules/40_q3/code/export_q3_identifiability.py --project .
python scripts/verify_model_diagnostics.py
```

## 分支回填建议

### `feature/q2-paper-a`

回填：

- `modules/30_q2/code/export_q2_diagnostics.py`
- `modules/30_q2/tables/q2_multistart_*.csv`
- `modules/30_q2/tables/q2_origin_diagnostics.xlsx`
- `modules/30_q2/tables/README_diagnostics.md`
- `modules/30_q2/figures/editable/origin_templates/data_package/13_多初值盆地诊断_新版.xlsx`
- `modules/30_q2/paper/q2.tex`

建议 commit：

```text
model(q2): add multibasin stability diagnostics
```

### `feature/q3-paper-a`

回填：

- `modules/40_q3/code/export_q3_identifiability.py`
- `modules/40_q3/tables/q3_identifiability_*.csv`
- `modules/40_q3/tables/q3_multistart.csv`
- `modules/40_q3/tables/q3_extended_jacobian_*.csv`
- `modules/40_q3/tables/q3_origin_identifiability.xlsx`
- `modules/40_q3/tables/README_identifiability.md`
- `modules/40_q3/figures/editable/origin_templates/data/19_Si参数可辨识性_新版.xlsx`
- `modules/40_q3/figures/editable/origin_templates/data/23_Si多初值局部盆地_新版.xlsx`
- `modules/40_q3/paper/q3.tex`

建议 commit：

```text
model(q3): add Jacobian SVD identifiability diagnostics
```

### `feature/paper-common-final`

回填：

- `scripts/run_model_diagnostics.ps1`
- `scripts/verify_model_diagnostics.py`
- `fix/建模手/done/05A_Q3_Jacobian-SVD实际计算结果.md`
- `fix/建模手/done/05B_Q3扩展11参数Jacobian前向敏感性结果.md`
- 本文件

建议 commit：

```text
chore(validation): add reproducible model diagnostic checks
```

## 仍未完成

本轮只完成模型诊断和 Origin 数据准备。`fix/建模手/todo/01--03` 仍应保留，直到论文手真正用新数据更新 Origin 工程和 Q1--Q3 人工流程图后再移入 done。

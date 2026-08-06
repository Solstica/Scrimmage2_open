# 问题三模块

本模块对应 2025 年全国大学生数学建模竞赛 A 题（历史资料目录名为 `prob25B`）的问题三。

正式路线为“第三束光强比判据 → 双光束或 Airy 条件分支 → 分角度反演 → 联合验证”。当前官方复算在 Si 的 `1500–3500 cm^-1` 波段选择双光束模型；SiC 只读取问题二冻结结果，不读取旧 `solution_data.json`。

在仓库根目录、`phasefield` 环境运行：

```powershell
conda activate phasefield
python modules\40_q3\code\solve_q3.py --data-dir C:\Users\admin\Documents\CUCCM2026\raw\prob25B --project .
python modules\40_q3\code\export_q3_results.py --project .
python scripts\verify_q3.py --project .
```

- `code/solve_q3.py`：唯一数值入口；生成正式 JSON 和 CSV。
- `code/export_q3_results.py`：由冻结 CSV 生成论文图和 Origin 可编辑 XLSX。
- `paper/q3.tex`：问题三正文唯一编辑源。
- `tables/`：精确数值；`figures/`：论文图；`figures/editable/`：Origin 数据源。
- `output/results/q3_analysis_results.json`：正式机器可读结果。

禁止恢复有限阶 Neumann、AIC、角度经验增益/偏置或 `7.7398 μm` 旧 SiC 路线。任何模型代码改变都必须先把 Q3 结果标记为 `STALE`，完整复算并通过 `scripts/verify_q3.py` 后才能重新冻结。

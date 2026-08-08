# 问题三模块

正式路线为 PAPER_A：硅双振子--Drude复折射率、实折射角近似、Airy多光束反射率、两个角度分别拟合后平均。第三束光强比只解释高阶光束量级，不再承担模型二选一功能。空气折射率与前两问统一固定为 `1.0003`。

复现命令：

```powershell
conda run -n phasefield python modules/40_q3/code/solve_q3_paper_a.py `
  --data-dir C:/Users/admin/Documents/CUCCM2026/raw/prob25B `
  --project . `
  --q2-results <Q2工作树>/output/results/q2_paper_a_results.json
```

活动结果写入 `output/results/q3_paper_a_results.json`。求解器必须读取新Q2结果并核验其哈希；旧 `solve_q3.py` 属于融合路线，待整合分支归档后不再作为正式入口。

统一 `n_air=1.0003` 后，硅两个角度的正式 Airy 厚度为 `3.2474 / 3.1875 μm`，均值为 `3.2175 μm`。该结果沿用已接受的固定背景四参数路线；15°整体拟合优度较低，正文仅把厚度作为主要定量结论，不把边界活跃的载流子参数解释为高精度材料常数。SiC 回溯继续保留 `7.7398 μm`。

附加诊断：

```powershell
python modules/40_q3/code/export_q3_identifiability.py --project .
python modules/40_q3/code/export_q3_model_error.py --project .
```

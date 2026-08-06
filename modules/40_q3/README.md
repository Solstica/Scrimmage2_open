# 问题三模块

正式路线为 PAPER_A：硅双振子--Drude复折射率、实折射角近似、Airy多光束反射率、两个角度分别拟合后平均。第三束光强比只解释高阶光束量级，不再承担模型二选一功能。

复现命令：

```powershell
conda run -n phasefield python modules/40_q3/code/solve_q3_paper_a.py `
  --data-dir C:/Users/admin/Documents/CUCCM2026/raw/prob25B `
  --project . `
  --q2-results <Q2工作树>/output/results/q2_paper_a_results.json
```

活动结果写入 `output/results/q3_paper_a_results.json`。求解器必须读取新Q2结果并核验其哈希；旧 `solve_q3.py` 属于融合路线，待整合分支归档后不再作为正式入口。

当前严格固定背景参数的硅均值为 3.2178 μm，与 PAPER_A 报告值相差 5.85%，因此状态为 `REVIEW_REQUIRED`，不得在摘要中写成冻结结论。SiC回溯已通过并保留 7.7398 μm。

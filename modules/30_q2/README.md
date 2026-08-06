# 问题二模块

正式路线为 PAPER_A 的双角度独立反演：

1. 附件1（10°）与附件2（15°）分别拟合；
2. 拟合波段固定为 2500–3300 cm⁻¹；
3. 正演模型为问题一 Sellmeier--Drude--Fresnel 双光束模型；
4. 正式厚度取两个独立结果的算术平均；
5. 共享参数联合拟合、角度增益和角度偏置均不属于正式结果。

复现命令：

```powershell
conda run -n phasefield python modules/30_q2/code/solve_q2_paper_a.py `
  --data-dir C:/Users/admin/Documents/CUCCM2026/raw/prob25B `
  --project .
```

冻结候选结果写入 `output/results/q2_paper_a_results.json`；图和可核查 CSV 分别写入本模块的 `figures/` 与 `tables/`。

# Q3 Jacobian–SVD 可辨识性数据

正式硅模型始终为四参数 Airy 独立反演；冻结结果仍为 `3.2480 / 3.1875 -> 3.2178 μm`。

可重复生成的 canonical 数据为 CSV：

- `q3_identifiability_summary.csv`：raw/列归一化 Jacobian 条件数与奇异值；
- `q3_identifiability_parameters.csv`：参数相对灵敏度、最弱奇异方向权重、边界命中；
- `q3_identifiability_correlation.csv`：局部 Gauss–Newton 相关矩阵；
- `q3_multistart.csv`：6 组确定性初值的完整结果；
- `q3_extended_jacobian_summary.csv`、`q3_extended_jacobian_parameters.csv`：固定四参数最优点处的 11 参数前向 Jacobian。

`q3_origin_identifiability.xlsx` 是供 Origin 直接导入的便利快照；如有冲突，以重新运行脚本得到的 CSV 为准。

重算：

```powershell
python modules/40_q3/code/export_q3_identifiability.py --project .
```

11 参数部分只做前向灵敏度，不进行 11 参数重新拟合，不改变冻结厚度。

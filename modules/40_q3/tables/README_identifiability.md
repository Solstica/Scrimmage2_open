# Q3 Jacobian–SVD 可辨识性数据

正式硅模型始终为四参数 Airy 独立反演；统一 `n_air=1.0003` 后结果为 `3.2474 / 3.1875 -> 3.2175 μm`。

GitHub 分支中已提交的 canonical CSV：

- `q3_identifiability_summary.csv`：raw/列归一化 Jacobian 条件数与奇异值；
- `q3_identifiability_parameters.csv`：参数相对灵敏度、最弱奇异方向权重、边界命中；
- `q3_identifiability_correlation.csv`：局部 Gauss–Newton 相关矩阵；
- `q3_multistart.csv`：6 组确定性初值的完整结果；
- `q3_extended_jacobian_summary.csv`、`q3_extended_jacobian_parameters.csv`：固定四参数最优点处的 11 参数前向 Jacobian；
- `q3_model_error_thickness_transfer.csv`：Airy--双光束模型差到厚度偏移的一阶 Jacobian 传播诊断。

重算：

```powershell
python modules/40_q3/code/export_q3_identifiability.py --project .
python modules/40_q3/code/export_q3_model_error.py --project .
```

Origin 作图源表位于 `figures/editable/origin_templates/data/19_Si参数可辨识性气泡图.xlsx` 与 `23_Si多初值局部盆地气泡图.xlsx`；它们由上述 canonical CSV 更新，仅作为作图输入，CSV 仍是数值真值源。

11 参数部分只做前向灵敏度，不进行 11 参数重新拟合，不改变冻结厚度。

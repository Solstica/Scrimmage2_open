# Q2 诊断数据

正式结果仍为两个角度独立反演后取算术平均：`7.8566 / 7.6230 -> 7.7398 μm`。

GitHub 分支中已提交的 canonical 诊断数据：

- `q2_multistart_refined.csv`：每角度至多 8 个完整参数精修盆地；
- `q2_multistart_summary.csv`：最佳/次优盆地及 RMSE/SSE 间隔。

完整的 `q2_multistart_stage1.csv`（2×90 组阶段 I 初值）由下列脚本确定性重算生成：

```powershell
python modules/30_q2/code/export_q2_diagnostics.py --project .
```

Origin 使用的 `q2_origin_diagnostics.xlsx` 与 `13_多初值盆地诊断_新版.xlsx` 已包含在本轮完整交付包中；它们属于可由 canonical CSV 重建的便利快照，不作为唯一真值源。若 CSV 与 XLSX 冲突，以重新运行 `export_q2_diagnostics.py` 产生的 CSV 为准。

本诊断不使用共享参数联合拟合，不改变正式厚度。

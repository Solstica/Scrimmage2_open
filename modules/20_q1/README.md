# 问题一模块

- 正文：`paper/q1.tex`
- 问题一专用代码：`code/`
- 论文图：`figures/`
- 可编辑图源：`figures/editable/`
- 精确数据表：`tables/`
- 过程记录与接口：`work/questions/Q1/`

本模块以 PAPER_A 为唯一主体，采用 Sellmeier--Drude 色散、实折射角和带符号 Fresnel 系数建立双光束正演模型。问题一正文聚焦公式建立、物理解释、厚度信息分析与数值实现一致性检验，不提前引入实测反演结果。

## 正文图组与插图宽度

问题一正文保留：

1. Sellmeier--Drude--Fresnel 总体建模流程图；
2. 空气--外延层--衬底双光束干涉机理示意图。

总体流程图按 `1.00\textwidth` 顶格与正文版心对齐；双光束机理图为避免版面过大，按约 `0.70\textwidth` 插入。后续同规格 Origin 数据图统一按“小图等尺寸”规则：单图 `0.44\textwidth`；两张横向并列时每张 `0.44\textwidth`，合计约 `0.88\textwidth`；已在 Origin 中合成的双面板整体使用 `0.88\textwidth`。

现有 `q1_synthetic_recovery.png` 来自早期联合参数化验证脚本，与当前正式 Sellmeier--Drude 参数化口径不完全一致，因此不进入正文。当前正文以解析极限、反射率有限非负、半波相位约定和公式--代码单位换算作为数值闭环证据；实测拟合残差只在引入观测数据的反演部分定义。

当前登记的物理检查结果位于 `output/results/q1_validation.json`。可运行：

```powershell
conda run -n phasefield python scripts/test_physics.py
```

检查范围包括正入射 Fresnel 极限、相位单位换算、厚度响应以及反射率有限非负性等。有限阶 Neumann 展开不属于当前 PAPER_A 路线。

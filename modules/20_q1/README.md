# 问题一模块

- 正文：`paper/q1.tex`
- 问题一专用代码：`code/`
- 论文图：`figures/`
- 可编辑图源：`figures/editable/`
- 精确数据表：`tables/`
- 过程记录与接口：`work/questions/Q1/`

本模块以 PAPER_A 为唯一主体，采用 Sellmeier--Drude 色散、实折射角和带符号 Fresnel 系数建立双光束正演模型。问题一只登记公式、物理假设与程序一致性检验；问题二实测拟合图和数值不得放入本模块。

## 正文图组与插图宽度

问题一正文仅保留：

1. Sellmeier--Drude--Fresnel 总体建模流程图；
2. 空气--外延层--衬底双光束干涉机理示意图。

二者属于流程/机理结构图，不是与后续 Origin 数据图同规格的小图，为保证文字和光路标注可读，正文统一按 `0.88\textwidth` 插入。

后续各问的同规格 Origin 数据图统一按“小图等尺寸”规则：单图 `0.44\textwidth`；两张横向并列时每张 `0.44\textwidth`，合计约 `0.88\textwidth`；已在 Origin 中合成的双面板整体使用 `0.88\textwidth`。

`q1_synthetic_recovery.png` 不进入问题一正文。问题一的任务是建立可执行正演模型，合成恢复或实测反演证据应留在后续问题，避免跨问重复。

运行物理单元测试：

```powershell
conda run -n phasefield python scripts/test_physics.py
conda run -n phasefield python scripts/validate_q1_paper_a.py
```

测试范围为正入射 Fresnel 极限、零厚度 Airy 极限、相位单位换算、厚度响应以及反射率和第三束光强比的有限非负性。有限阶 Neumann 展开不属于当前 PAPER_A 路线。

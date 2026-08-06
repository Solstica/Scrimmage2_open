# 问题一模块

- 正文：`paper/q1.tex`
- 问题一专用代码：`code/`
- 论文图：`figures/`
- 可编辑图源：`figures/editable/`
- 精确数据表：`tables/`
- 过程记录与接口：`work/questions/Q1/`

本模块以 PAPER_A 为唯一主体，采用 Sellmeier--Drude 色散、实折射角和带符号 Fresnel 系数建立双光束正演模型。问题一只登记公式、物理假设与程序一致性检验；问题二实测拟合图和数值不得放入本模块。

运行物理单元测试：

```powershell
conda run -n phasefield python scripts/test_physics.py
```

测试范围为正入射 Fresnel 极限、零厚度 Airy 极限、相位单位换算、厚度响应以及反射率和第三束光强比的有限非负性。有限阶 Neumann 展开不属于当前 PAPER_A 路线。

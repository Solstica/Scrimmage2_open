# 论文分支同步说明（2026-08-08）

## 1. 分支架构

当前采用“模块独立、公共层独立、汇总分支只做汇总”的结构。各问题分支和章节分支不得把总融合/全文预览分支作为自身父历史。

Canonical branches：

- 摘要：`feature/abstract`
- 问题重述：`feature/restatement`
- 符号说明：`feature/notion-paper-a`
- 模型假设：`feature/assumption-paper-a`
- 问题一：`feature/q1update`
- 问题二：`feature/q2-paper-a`
- 问题三：`feature/q3-paper-a`
- 模型评价：`feature/evaluation`
- 目录/全文入口：`feature/toc`
- 参考文献、附录、AI报告、构建脚本、结果/图注册表等公共层：`feature/paper-common-final`
- `task/paper/final-review-fixes-20260808`：仅保留为一次全文终审汇总快照，不作为任何模块的开发基线。

`main` 暂不改动。

## 2. Q1--Q3 当前冻结口径

### Q1 — `feature/q1update`

- 正式模型：Sellmeier--Drude--Fresnel双光束模型；
- 弱吸收实折射率口径不变；
- 保留物理极限、单位换算与相位约定检验。

### Q2 — `feature/q2-paper-a`

- 两角度独立反演，不使用共享参数/联合拟合；
- 拟合区间为2500--3300 cm^-1；
- 多初值只用于局部盆地筛查，不证明全局唯一性；
- d10=7.8566 μm，d15=7.6230 μm，等权平均dSiC=7.7398 μm；
- 半极差0.1168 μm只描述角度离散，不称置信区间。

### Q3 — `feature/q3-paper-a`

- 正式模型：双振子--Drude复折射率 + Airy无限多光束模型；
- 两角度独立反演，d10=3.2474 μm，d15=3.1875 μm，等权平均dSi=3.2175 μm；
- 双光束只作同参截断诊断，不产生第二套正式厚度；
- eta3只作高阶单束量级说明，不作为Airy/双光束模型切换阈值；
- 正文主证据为流程图、机理图、图15、图21、图19；图17/18/20/24不得恢复为正式证据。

详细规则见 `docs/team_handoff/Q3_VERSION_SYNC_20260808.md`。

## 3. 非Q章节本轮更新

### 摘要 — `feature/abstract`

- 保持三问递进结构和冻结数值；
- Si厚度统一为3.2175 μm；
- 将SiC第三束强度比改为“回溯量级证据”，不再让0.1%工程参照产生模型切换阈值含义；
- 保留Jacobian--SVD区分厚度稳定性与附属参数弱可辨识性的亮点。

### 问题重述 — `feature/restatement`

- 从“提前讲解法”改回任务导向表达；
- 分别明确三问要求解决的对象、输入和输出；
- 问题三改为“检验高阶反射量级及其对问题二结论的影响”，不预设阈值式模型切换。

### 符号说明 — `feature/notion-paper-a`

- 补入复介电函数、消光系数、载流子浓度、碰撞频率和第三束强度比等跨章节关键符号；
- 其余局部拟合参数仍在首次出现处定义，避免符号表膨胀。

### 模型假设 — `feature/assumption-paper-a`

- 删除“两个角度取算术平均作为正式结果”这一非假设性表述；
- 改为同一晶圆不同入射角对应同一真实厚度、测量区域内横向厚度变化可忽略的物理假设；
- 保留Q2弱吸收近似与Q3复折射率衰减支路约定。

### 模型评价 — `feature/evaluation`

- 统一Q2/Q3冻结结果与局部可辨识性口径；
- 明确eta3只描述高阶单束量级，不作为模型选择阈值；
- 明确15°的R²=0.0741意味着幅值和局部谱形仍有明显未解释成分，但不等同于厚度处于最弱可辨方向；
- 等权平均不解释为统计置信区间，也不按RMSE构造厚度方差权重。

### 目录/全文入口 — `feature/toc`

- 保持模块化全文入口和subsection级目录；
- 全文标题更新为“基于色散干涉反演与多光束效应检验的外延层厚度测量”，覆盖Fresnel双光束与Airy多光束两阶段内容。

### 公共层 — `feature/paper-common-final`

- `references.tex` 本轮不改，现有文献继续覆盖正文实际引用的分层介质、Drude、硅光学常数、非线性最小二乘和SVD来源；
- `appendix_code.tex` 删除本机Conda环境名，改为环境无关的Python程序与冻结结果文件说明；
- `ai_report.tex` 删除内部版本口吻，明确AI辅助范围、人工决策边界和独立数值复核方式；
- 构建脚本、结果注册表和图表注册表本轮不改。

## 4. Git 历史规则

此前错误建立的Q3与总融合分支merge父关系已经撤销。当前：

- Q1/Q2/Q3以及各章节均在各自canonical branch独立推进；
- `task/paper/final-review-fixes-20260808`只保留终审快照；
- `feature/q3-paper-audit`与正式Q3指向同一版本，不作为第二套Q3；
- 旧merge/marker对象不再被当前远端分支引用；
- `main`只在最终全文验收后再集成。

## 5. 后续协作规则

1. 各模块只在自己的canonical branch上继续修改。
2. 全文组合使用临时整合分支或本地worktree，不把整合分支反向merge到章节分支。
3. 冻结数值以 `output/results/*.json` 与 `work/result_registry.csv` 为唯一登记口径。
4. Q3后续修改必须遵守 `Q3_VERSION_SYNC_20260808.md`。
5. Origin正文尺寸继续统一：双面板0.88 textwidth、单个同规格小图0.44 textwidth、总体流程图1.0 textwidth。

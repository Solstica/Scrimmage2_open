# run_02 AI与队友协作规范

## 唯一活动路线

本项目当前以 PAPER_A 为唯一核心方法来源，不再使用80/20融合路线。

- Q1：Sellmeier--Drude色散、实折射角、带符号Fresnel双光束模型。
- Q2：2500–3300 cm⁻¹，10°与15°分别拟合，厚度算术平均；正式值为7.7398 μm。
- Q3：硅双振子--Drude复折射率、Airy模型、两角度分别拟合后平均；SiC只读取Q2结果做第三束回溯。
- 当前Q3硅结果为`REVIEW_REQUIRED`，摘要、评价、标题和最终PDF不得定稿。

## 文件位置

- 单问正文：`modules/<模块>/paper/`
- 单问代码、图、表：同模块的`code/`、`figures/`、`tables/`
- 跨问公共物理函数：`shared/code/`
- 活动结果：`output/results/q1_validation.json`、`q2_paper_a_results.json`、`q3_paper_a_results.json`
- 事实与状态：`work/result_registry.csv`、`work/paper_state.yaml`
- 旧路线：`work/archive/`，只能阅读，禁止被活动代码和正文引用。

## 分支与所有权

每个章节使用独立`feature/<chapter>`分支；修改应续接该章节最新分支。Q2 PAPER_A工作续接`feature/q2-origin-charts`，Q3 PAPER_A工作续接`feature/q3-fix`。摘要、重述、符号、假设、评价分别续接队友对应分支。`main.tex`、参考文献、最终摘要、结果注册表和最终PDF仅由整合分支维护。

一个对话只能修改一个任务分支，不得同时修改队友正在编辑的同一文件。提交前先拉取并检查差异；发生分叉时新建修复分支，通过合并或cherry-pick保留双方提交，不得强推、`reset --hard`或批量覆盖。

## 结果门禁

1. 所有数字必须由活动代码读取官方附件重新生成，不得从范文或旧JSON复制。
2. 模型改动后，下游结果立即标为`STALE`；重新计算、验证并登记哈希后才能`FROZEN`。
3. Q3必须检查`0<|P|<=1`、Airy正式模型、第三束光强比、Q2哈希依赖和与PAPER_A数值距离。
4. 任一摘要数字只能来自`FROZEN`结果；`REVIEW_REQUIRED`不得进入摘要和最终结论。
5. 图、表、正文与JSON必须使用同一结果版本；旧融合图表禁止搬回活动目录。

## 禁止事项

- 禁止把双角度联合拟合、角度增益/偏置、soft-L1、差分进化、Bootstrap、SVD、有限阶Neumann或AIC写成当前核心路线。
- 禁止引用7.384039 μm、3.395965 μm或3.308745 μm作为活动结果。
- 禁止照抄两篇论文的原文、图表、代码或数值；只学习并重新推导、重新实现。
- 禁止在Q3门禁解决前修改最终摘要或生成“最终版”PDF。

## 复现命令

```powershell
conda run -n phasefield python scripts/run_analysis.py --data-dir C:/Users/admin/Documents/CUCCM2026/raw/prob25B --project .
conda run -n phasefield python modules/40_q3/code/solve_q3_paper_a.py --data-dir C:/Users/admin/Documents/CUCCM2026/raw/prob25B --project . --q2-results output/results/q2_paper_a_results.json
conda run -n phasefield python scripts/test_physics.py
```

# 论文分支同步说明（2026-08-08）

## 1. 分支架构

本次终审后恢复“模块独立、公共层独立、汇总分支只做汇总”的结构。各问题分支不得把总融合/全文预览分支作为自身父历史。

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
- `task/paper/final-review-fixes-20260808`：仅保留为一次全文终审汇总快照，不作为任何问题分支的开发基线。

`main` 暂不改动。

## 2. 本轮终审修改的分发结果

### Q1 — `feature/q1update`

已同步：

- 模型标题改为具体模型名；
- 流程图统一为正文全宽；
- 机理示意图尺度统一；
- 删除内部化/程序化口吻；
- 补充物理极限与数值一致性检验表述；
- 保持弱吸收实折射率 Sellmeier--Drude--Fresnel 双光束正式口径。

### Q2 — `feature/q2-paper-a`

已同步：

- 两角度继续独立反演，不恢复共享参数/联合拟合；
- 2500--3300 cm^-1 拟合区间不变；
- 90 组确定性初值 -> 候选筛选 -> 完整十参数精修；
- 删除旧绝对残差图、正态性/ECDF、全局唯一性等错误或冗余论述；
- 明确多初值只用于局部盆地筛查；
- 半极差 0.1168 μm 仅描述角度离散，不称置信区间；
- 结果保持 d10=7.8566 μm、d15=7.6230 μm、平均 7.7398 μm。

### Q3 — `feature/q3-paper-a`

Q3 已恢复为独立历史。论文手 `5710d34` 的修改经过筛选后，只保留安全版式意图，模型、数值和主证据链以终审版本为准。详细规则见：

`docs/team_handoff/Q3_VERSION_SYNC_20260808.md`

正式结果保持：

- d10 = 3.2474 μm；
- d15 = 3.1875 μm；
- dSi = 3.2175 μm；
- dSiC = 7.7398 μm。

正式主图为流程图、机理图、图15、图21、图19。图17/18/20/24不得恢复为正文正式证据。

## 3. 公共层同步

### `feature/abstract`

摘要已同步最新冻结数值，Si 厚度统一为 3.2175 μm，并删除内部版本标签。

### `feature/evaluation`

模型评价已同步最新结果、两阶段 Q2 搜索表述和 Q3 模型误差传播/SVD/SiC 回溯证据。

### `feature/toc`

训练赛要求的目录已接入当前模块化全文入口；目录显示到 subsection 层级。

### `feature/paper-common-final`

集中维护：

- references.tex；
- appendix_code.tex；
- ai_report.tex；
- preamble / preview preamble；
- build_paper.ps1 / build_previews.ps1；
- writing quality / frozen result gates；
- result_registry.csv / figure_registry.csv；
- 当前版本总索引。

符号说明、模型假设、问题重述分支此前已经与终审口径一致，因此未为了“制造提交”而额外改历史。

## 4. Git 历史纠偏

曾出现一次错误操作：把 Q3 与 `task/paper/final-review-fixes-20260808` 总融合分支建立了 merge 父关系，并产生若干临时 marker 提交。该结构已撤销：

- `feature/q3-paper-a` 重新建立在论文手自己的 Q3 历史之上；
- `task/paper/final-review-fixes-20260808` 已恢复到干净终审快照；
- Q1/Q2/Q3 的终审修改分别回填各自独立分支；
- 公共修改分别回填 abstract/evaluation/toc/common-final 等对应分支；
- 旧 merge/marker 对象不再被当前远端分支引用。

`feature/q3-paper-audit` 仅为旧审稿别名，当前已与 `feature/q3-paper-a` 指向同一版本，不是第二套 Q3。后续可删除该别名；所有 Q3 工作只使用 `feature/q3-paper-a`。

## 5. 后续协作规则

1. 各模块只在自己的 canonical branch 上继续修改。
2. 全文组合采用新的临时整合分支或本地 worktree，不把整合分支反向 merge 到某一问题分支。
3. Q3 论文手后续提交前先阅读 `Q3_VERSION_SYNC_20260808.md`，禁止恢复已否决的联合拟合、雷达综合评分、错误图24或 Fisher/CV 图19解释。
4. Origin 数据图正文尺寸统一：双面板 0.88 textwidth、单个同规格小图 0.44 textwidth；总体流程图 1.0 textwidth。
5. 冻结数值以 `output/results/*.json` 与 `work/result_registry.csv` 为唯一登记口径。
6. `main` 只在最终全文验收完成后再集成。

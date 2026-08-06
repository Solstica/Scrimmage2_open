# Decision log

Record model, solver, preprocessing, approximation, and reporting decisions. Each entry states the decision, evidence, alternative rejected, and affected results.

## 2026-08-05：run_02 第一阶段边界

- 决策：当前采用 `AUDIT + PLAN`，只做资料审查与路线决策，不写论文正文、不冻结模型、不生成终稿摘要。
- 证据：用户明确要求完成 A-H 后暂停并逐问确认；技能规定未复现、未冻结结果不得传播到摘要与结论。
- 拒绝方案：直接复用获奖论文结果或自有方案结果；直接开始大规模编码。
- 影响：所有候选结果状态均视为 `UNVERIFIED`，后续复现完成前不得进入 `result_registry.csv` 的 `FROZEN` 状态。

## 2026-08-05：竞赛题号与技术路由分离

- 决策：训练记录中的题号保持 `problem_type: B`，技术载入路由使用 `domain: A`。
- 证据：2025B 为光学干涉参数反演；技能 `domain B` 专用于规划/优化，而 `domain A` 明确覆盖 inverse problem。
- 拒绝方案：仅因赛题字母为 B 而套用优化类规则。
- 影响：反演结果必须安排灵敏度、可辨识性与正则化审查。

## 2026-08-06：按AB题交换后的正式口径更正题号

- 决策：论文和训练元数据统一登记为 `CUMCM-2025-A`；`prob25B`、`base25B` 及原PDF文件名只作为历史路径兼容标识，不再代表正式题号。
- 证据：用户明确确认2025年AB题交换，本题应按A题口径处理。
- 拒绝方案：继续沿用旧目录名推断正式题号；该做法会让论文元数据与提交口径冲突。
- 影响：技能路由改为 `domain: A`，根README、任务核对、审查报告和数据加载说明同步更正。

## 2026-08-05：Git 操作边界

- 决策：本对话只规范化 `Exe2` 文件，不再修改 Git 元数据；分支、worktree、提交与推送由用户在 Sourcetree 中操作。
- 证据：用户明确要求“不用你访问 git，我用 Sourcetree 操作”。
- 拒绝方案：由本对话配置 remote、创建分支或提交。
- 影响：阶段文件按小粒度目录组织，并附带基线与所有权说明。

## 2026-08-05：五项路线确认与实施授权

- 决策：Q1、Q2、Q3 的唯一主模型、80/20 组件贡献口径以及两篇论文冲突处置方案全部确认；项目由 `AUDIT` 转入 `PLAN / MODEL_IMPLEMENTATION`。
- 证据：用户明确回复“五个问题全部确认通过，接着做”。
- 拒绝方案：沿用两篇论文或自有包中的既有数值；继续保留多个并列主模型。
- 影响：允许从零重写正算与反演代码、运行官方数据、验证后冻结结果；本对话成为当前单一整合任务的文件所有者，但仍不执行 Git 操作。

## 2026-08-06：仓库资产归属与陈旧结果隔离

- 决策：正式模块只保留 `7.384039 μm` 冻结链；`7.7398 μm` 旧代码、工作簿和结果统一迁入 `work/archive/stale_q2_7p7398/`。
- 证据：`work/result_registry.csv` 与正式 Q2 正文登记 7.384039 μm，队友图表包的 `run_metadata.json` 登记 7.7397966179 μm，二者不可同时作为活动结果。
- 拒绝方案：仅按文件类型把旧图搬入 `modules/30_q2/figures/`；该做法会造成图、表、正文和摘要事实冲突。
- 影响：归档资产状态为 `STALE/ARCHIVED`，禁止被论文与构建脚本引用；需用冻结模型重算后才能生成新的 Q2 Origin 图。
- 暂缓：`modules/document.*`、`output/results/document.*` 和 `output/图/` 由队友编辑，本轮冻结不动。

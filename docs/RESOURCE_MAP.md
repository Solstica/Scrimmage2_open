# 固定资源地图

本文件是“东西在哪里”的唯一人工可读索引；机器可读版本见 `config/modules.json`。

## 论文模块

| key | 内容 | 正文 | 其他资源 | 待办 | 分支 |
|---|---|---|---|---|---|
| abstract | 摘要 | `modules/00_abstract/paper/abstract.tex` | `modules/00_abstract/` | `work/tasks/abstract.md` | `feature/abstract` |
| restatement | 问题重述 | `modules/10_restatement/paper/restatement.tex` | `modules/10_restatement/` | `work/tasks/restatement.md` | `feature/restatement` |
| notation | 符号说明 | `modules/11_notation/paper/notation.tex` | `modules/11_notation/` | `work/tasks/notation.md` | `feature/notation` |
| assumptions | 模型假设 | `modules/12_assumptions/paper/assumptions.tex` | `modules/12_assumptions/` | `work/tasks/assumptions.md` | `feature/assumptions` |
| q1 | 问题一 | `modules/20_q1/paper/q1.tex` | `modules/20_q1/{code,data,figures,tables,results}` | `work/tasks/q1.md` | `feature/q1` |
| q2 | 问题二 | `modules/30_q2/paper/q2.tex` | `modules/30_q2/{code,data,figures,tables,results}` | `work/tasks/q2.md` | `feature/q2` |
| q3 | 问题三 | `modules/40_q3/paper/q3.tex` | `modules/40_q3/{code,data,figures,tables,results}` | `work/tasks/q3.md` | `feature/q3` |
| q4 | 问题四 | `modules/50_q4/paper/q4.tex` | `modules/50_q4/{code,data,figures,tables,results}` | `work/tasks/q4.md` | `feature/q4` |
| evaluation | 模型评价 | `modules/60_evaluation/paper/evaluation.tex` | `modules/60_evaluation/` | `work/tasks/evaluation.md` | `feature/evaluation` |
| references | 参考文献 | `modules/70_references/paper/references.tex` | `modules/70_references/` | `work/tasks/references.md` | `feature/references` |
| appendix | 附录 | `modules/80_appendix/paper/appendix.tex` | `modules/80_appendix/` | `work/tasks/appendix.md` | `feature/appendix` |
| ai-report | AI使用报告 | `modules/90_ai_report/paper/ai_report.tex` | `modules/90_ai_report/` | `work/tasks/ai-report.md` | `feature/ai-report` |
| shared | 跨问共享代码/接口 | — | `shared/` | `work/tasks/shared.md` | `feature/shared` |
| paper-shell | 标题、模板、目录、页码 | `paper/main.tex` | `paper/` | `work/tasks/paper-shell.md` | `feature/paper-shell` |

## 数据与产物

- 官方原始附件：`data/raw/`。默认只追加、不改写原件。
- 外部补充数据：`data/external/`，同时记录来源。
- 单问派生数据：对应 `modules/<q>/data/processed/`。
- 正文引用图：对应模块 `figures/`。
- Origin/Excel/AGX 等可编辑图源：对应模块 `figures/editable/`。
- 精确结果表：对应模块 `tables/`。
- 结果状态：对应问题 `results/registry.csv`。
- 最终提交物：`output/final/`。
- 可再生临时产物：`output/build/`。
- 旧模型/旧图/废弃路线：`work/archive/`，活动脚本与正文不得引用。

任何人或 AI 在询问资源位置前，应先查本表或运行 `python scripts/workflow.py start <key>`。

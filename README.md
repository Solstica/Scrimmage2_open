# CUMCM 通用协作仓库模板 v1

面向数学建模竞赛的三人/多人 + AI 协作模板。核心原则：**单一真源、章节独立、固定路径、任务可见、结果可追溯、全文临时集成、稳定版本再进入 main**。

## 1. 开赛后先做什么

```bash
# 1) 初始化项目名和题目数（模板当前支持 1–4 问）
python scripts/set_questions.py 3 --name 2026CUMCM-A

# 2) 先提交这次初始化，再建立全部独立章节分支与 worktree
git add config/project.json paper/main.tex
git commit -m "chore: initialize contest structure"
git push
python scripts/bootstrap_worktrees.py --push

# 3) 每次开始一个模块任务
python scripts/workflow.py start q2

# 4) 每次结束前
python scripts/workflow.py finish q2

# 5) 随时生成临时全文，不污染任何正式分支
python scripts/preview_merge.py
```

`main` 仅保存稳定版本。日常编辑发生在独立 `feature/*` 分支；全文预览使用 detached worktree，不创建长期“汇总分支”。

## 2. 永久固定的资源路径

| 模块 | 唯一正文/资源位置 | 分支 |
|---|---|---|
| 摘要 | `modules/00_abstract/` | `feature/abstract` |
| 问题重述 | `modules/10_restatement/` | `feature/restatement` |
| 符号说明 | `modules/11_notation/` | `feature/notation` |
| 模型假设 | `modules/12_assumptions/` | `feature/assumptions` |
| 问题一 | `modules/20_q1/` | `feature/q1` |
| 问题二 | `modules/30_q2/` | `feature/q2` |
| 问题三 | `modules/40_q3/` | `feature/q3` |
| 问题四 | `modules/50_q4/` | `feature/q4` |
| 模型评价 | `modules/60_evaluation/` | `feature/evaluation` |
| 参考文献 | `modules/70_references/` | `feature/references` |
| 附录 | `modules/80_appendix/` | `feature/appendix` |
| AI 使用报告 | `modules/90_ai_report/` | `feature/ai-report` |
| 跨问共享代码 | `shared/` | `feature/shared` |
| 标题/目录/页码/模板 | `paper/` | `feature/paper-shell` |
| 官方原始附件 | `data/raw/` | 不随章节移动 |
| 外部补充数据 | `data/external/` | 不随章节移动 |
| 模块待办 | `work/tasks/<模块>.md` | 跟随对应模块分支 |
| 正式交付物 | `output/final/` | 仅稳定集成后生成 |
| 废弃路线 | `work/archive/` | 只读归档，不被活动代码引用 |

详细地图见 `docs/RESOURCE_MAP.md`。**路径是固定约定；找文件时先查资源地图和 `workflow.py start` 输出，不重新向队友询问已经固定的位置。**

## 3. 每个问题模块内部固定结构

```text
modules/30_q2/
├─ paper/q2.tex              # 唯一正文源
├─ code/                     # 本问题求解/验证代码
├─ data/processed/           # 本问题派生数据
├─ figures/                  # 正文引用图
│  └─ editable/              # Origin/Excel/AGX 等可编辑图源
├─ tables/                   # 精确结果表
└─ results/registry.csv      # 结果状态、来源、复核状态
```

跨两个及以上问题共用的数值内核进入 `shared/`，禁止在多个问题目录复制。

## 4. 分支规则

长期活动分支只按**责任域**划分，不按人名划分：

```text
main
├─ feature/abstract
├─ feature/restatement
├─ feature/notation
├─ feature/assumptions
├─ feature/q1
├─ feature/q2
├─ feature/q3
├─ feature/q4
├─ feature/evaluation
├─ feature/references
├─ feature/appendix
├─ feature/ai-report
├─ feature/shared
└─ feature/paper-shell
```

一个章节一个分支，一个分支一个固定资源区。不要创建 `feature/张三`、`final2`、`真的final`、第二套 `document.tex`。

题目数少于 4 时，`set_questions.py` 会把多余问题设为 inactive，并从 `paper/main.tex` 的活动输入中注释掉；`bootstrap_worktrees.py` 也不会为 inactive 问题创建活动 worktree。

## 5. 日常 Git 最小操作

开始：

```bash
git status
git fetch origin --prune
git pull --ff-only
python scripts/workflow.py start <模块key>
```

结束：

```bash
python scripts/workflow.py finish <模块key>
git diff
git add <明确需要提交的文件>
git commit -m "feat(q2): 完成……"
git push
```

公共分支禁止无脑 `git push --force`、`git reset --hard`。发生分叉先停止并检查差异。

## 6. 结果状态

问题模块的 `results/registry.csv` 使用：

- `DRAFT`：正在计算/尚未验证；
- `VALIDATED`：代码与数据已复算，等待最终检查；
- `FROZEN`：已完成规定检查，可进入正式论文。

另有 `review_state`：`NEEDS_REVIEW` / `CHECKED`。需要检查时只标记“需要复核”；可由管理员或指定复核成员完成，不绑定某个固定角色。

正文引用的关键数值必须来自 `FROZEN + CHECKED` 结果。模型或代码改变后，受影响结果应回到 `DRAFT`。

## 7. 临时全文 Merge Test

```bash
python scripts/preview_merge.py
```

流程：

```text
fetch origin
→ 从 origin/main 创建 detached 临时 worktree
→ 按配置依次 merge 各独立章节分支
→ feature/paper-shell 最后合入
→ 编译 paper/main.tex
→ final_preflight
→ 打开 PDF
```

它只是演习，不会生成长期汇总分支。真正进入 `main` 应通过明确的稳定集成/PR。

## 8. 给 AI 的规范提示词（队友可直接复制）

将 `<模块key>` 与本次任务替换后直接发送给 AI：

```text
你正在 CUMCM 模块化 Git 仓库中工作，本次模块是 <模块key>，任务是：<任务>。

开始任何修改前必须依次完成：
1. 阅读仓库根目录 AGENTS.md、README.md、docs/RESOURCE_MAP.md。
2. 运行 `python scripts/workflow.py start <模块key>`，读取它输出的当前分支、允许修改路径、固定资源位置和该模块实时待办。
3. 读取 `work/tasks/<模块key>.md`；后续工作必须围绕当前待办推进。若实际工作产生新待办、阻塞项或需要检查项，实时更新这个任务文件，不要只在聊天中记录。
4. 固定资源路径以 `docs/RESOURCE_MAP.md` 和 `config/project.json` 为准。遇到“不知道文件在哪里”时先查询这两个文件及模块目录，不要要求队友重复提供已经固定的路径。
5. 只修改当前模块拥有的路径；跨模块内容先说明依赖，必要时记录到待办，不直接覆盖其他章节。
6. 所有正式数值必须能追溯到当前活动代码/结果文件；不能从旧论文、旧 JSON、截图或范文手抄回正文。
7. 需要人工判断的内容统一标记为“NEEDS_REVIEW/需要复核”，由管理员或指定复核成员检查；不要写成必须由某一个固定角色确认。
8. 不得 force push，不得 reset --hard，不得创建第二套全文 TeX 或新的随意汇总目录。

结束本轮前必须：
1. 更新 `work/tasks/<模块key>.md` 的完成项、剩余项、阻塞项和需要复核项；
2. 运行 `python scripts/workflow.py finish <模块key>`；
3. 检查 `git diff`，确认没有越权修改其他模块；
4. 汇报：本轮改了什么、结果/文件在哪里、还剩什么待办、有哪些需要复核。
```

即使队友忘记复制上面的提示词，根目录仍保留 `AGENTS.md`；支持仓库级指令的 AI 工具可以自动读取它。仓库还提供 `.github/copilot-instructions.md` 作为额外兜底。最稳妥的启动方式仍是让 AI 先执行 `workflow.py start <模块key>`。

## 9. 提交前检查层级

1. `structure_guard.py`：防止仓库骨架、文件所有权、第二套全文源被破坏；
2. `final_preflight.py`：检查未解析引用、TODO/FIXME、结果状态、LaTeX 日志等；
3. 人工检查：模型合理性、结果解释、图表视觉、论文表达。

机器检查用于防灾难性错误，不替代人工判断。

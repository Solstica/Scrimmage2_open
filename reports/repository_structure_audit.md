# run_02 仓库结构审计报告

审计日期：2026-08-06  
审计分支：`feature/q1q2update`  
模式：`AUDIT → REVISE`

## 一、结论

仓库主体模块架构正确，但队友新增材料曾绕过模块所有权，形成“活动正文使用 7.3840 μm、图表包使用 7.7398 μm”的双结果链。此次整理不改变正式模型和冻结数值，只做文件归位、陈旧资产隔离、命名规范化和协作规则补充。

## 二、缺陷分级

### P0

1. `modules/图表/`、`modules/outputs/`、旧 `solve_q1_q2.py` 和相关待办均使用 7.7398 μm 路线，与 `work/result_registry.csv` 登记的 7.384039 μm 冲突。
2. `paper/符号说明.txt` 来自 Exe1 人口题，包含人口变量和题目专属措辞，违反本场禁止复用规则。
3. 混合 `document.*` 正由队友调整，当前不得作为正式模块正文或结果源。

### P1

1. Q1/Q2 过程笔记混放在 `modules/*/construction/`，不属于可提交正文、代码、图或表。
2. 可编辑图源、渲染图和结果工作簿混放于通用目录，无法确定问题所有权和结果状态。
3. 根目录 `fix/` 缺少任务状态、负责人和结果口径约束。
4. `output/pdf/` 存在乱码命名的历史 PDF，容易误交付。

### P2

1. 大量文件使用“图表、总表、示意图1”等含糊名称。
2. Origin/AGX 等可编辑源未与论文渲染图分层。
3. 缺少面向 AI 的强制目录与提交约定。

## 三、已执行调整

- Q1 示意图成品规范为 `modules/20_q1/figures/q1_interference_schematic.png`。
- Q1 示意图可编辑源归入 `modules/20_q1/figures/editable/`。
- Q1/Q2 建模过程笔记分别归入 `work/questions/Q1/` 和 `work/questions/Q2/`。
- 7.7398 μm 旧代码、Excel、图表工程和结果归档至 `work/archive/stale_q2_7p7398/`，文件名统一为 `q2_*` 英文蛇形格式。
- 团队待办迁至 `work/team_tasks/<member>/{todo,done}/`。
- Exe1 人口符号文件从活动仓库删除；可从 Git 历史恢复，但不得复用。
- 乱码历史 PDF 归档至 `work/archive/legacy_outputs/`，正式交付路径保持唯一。
- `scripts/build_paper.ps1` 改用 Unicode 码点构造中文交付文件名，避免 Windows PowerShell 5.1 将 UTF-8 无 BOM 脚本中的“真题解析”误读为乱码并重新生成错误文件。

## 四、暂缓项目

以下文件由队友正在编辑，本轮冻结：

- `modules/document.tex`
- `modules/document.pdf`
- `output/results/document.tex`
- `output/results/document.pdf`
- `output/图/` 下被该文档引用的七张 PNG 及其 OPJU 源

冻结解除后应执行：

1. 按 Q1、Q2、Q3 拆入对应模块，或作为个人合稿移入 `work/drafts/`；
2. 重新生成使用 7.384039 μm 冻结结果的 Q2 图；
3. 将正式 PNG 放入 `modules/30_q2/figures/`，OPJU 放入 `figures/editable/`；
4. 更新 LaTeX 引用并删除 `output/图/` 通用目录；
5. 重新编译并更新 PDF 哈希绑定。

## 五、事实门禁

- 正式 Q2 厚度：`7.384039 μm`。
- 旧归档厚度：`7.739796... μm`，状态为 `STALE/ARCHIVED`。
- `work/archive/` 不得被活动正文、构建脚本或结果注册表引用。
- 本轮未修改 `modules/20_q1/paper/q1.tex`、`modules/30_q2/paper/q2.tex` 或冻结结果。

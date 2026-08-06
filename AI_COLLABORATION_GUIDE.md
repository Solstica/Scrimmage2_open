# 队友 AI 仓库协作规范

本文件是本仓库中所有 AI、自动化脚本和协作者的强制工作约定。开始任何任务前，先读取 `README.md`、`ARCHITECTURE.md`、本文件以及当前问题的 `work/questions/Q*/` 状态文件。

## 1. 当前事实基线

- 项目：CUMCM 2025 B 题，训练编号 `run_02`。
- 正式结果的唯一登记源：`work/result_registry.csv`。
- 正式数值输出：`output/results/analysis_results.json`。
- 当前问题二冻结主厚度为 `7.384039 μm`。任何 `7.7398 μm`、`7.7390 μm` 或 `7.40±0.12 μm` 资产均属于陈旧路线，不得写入活动正文、摘要、结论或正式图表。
- `work/archive/` 中的内容只用于追溯，禁止被论文、构建脚本或结果注册表引用。

## 2. 动手前必须执行

```powershell
git status --short --branch
git log --graph --decorate --oneline --all -n 20
```

必须确认：

1. 当前分支属于本任务；
2. 没有覆盖队友未提交修改；
3. 一个对话只维护一个任务分支和一组明确文件；
4. 未经用户明确要求，不推送、不强制推送、不删除远程分支；
5. 禁止 `git reset --hard` 和未经确认的批量覆盖；
6. 错误历史上的单个有效提交使用 `cherry-pick` 移植，不直接合并整条错误分支。

## 3. 目录所有权

| 内容 | 正确位置 |
|---|---|
| 摘要正文 | `modules/00_abstract/paper/abstract.tex` |
| 问题重述、符号、假设 | `modules/10_restatement`、`11_notation`、`12_assumptions` |
| 问题一正文、代码、图、表 | `modules/20_q1/{paper,code,figures,tables}` |
| 问题二正文、代码、图、表 | `modules/30_q2/{paper,code,figures,tables}` |
| 问题三正文、代码、图、表 | `modules/40_q3/{paper,code,figures,tables}` |
| 两问以上共用的数值内核 | `shared/code/` |
| 全项目运行、制图、验证、构建入口 | `scripts/` |
| 可编辑图源（Origin、Adobe、Excel 图工程） | 对应问题的 `figures/editable/` |
| 论文精确数据表 | 对应问题的 `tables/` |
| 正式 JSON 和最终 PDF | `output/results/`、`output/pdf/` |
| 过程笔记、接口、待办、决策 | `work/` |
| 失效或被替代的历史材料 | `work/archive/` |
| 模板和全文整合入口 | `paper/` |
| 可再生中间文件 | `build/`，不得提交 |

不要再创建 `modules/图表/`、`modules/outputs/`、`output/图/`、根目录 `fix/`、`总表.xlsx`、`document2.tex`、`最终版_new.pdf` 等无归属路径或含糊文件名。

## 4. 每问闭环

每个问题必须按以下顺序形成闭环：

1. 问题描述与分析；
2. 预备工作；
3. 具体名称的模型建立与模型汇总；
4. 算法选择、原理、问题绑定步骤、流程图和伪代码；
5. 结果展示；
6. 结果分析、误差/灵敏度/稳定性验证。

跨问复用必须登记在 `work/model_relation_graph.yaml` 和各问 `interface.yaml` 中。共享公式、符号和单位不得在不同问题中悄悄改义。

## 5. 文件命名

- 活动工程文件使用 ASCII 小写蛇形命名，并以问题号开头：`q1_...`、`q2_...`、`q3_...`。
- 渲染图示例：`q2_joint_fit.png`；可编辑源：`figures/editable/q2_joint_fit.opju`。
- 表格示例：`q2_block_bootstrap.csv`。
- 单位写在表头、坐标轴或正文中，不写进含糊文件名。
- 禁止仅使用“图1”“总表”“结果”“最终”“新建文件”等名称。
- 中文用于论文正文、图题和说明；路径名优先英文，避免跨平台乱码。

## 6. 图、表和可编辑源

- PNG/PDF/SVG 等论文可引用成品放入对应问题的 `figures/`。
- OPJU、AGX、PSD、AI、用于制图的 XLSX 放入对应问题的 `figures/editable/`。
- 论文中展示的精确数值表放入对应问题的 `tables/`。
- 图必须有坐标轴、单位、图例和图下注释；表必须使用三线表并在表上方题注。
- 每幅正式图必须能追溯到代码输出或已登记数据；陈旧图不得通过“看起来合理”进入正文。

## 7. 正文与整合

- 各模块 `paper/*.tex` 是唯一活动正文源。
- `paper/main.tex`、`paper/paper_template.tex`、最终摘要、参考文献、结果注册表和正式 PDF 只由整合分支维护。
- 跨问合稿、个人整篇草稿和临时 PDF 放在 `work/drafts/`，不能放在 `modules/` 或 `output/results/`。
- 当前 `modules/document.tex`、`modules/document.pdf`、`output/results/document.*` 由指定队友调整，其他 AI 在解除冻结前不得移动、改写或删除。

## 8. 结果和 STALE 传播

- 只有 `FROZEN` 结果可以进入摘要、正文结论、模型评价和最终 PDF。
- 模型、参数、代码、数据清洗或单位缩放发生变化时，依赖的结果、图、表、摘要槽位和结论全部标记为 `STALE`。
- 重新运行计算与验证后，才可恢复为 `FROZEN`。
- 必须检查“公式—代码—单位—缩放”四联一致；未运行不得声称准确、稳定、鲁棒或优于其他方法。

## 9. 提交前检查

```powershell
conda run -n phasefield python -m unittest -v scripts.test_physics
conda run -n phasefield python -m scripts.verify_results --project .
powershell -ExecutionPolicy Bypass -File .\scripts\build_paper.ps1
git status --short
git diff --check
```

提交说明必须指出：修改的问题编号、模型/结果是否变化、哪些结果被标记为 `STALE`、运行了哪些验证、是否影响 `paper/main.tex`。

## 10. AI 交接模板

```text
任务分支：
文件所有权：
本次修改：
未修改/冻结文件：
结果状态（FROZEN/STALE）：
验证命令与结果：
待人工确认：
是否已推送：
```

若目标位置、结果口径或文件所有权不明确，先停止并询问，不得自行把文件塞入通用目录。

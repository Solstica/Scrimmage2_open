# Scrimmage2 · run_02 真题解析

2025 年全国大学生数学建模竞赛 B 题的模块化真题解析。当前唯一核心路线为 PAPER_A 的重新推导与重算：Q1 双光束正演，Q2 两角度独立反演后平均，Q3 硅 Airy 多光束独立反演及 SiC 回溯。PAPER_B 与旧自有融合模型仅保留在审查和归档中。

## 目录职责

```text
paper/       唯一全文整合入口、cumcmthesis.cls、公共导言和门禁兼容路由
modules/     摘要、重述、符号、假设、问题一至三、评价、参考文献、附录、AI报告
shared/      跨问题共享的光学/反演内核、公共图和环境文件
scripts/     全流程计算、验证、制图与论文构建入口
output/      正式结果 JSON 与最终 PDF
work/        结果、来源、符号、跨问接口及训练状态注册表
reports/     自动门禁、数值复核和人工审计
training/    run_02 训练迭代记录
build/       可再生 LaTeX 中间产物，不提交
```

每个模块内的 `paper/` 是该板块唯一正文编辑源。问题一至三分别拥有自己的 `code/`、`figures/` 和 `tables/`；真正被两问以上共同使用的实现放在 `shared/code/`，避免复制后产生公式漂移。

## Python 复现

在仓库根目录的 PowerShell 中执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& 'C:\Users\admin\miniconda3\shell\condabin\conda-hook.ps1'
conda activate phasefield
python scripts/run_analysis.py --data-dir C:\Users\admin\Documents\CUCCM2026\raw\prob25B --project .
python scripts/test_physics.py
python modules/40_q3/code/solve_q3_paper_a.py --data-dir C:\Users\admin\Documents\CUCCM2026\raw\prob25B --project . --q2-results output/results/q2_paper_a_results.json
```

三问结果分别写入 `q1_validation.json`、`q2_paper_a_results.json` 和 `q3_paper_a_results.json`。旧 `analysis_results.json` 已归档，禁止作为活动事实源。

## LaTeX 构建

全文使用 `paper/cumcmthesis.cls`，友好入口为 `paper/main.tex`，门禁兼容入口为 `paper/paper_template.tex`。两者合成同一篇论文。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_paper.ps1
```

最终 PDF 仅在三问结果全部冻结后重新生成。当前 Q3 的5%数值门禁未通过，旧 PDF 已归档，摘要和最终 PDF 不得定稿。`paper/sections/` 和 `paper/abstract_content.tex` 是构建时生成、被 Git 忽略的门禁兼容镜像，不是正文编辑源。

## 编辑规则

- 一个任务分支只由一个对话维护同一模块。
- `paper/main.tex`、`paper/paper_template.tex`、参考文献、最终摘要、结果注册表和正式输出由整合者维护。
- 模型或代码改变后，将依赖结果标为 `STALE`，重新运行验证后才能恢复为 `FROZEN`。
- 不提交 `build/`、`tmp/`、官方论文 PDF、自有旧模型包或原始对话。

## AI 与队友协作

所有 AI 和自动化协作者在修改仓库前必须阅读 `AI_COLLABORATION_GUIDE.md`。活动结果以 `work/result_registry.csv` 为唯一事实源；`work/archive/` 只用于追溯，禁止被正文、摘要、结论或构建脚本引用。

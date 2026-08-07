# Origin 图表数据重算与导出 TODO

## 目标
保留现有 Origin 图形风格，仅替换旧路线的数据源。编程手负责从最终 PAPER_A 代码生成可直接导入 Origin 的表格，不负责在 Python 中重新画一套替代图。

## 数据唯一来源
- Q2：最终 PAPER_A 单角度反演代码与 `output/results/q2_paper_a_results.json`。
- Q3：最终 PAPER_A Airy 反演代码与 `output/results/q3_paper_a_results.json`。
- 禁止从旧 PNG 手工读数、从旧 document.tex 抄数、从 stale/archive 结果回填。

## 输出要求
每张 Origin 图至少给出一个对应的 `.xlsx` 或 `.csv`，列名必须可读，并包含：
- 横坐标；
- 各系列纵坐标；
- 必要的分组/角度/模型标签；
- 生成脚本或数据来源说明。

建议目录：
- `modules/30_q2/figures/editable/`
- `modules/40_q3/figures/editable/`

Q2 当前 `modules/图表/` 中的 01--14 Excel 表应逐步迁入 Q2 模块；不要继续把问题二专属数据放在根级“图表”目录。

## Q3 特别要求
Q3 的 `.opju` 工程继续保留。更新时优先使用现有工程替换数据列，不重新搭图。若工程内部仍引用旧表，替换后必须检查图例、坐标范围、辅助线和数据标签。

## Q2 Origin 工程缺口
当前 Git bundle 中能看到 Q2 的 Excel 数据表和 PNG，但没有看到 Q2 对应的 `.opju/.opj` 工程文件。如果这些图确实由 Origin 制作，请立即从论文手/制图人员电脑上找到并提交到：
`modules/30_q2/figures/editable/origin/`
否则后续只剩 PNG + Excel，无法完整保留 Origin 排版。

## 验收
重算完成后运行正式结果链验证，并人工抽查关键厚度：
- Q2：7.8566 / 7.6230 / 7.7398 μm；
- Q3：3.2480 / 3.1875 / 3.2178 μm。
完成后将对应任务移动到 `fix/编程手/done/`。

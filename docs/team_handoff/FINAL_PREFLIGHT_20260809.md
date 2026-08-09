# 终稿 Preflight 与 Q3 相位诊断交接（2026-08-09）

## 1. 使用场景

本检查用于论文各章节已经交给论文手之后的最终质量控制，不替代正文写作，也不改变 Q1/Q2/Q3 的冻结模型和数值口径。

推荐始终在一次新的全文 merge-test 上运行：

```bash
git fetch origin --prune
bash <(git show origin/feature/paper-common-final:preview_merge.sh)
```

最新版 `preview_merge.sh` 在全文编译完成后会自动执行：

```bash
python scripts/final_preflight.py --post-build
```

因此正常情况下无需再单独运行。

## 2. 输出含义

- `[FAIL]`：提交前必须处理，包括旧版正式数值、未解析引用、重复 label、分页结构错误和关键图尺寸错误；
- `[WARN]`：人工检查，包括内部工程口吻、Overfull hbox、正文页数超过 27 页、可选诊断无法执行等；
- `[INFO]`：记录通过项和诊断指标，不要求修改正文。

`final_preflight.py` 还会调用现有 `check_writing_quality.py`，并在环境允许时自动运行 Q3 峰谷位置诊断。

## 3. Q3 峰谷/相位位置诊断

诊断脚本：

```text
modules/40_q3/code/export_q3_phase_alignment.py
```

输入为冻结的 10°、15° Airy 拟合 CSV，不重新拟合任何参数。脚本对实测光谱和 Airy 拟合曲线采用相同平滑、峰谷识别规则，再进行同类型最近邻匹配，输出：

- 实测/拟合峰谷数量；
- 成功匹配数量；
- 匹配峰谷波数位置 MAE；
- 最大绝对位置偏差。

输出文件：

```text
modules/40_q3/tables/q3_phase_alignment.csv
```

该诊断仅用于回答“15° 幅值拟合较弱时，主要干涉条纹位置是否仍被模型捕捉”。只有在 10°、15° 两角度的峰谷位置误差均足够小且人工检查匹配没有明显错配时，才可在正文增加一行相位位置结果；否则不进入正文，不改变当前厚度结论。

若自动运行因本机缺少 SciPy 等依赖失败，可在建模环境中单独执行：

```bash
python modules/40_q3/code/export_q3_phase_alignment.py
```

## 4. Q3 固定硅背景参数来源

见：

```text
docs/team_handoff/Q3_PARAMETER_PROVENANCE_AUDIT.md
```

当前尚未核实到能够逐项对应整组固定双振子常数的同行评议原始参数表。正式论文可以引用 Li (1980)、Humlícek & Vojtěchovský (1985)、Moore et al. (2022) 支持硅红外光学常数和解析介电函数建模背景，但不要把整组精确常数直接归为其中任意一篇文献给出。

## 5. 当前冻结数值防回退

Preflight 会阻止以下旧版结果重新进入正式正文：

- SiC：`7.3840`、`7.3747`、`7.3943`；
- Si：`3.3960`、`3.2178`；
- 旧 SiC 多光束修正量：`0.000088`。

当前正式厚度仍为：

- SiC：`7.7398 μm`；
- Si：`3.2175 μm`。

## 6. 版式终检

全文提交前确认：

1. 摘要、目录不计正文页码，问题重述从第 1 页开始；
2. 正文（问题重述至模型评价结束）目标不超过 27 页；
3. 参考文献、附录、AI 使用报告分别另起一页；
4. 附录在目录中只展开一级标题，不出现 `7.5` 一类二级编号；
5. Origin 单小图约 `0.44\textwidth`，双面板组合图约 `0.88\textwidth`，总体流程图约 `1.0\textwidth`；
6. Q3 参数可辨识性 PNG 本身为双面板图，必须按 `0.88\textwidth` 插入。

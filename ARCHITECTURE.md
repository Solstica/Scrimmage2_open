# 模块化论文架构

## 单一编辑源

论文各板块只在 `modules/<编号_模块>/paper/` 编辑。`paper/sections/` 与 `paper/abstract_content.tex` 是构建时生成且被 Git 忽略的兼容镜像，用来适配现有 Skill 的固定目录门禁；`scripts/build_paper.ps1` 会在每次编译前覆盖同步，禁止直接编辑这些镜像。

## 跨问共享原则

- 只服务一问的代码、图、表归对应模块。
- 服务两问及以上的数值内核归 `shared/code/`。
- 生成全项目资产和执行总验证的入口归 `scripts/`。
- 正式交付物归 `output/`；`build/` 只保存可再生中间文件。

## LaTeX 引用规则

所有路径以编译工作目录 `paper/` 为基准：

```tex
\input{../modules/30_q2/paper/q2.tex}
\includegraphics{../modules/30_q2/figures/q2_10deg_paper_a_fit.png}
\lstinputlisting{../modules/30_q2/code/example.py}
```

主文稿通过兼容路由载入各模块，因此模块正文中的图路径仍按上述规则书写。

## 文件所有权

| 路径 | 所有者职责 |
|---|---|
| `modules/00_abstract` | 摘要六槽位压缩后的正文 |
| `modules/10_restatement`–`12_assumptions` | 前置部分 |
| `modules/20_q1`、`30_q2`、`40_q3` | 各问闭环与独有资产 |
| `modules/50_evaluation`–`80_ai_report` | 后置部分 |
| `shared` | 跨问公共内核，不得在模块内复制 |
| `paper` | 模板与整合，不承载模块正文 |
| `work` | 状态与溯源真值 |
| `output` | 可提交的正式产物 |

## 可编辑图源与归档

- 论文引用的 PNG/PDF/SVG 放入对应问题的 `figures/`。
- Origin、AGX、Excel 图工程等可编辑源放入对应问题的 `figures/editable/`。
- 精确结果表放入对应问题的 `tables/`。
- 被替代或结果口径冲突的材料统一放入 `work/archive/`，活动正文和构建脚本不得引用。
- 团队任务统一放入 `work/team_tasks/<member>/{todo,done}/`。

## 临时冻结区

`modules/document.*`、`output/results/document.*` 与 `output/图/` 当前由指定队友调整。解除冻结前，其他协作者和 AI 不得移动、改写或删除；后续迁移方案见 `work/document_migration_pending.md`。

完整 AI 协作规则见 `AI_COLLABORATION_GUIDE.md`。

## 当前结果依赖链

```text
Q1 PAPER_A双光束物理核
        ↓
Q2 10°与15°独立拟合 → 平均7.7398 μm
        ↓
Q3读取Q2 JSON及哈希 → SiC第三束回溯
Q3硅Airy结果 → REVIEW_REQUIRED → 阻断摘要与PDF
```

`work/archive/fusion_80_20_20260806/`中的代码、图表、结果和PDF均为STALE，只可复盘，不得被活动构建入口读取。

# Route execution bundle

- route: `full_paper`
- domain: `A`
- task_zh: 将run_02切换为PAPER_A唯一主体并按Q1/Q2/Q3独立分支重建代码结果图表正文与门禁

> This file is generated from the exact mandatory source files. Read this bundle before writing. Do not rely on filenames alone.


---

## FILE: `SKILL.md`

---
name: cumcm-paper-writing-chenjianye-v3-4-training-rc
version: 3.4.0-rc1
language: en-control/zh-CN-output
description: Deterministic CUMCM paper-writing and four-training-run iteration skill based on Prof. Chen Jianye's 2026 course, annotated exemplar, explicit intermediate state, cross-question relation checks, literature-impact rollback, feasibility review, reusable LaTeX assets, guided function menu, and fail-closed rendering gates.
---

# CUMCM Paper Writing Skill - Chen Jianye Course Edition v3.4 Training RC

## 0. Non-negotiable operating model

This skill uses **English for executable control instructions** and **Chinese for teacher evidence, structured content, and final paper prose**. Do not write a complete English paper and translate it into Chinese. Build structured facts first, then write Chinese directly.

The course requirements are the default operating standard. Do not dilute them with generic competition-paper templates. Do not silently trade them off against external conventions unless the user explicitly requests a separate comparison.

The system is **fail-closed**:

- If a mandatory rule file cannot be opened, stop and report `E_LOAD_REQUIRED_FILE`.
- If required intermediate files do not exist, do not jump to the final draft.
- If model results are not frozen, do not finalize the abstract, title, keywords, conclusion, or model evaluation.
- If a gate fails, revise and rerun it. Never deliver while a `MUST` gate is failing.
- Hidden reasoning is not evidence of workflow completion. Only saved intermediate artifacts count.

## 1. Mandatory first actions for every task

1. Open this file.
2. If the user's requested function is ambiguous, run `python scripts/menu.py --list`, show the compact Chinese numbered menu, and ask for one function number. Do not force the menu when the requested operation is already explicit.
3. Open `control/task_router.yaml`.
4. Run `scripts/record_load.py` for the selected route. For A/B/C-specific work, pass `--domain A`, `--domain B`, `--domain C`, or `--domain mixed`.
5. The command creates `work/route_bundle.md`, which embeds the exact content of every mandatory rule and workflow file for the route. Open and read this single bundle before writing. Do not rely on filenames or links alone.
6. Run `gates/check_load_log.py`. It verifies the route, domain, source hashes, bundle hash, and bundle completeness. A missing, stale, fabricated, or incomplete bundle stops the task.
7. Determine the operating mode: `PLAN`, `DRAFT`, `REVISE`, or `AUDIT`.
8. Run the route preconditions before writing.

If the active project does not exist, run:

```bash
python scripts/init_project.py /path/to/project --questions <N>
```

Then record the route before writing:

```bash
python scripts/record_load.py --project /path/to/project --skill-root . --route <route> --domain <A|B|C|mixed> --task "<task in Chinese>"
```

## 2. Critical teacher rules embedded at the top level

These rules remain active even if secondary files are unavailable.

### 2.1 Abstract

- The abstract and keywords must fit on one rendered A4 page.
- Use the course's three-part structure: short overview, one paragraph per question, optional innovation paragraph.
- The overview is at most 3 rendered lines; the exemplar baseline is 2 lines.
- Every question paragraph must first be built from six explicit slots: central sentence, preliminary work, mathematical model, solution algorithm, numerical/qualitative result, result analysis.
- Save the six-slot additive draft before compression. Direct final-draft generation is forbidden.
- Each final question paragraph should occupy 4-6 rendered lines in the baseline LaTeX template; 6 is the hard maximum.
- No figures, tables, citations, display equations, inline math delimiters, unexplained single-letter variables, or information absent from the body.
- Numerical results must be written as normal Chinese prose with units, not as standalone equations.
- Important central sentences, model names, and key results are bolded selectively.
- Keywords: 3-6 items in the order research problem -> specific model -> algorithm. Generic keywords such as “优化模型”, “预测模型”, or “评价模型” fail the specificity gate.

### 2.2 Every question unit

Each question must contain, in order:

1. Problem description and analysis;
2. Preliminary work;
3. Model formulation;
4. Algorithm design and solution;
5. Result presentation;
6. Result analysis.

The analysis must be inside the corresponding question. Each question must contain a **specific model title** and a **model summary**. Missing model summary is treated as an incomplete model.

For an optimization model, present decision variables, objective function, constraints, and model summary in that order. Move long derivations to preliminary work.

### 2.3 Algorithm

When a question genuinely uses an algorithm, the algorithm section must separately contain:

- selection rationale;
- very short principle description;
- steps bound to this problem's variables, objective, and constraints;
- a color flowchart;
- genuine pseudocode;
- full runnable code in the appendix.

A step table is not pseudocode. A generic algorithm encyclopedia fails. Analytic derivation and direct-calculation questions may declare `algorithm.required: false`, but must record a concrete exemption reason and a derivation/calculation artifact. Never create placeholder flowcharts or pseudocode to bypass the gate.

### 2.4 Results and validation

- Map every result to a question requirement.
- Present key results centrally and bold the decisive values.
- Every figure and table must be explained in prose.
- Every question contains a result-analysis part.
- Every complete paper contains at least one explicit sensitivity analysis in a prominent position.
- Every independent parameterized model should receive its own sensitivity analysis; closely related questions may share one consolidated analysis when coverage is declared.
- A purely analytic question without uncertain inputs may use limiting-case, dimensional, derivation, or numerical-consistency verification instead of an artificial sensitivity plot.
- A/B problems include error analysis.
- Intelligent optimization includes convergence analysis; stochastic methods should also use repeated-run stability.
- Finite-difference PDE solutions include stability and grid/time-step convergence.
- Unrun, unverified, or unfrozen values must never be presented as final results.

### 2.5 Format and end matter

- A4, at least 25 mm margins, no header, 12 pt Chinese body baseline, approximately 19.9 pt baseline spacing.
- Figure caption below; table caption above; tables use three-line structure and do not split across pages.
- Equations are numbered and punctuated as parts of sentences.
- Model evaluation contains summary, strengths, limitations, and improvement/outlook; strengths are longer than limitations.
- At least 10 references, at least 3 English references, favoring recent high-quality sources.
- The submission package includes complete runnable code and an AI-use report.

## 3. Source authority

Use this priority order:

1. Explicit teacher requirement in recording;
2. Explicit requirement on PPT;
3. Explicit teacher approval or criticism of an exemplar;
4. Exemplar layout or structure without teacher comment;
5. Student-made method or tool collections.

Never infer teacher approval merely because a paper won an award. Exemplar annotations use `APPROVED`, `REQUIRED`, `CRITIQUED`, `TOLERATED`, and `OPTIONAL` labels.

## 4. Operating modes

### PLAN
Use when models, data, code outputs, or literature are incomplete. Produce structure, equations to derive, figures to create, required results, and validation tasks. Mark missing work with `TODO[...]`.

### DRAFT
Use only when the relevant inputs are sufficient. Write Chinese paper prose and update registries.

### REVISE
Preserve verified models, values, and conclusions. Reorganize, shorten, define, and remove generic AI prose. Do not alter frozen results.

### AUDIT
Report defects by severity before editing:

- `P0`: missing answer, inconsistent model/result, fabricated value/source, invalid model closure;
- `P1`: missing assumption, constraint, parameter source, validation, or model summary;
- `P2`: teacher-structure, title, figure, table, formula, notation, or style violation;
- `P3`: optional differentiation, combined visual, or extension.

## 5. Required project state

A multi-question or full-paper project must contain:

```text
work/
  load_log.yaml
  route_bundle.md
  paper_state.yaml
  symbol_registry.csv
  result_registry.csv
  source_registry.csv
  decision_log.md
  questions/Q*/question_plan.yaml
  questions/Q*/interface.yaml
  questions/Q*/feasibility_review.yaml
  model_relation_graph.yaml
  literature_impact_log.yaml
  validation_plan.yaml
  abstract_slots.yaml
  abstract_additive_zh.md
  abstract_compressed_zh.md
  title_builder.yaml
reports/
  gate_report.json
  final_audit_zh.md
build/
```

Only `FROZEN` results may propagate into the abstract, conclusion, title, keywords, and model evaluation. Any model/code change marks dependent results `STALE`.

## 6. Deterministic workflow

For a full paper, execute `workflows/01_full_paper.md` in order. Before large-scale coding, complete `workflows/07_model_relation.md`, `workflows/08_literature_impact.md`, and `workflows/09_feasibility.md`. For one question, execute `workflows/02_question_unit.md`. For an abstract, execute `workflows/03_abstract.md` without skipping any artifact. The additive draft must preserve all slot markers after typography normalization, the compressed draft must be observably shorter, and `scripts/build_abstract_tex.py` must generate the LaTeX source from the compressed draft.

The final prose generation sequence is:

1. English control instructions;
2. structured Chinese facts in YAML/CSV;
3. Chinese additive draft;
4. Chinese compressed draft;
5. Chinese author-style revision;
6. LaTeX compilation;
7. rendered Chinese gates;
8. final delivery.

Do not request or claim “English hidden thinking”. Only observable files and gate reports matter.

## 7. Style layer

Load `profiles/chinese_style_default.md` after technical content passes. A user-provided style profile may replace it. Style revision must not change equations, symbols, values, units, uncertainty statements, or conclusions. After style revision, rerun all relevant gates.

## 8. Gate execution

From the skill root:

```bash
python gates/run_all.py --project /path/to/project --skill-root .
```

For abstract-only work:

```bash
python gates/run_all.py --project /path/to/project --skill-root . --scope abstract
```

A final deliverable requires `reports/gate_report.json` with `overall_status: PASS`. Abstract delivery also requires every field in `reports/abstract_manual_review.yaml` to be true. Full-paper delivery requires every field in `reports/manual_review.yaml` to be true. Manual checks must be recorded rather than silently assumed.

## 9. Truthfulness constraints

- Not run -> no numeric result or convergence claim.
- Not tested -> no “stable”, “accurate”, “robust”, or “reliable”.
- Not compared -> no “better than”.
- Original paper not read -> no detailed literature claim.
- Missing evidence -> state the gap.
- Formula, table, figure, text, abstract, conclusion, and code outputs must agree.

## 10. Delivery policy

Deliver only the requested unit and its gate report. Do not flood the user with all internal source files. When packaging a complete skill or paper project, include a manifest and encoding validation report.
## 11. Guided function menu and training-run iteration

The VASPKit-style entry point is:

```bash
python scripts/menu.py --list
python scripts/menu.py --select <number> [arguments]
```

The menu covers project initialization, writing routes, cross-question relations, literature rollback, feasibility, validation planning, four training runs, historical-project asset ingestion, asset validation/promotion, gates, and the status dashboard.

Training is not an autonomous agent that rewrites itself. The stable skill core remains read-only during a run. A training project may create logs, patches, and candidate assets only. Use `workflows/06_training_iteration.md`. Promotion requires validation, at least two successful training reuses, cross-problem-type evidence, and named human approval.

During formal competition work:

- stable assets may be called;
- candidate assets may be generated for later review;
- the skill core and stable manifest must not be modified;
- no candidate is promoted automatically.


---

## FILE: `control/task_router.yaml`

version: 3.4.0-rc1
routes:
  abstract:
    triggers:
    - 摘要
    - 关键词
    - abstract
    - summary
    must_load:
    - rules/source_priority.md
    - rules/title_abstract_keywords.md
    - workflows/03_abstract.md
    - profiles/chinese_style_default.md
    - examples/exemplar/layout_baseline.md
    - examples/exemplar/teacher_annotations.yaml
    - examples/failures/abstract_failure_patterns.md
    preconditions:
    - result_registry_exists
    - referenced_results_are_frozen
  title:
    triggers:
    - 标题
    - 题目
    - title
    must_load:
    - rules/source_priority.md
    - rules/title_abstract_keywords.md
    - templates/content/title_builder.yaml
    - examples/exemplar/teacher_annotations.yaml
  front_matter:
    triggers:
    - 问题重述
    - 符号说明
    - 模型假设
    must_load:
    - rules/source_priority.md
    - rules/front_matter.md
    - rules/visuals_format.md
    - workflows/04_revision.md
  question_unit:
    triggers:
    - 问题一
    - 问题二
    - 问题三
    - 某一问
    - 模型建立与求解
    must_load:
    - rules/source_priority.md
    - rules/teacher_principles.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - workflows/02_question_unit.md
    - examples/exemplar/section_naming_and_structure.md
    - examples/exemplar/flowchart_and_result_visuals.md
    - rules/model_relation.md
    - rules/feasibility.md
    - workflows/07_model_relation.md
    - workflows/09_feasibility.md
    domain_optional: true
  A_problem:
    triggers:
    - A题
    - PDE
    - ODE
    - 微分方程
    - 扩散
    - 流动
    - 反问题
    must_load:
    - rules/source_priority.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/A_pde_inverse.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - workflows/02_question_unit.md
    - rules/model_relation.md
    - rules/feasibility.md
    - workflows/07_model_relation.md
    - workflows/09_feasibility.md
  B_problem:
    triggers:
    - B题
    - 优化
    - 规划
    - 路径
    - 调度
    - 图论
    must_load:
    - rules/source_priority.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/B_optimization.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - workflows/02_question_unit.md
    - rules/model_relation.md
    - rules/feasibility.md
    - workflows/07_model_relation.md
    - workflows/09_feasibility.md
  C_problem:
    triggers:
    - C题
    - 数据
    - 统计
    - 评价
    - 预测
    - 聚类
    - 分类
    must_load:
    - rules/source_priority.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/C_statistics.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - workflows/02_question_unit.md
    - rules/model_relation.md
    - rules/feasibility.md
    - workflows/07_model_relation.md
    - workflows/09_feasibility.md
  visuals:
    triggers:
    - 流程图
    - 图表
    - 公式
    - 排版
    - LaTeX
    - 可视化
    must_load:
    - rules/source_priority.md
    - rules/visuals_format.md
    - examples/exemplar/layout_baseline.md
    - examples/exemplar/flowchart_and_result_visuals.md
    - sources/knowledge/tools_and_visual_platforms.md
  end_matter:
    triggers:
    - 模型评价
    - 参考文献
    - 附录
    - AI使用报告
    must_load:
    - rules/source_priority.md
    - rules/end_matter.md
    - rules/literature.md
    - rules/visuals_format.md
  full_paper:
    triggers:
    - 完整论文
    - 全文
    - 从零写
    - 终稿
    must_load:
    - rules/source_priority.md
    - rules/teacher_principles.md
    - rules/title_abstract_keywords.md
    - rules/front_matter.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - rules/literature.md
    - rules/end_matter.md
    - workflows/01_full_paper.md
    - workflows/03_abstract.md
    - workflows/05_final_audit.md
    - profiles/chinese_style_default.md
    - profiles/team_signature.md
    - examples/exemplar/layout_baseline.md
    - examples/exemplar/section_naming_and_structure.md
    - examples/exemplar/flowchart_and_result_visuals.md
    - examples/exemplar/teacher_annotations.yaml
    - examples/failures/abstract_failure_patterns.md
    - examples/failures/algorithm_failure_patterns.md
    - rules/model_relation.md
    - rules/literature_impact.md
    - rules/feasibility.md
    - rules/training_iteration.md
    - rules/asset_library.md
    - workflows/06_training_iteration.md
    - workflows/07_model_relation.md
    - workflows/08_literature_impact.md
    - workflows/09_feasibility.md
    - workflows/10_asset_learning.md
    domain_optional: true
  audit:
    triggers:
    - 审查
    - 检查
    - 评阅
    - audit
    must_load:
    - rules/source_priority.md
    - rules/teacher_principles.md
    - rules/title_abstract_keywords.md
    - rules/front_matter.md
    - rules/question_structure.md
    - rules/model_general.md
    - rules/algorithm.md
    - rules/results_validation.md
    - rules/visuals_format.md
    - rules/literature.md
    - rules/end_matter.md
    - workflows/05_final_audit.md
    - gates/manual_review.md
    - rules/model_relation.md
    - rules/literature_impact.md
    - rules/feasibility.md
    domain_optional: true
  model_relation:
    triggers:
    - 跨问题关系
    - 模型递进
    - 模型继承
    - 关系图
    must_load:
    - rules/source_priority.md
    - rules/model_relation.md
    - workflows/07_model_relation.md
  literature_impact:
    triggers:
    - 文献推翻
    - 文献影响
    - 模型回溯
    - 新文献
    must_load:
    - rules/source_priority.md
    - rules/literature.md
    - rules/literature_impact.md
    - workflows/08_literature_impact.md
  feasibility:
    triggers:
    - 可实现性
    - 模型复杂度
    - 候选模型
    - 实现难度
    must_load:
    - rules/model_general.md
    - rules/feasibility.md
    - workflows/09_feasibility.md
  validation_plan:
    triggers:
    - 灵敏度安排
    - 结果分析计划
    - 验证计划
    must_load:
    - rules/results_validation.md
    - workflows/02_question_unit.md
  training_iteration:
    triggers:
    - 训练赛迭代
    - 训练复盘
    - 四场训练
    must_load:
    - rules/training_iteration.md
    - rules/asset_library.md
    - workflows/06_training_iteration.md
    - workflows/10_asset_learning.md
  asset_learning:
    triggers:
    - 历史项目反哺
    - 提取模板
    - 资产库
    - 复用LaTeX
    must_load:
    - rules/asset_library.md
    - workflows/10_asset_learning.md
domains:
  A:
    aliases:
    - A
    - PDE
    - inverse
    - differential_equation
    must_load:
    - rules/A_pde_inverse.md
  B:
    aliases:
    - B
    - optimization
    - planning
    must_load:
    - rules/B_optimization.md
  C:
    aliases:
    - C
    - statistics
    - data
    must_load:
    - rules/C_statistics.md
  mixed:
    aliases:
    - mixed
    - MIXED
    must_load:
    - rules/A_pde_inverse.md
    - rules/B_optimization.md
    - rules/C_statistics.md


---

## FILE: `rules/source_priority.md`

# Source priority and evidence labels

Use sources in this order: explicit teacher recording > explicit PPT requirement > explicit teacher comment on exemplar > unreviewed exemplar pattern > student-made knowledge/tool page.

Evidence labels:

- `REQUIRED`: teacher explicitly requires it; enforce as `MUST`.
- `APPROVED`: teacher explicitly praises it; use as preferred implementation.
- `CRITIQUED`: teacher identifies a defect; do not reproduce it.
- `TOLERATED`: acceptable error in an awarded paper, but not a target.
- `OPTIONAL`: useful when relevant, not a quantity-filling requirement.
- `DISPLAY_ONLY`: shown without teacher endorsement.

Never convert `DISPLAY_ONLY` or award status into a hard rule. Source details are in `sources/recording_ppt_alignment.md`, `examples/exemplar/recording_179_alignment.md`, and `rules/teacher_rules.yaml`.


---

## FILE: `rules/teacher_principles.md`

# Teacher doctrine

1. The reader is the evaluator. Save evaluator time through a clear center sentence, compact model summary, concentrated results, and legible visuals.
2. Accuracy precedes novelty. A simple model that answers the problem is preferable to an advanced method without mechanism or data support.
3. Use problem-driven modeling. State the object, task, key difficulty, and required output before selecting a method.
4. Keep one final model per question. Development history may be mentioned only when it explains a necessary refinement.
5. Prefer a general model using variables such as N rather than embedding the problem's specific count into the model definition.
6. Modeling and computation are coupled. If the model cannot be solved, simplify or constrain it; if the result is poor because of excessive simplification, refine it.
7. A paper is judged through assumptions, creativity, result correctness, and clarity. Result correctness must be supported quantitatively.
8. Do not fill sections mechanically. Add analysis only when it answers what could be wrong, why the result is credible, or how the model is used.


---

## FILE: `rules/title_abstract_keywords.md`

# Title, abstract, and keywords

## Title

Build the long title from `research problem + model + algorithm`. Then shorten in this order: remove algorithm first, remove model second, never remove the research problem. Prefer no more than about 20 Chinese characters when possible. Avoid formulas, chemical formulas, subscripts, unexplained abbreviations, slogans, and literary decoration.

The 2025 A exemplar shows that `research problem + algorithms` is acceptable when the model is omitted for length. This is an approved option, not a mandatory pattern.

## Abstract workflow contract

The final abstract is forbidden until these files exist:

- `work/abstract_slots.yaml`;
- `work/abstract_additive_zh.md`;
- `work/abstract_compressed_zh.md`;
- `build/abstract_check.pdf`;
- a passing abstract gate report.

Each question slot contains:

1. `central_sentence` - what this question solves and the final model name;
2. `preliminary_work` - essential data/mechanism preparation only;
3. `model` - mathematical model, without detailed derivation;
4. `algorithm` - solver or numerical method;
5. `result` - concrete answer to the question;
6. `analysis` - one quantitative credibility or interpretation statement.

Write all six slots before prose compression. The additive draft may be long. The compressed paragraph may merge slots, but it must still contain all six functions.

## Abstract source restrictions

- No display or inline formula delimiters.
- No variable names that require the notation table.
- No figures, tables, citations, reference numbers, footnotes, or URLs.
- No strict confidence-interval language unless the body provides the corresponding statistical construction.
- Do not explain why each intermediate step is used. State what was done and what was obtained.
- Use normal Chinese prose for numbers and units, e.g. “厚度为 7.40±0.03 μm”.

## Render limits

Under the baseline template:

- overview: <= 3 lines; exemplar baseline 2;
- each question paragraph: 4-6 lines; hard maximum 6;
- innovation paragraph: 0-2 points and normally <= 2 lines;
- abstract plus keywords: exactly one page maximum.

## Keywords

Use 3-6 items in the order research problem -> specific model -> algorithm. The research object/problem must appear. Reject generic model terms including “优化模型”, “预测模型”, “评价模型”, “数学模型”, and “机器学习模型” unless modified by a specific mechanism or structure.


---

## FILE: `rules/front_matter.md`

# Front matter

The combined rendered length of problem restatement, notation, and assumptions is preferably about 1.5 pages and must not exceed 2 pages under the baseline template.

## Problem restatement

- Use Arabic section numbering.
- Do not copy the problem statement.
- Express the background briefly, then convert the requested tasks into mathematical objects, inputs, outputs, and constraints.
- A background image is optional and must be directly relevant and substantially reworked or composed by the team.
- An Our Work diagram is optional. When used, it must reveal the paper's task or method structure.

## Notation

- Define every symbol at first use even if a notation table exists.
- Use conventional symbols: time t/T, speed v, length l/L, radius r/R, mass m, and so on.
- Use a color three-line table with a unit column when space permits.
- A notation table may be removed if it consumes space without improving readability.

## Assumptions

- Use 3-6 assumptions.
- Cover every simplification that changes the model's domain, geometry, dynamics, boundary conditions, independence, or measurement error.
- Give a short reason for each assumption whenever possible. The exemplar's unreasoned assumptions were tolerated, not praised.
- Do not repeat facts already given by the problem as assumptions.


---

## FILE: `rules/question_structure.md`

# Per-question writing unit

Each question is a closed unit with six ordered parts.

## 1. Problem description and analysis

A short paragraph answers: what must be solved, what is the key object, what makes it difficult, and what route will be used. Place it inside the question, not in a global analysis section. Follow it with a per-question flowchart when the process has multiple stages.

## 2. Preliminary work

Create one subheading per preparation item. Typical items: coordinate system, data cleaning, phase unwrapping, nondimensionalization, mechanism decomposition, long state-variable derivation, parameter range, algorithm encoding. The purpose is to keep the model and solver sections compact.

## 3. Model formulation

Use a specific model name that identifies the object and task. Generic headings such as “模型的建立” fail.

The model section contains definitions, governing equations/objective, constraints/boundary conditions, and a final `模型汇总`. The summary is mandatory for every question and must collect the final model in one location.

## 4. Algorithm design and solution

Separate selection rationale, short principle, problem-bound steps, color flowchart, pseudocode, parameter settings, and implementation details. Full code goes to the appendix.

## 5. Result presentation

Answer the question directly. Put decisive values in a compact colored table or clear figure and bold them in prose. Do not force the evaluator to search plots for the answer.

## 6. Result analysis

Explain correctness, sensitivity, error, stability, convergence, comparison, or mechanism as required by the model. Quantitative analysis is preferred to generic statements.

At completion, write `work/questions/Q*/interface.yaml` containing inputs, outputs, model name, solver, frozen results, figure/table IDs, and unresolved limitations.


---

## FILE: `rules/model_general.md`

# General model formulation

- Every paper contains at least one explicit mathematical model.
- Show one final model per question. Do not present competing models and ask the evaluator to decide.
- Transform the real problem into a recognized mathematical structure when possible, but name and adapt it according to the current mechanism.
- Prefer a general form that can solve a class of problems; substitute the problem's actual values only in the solution stage.
- The model must define variables, domains, parameters, objective/output, constraints or governing conditions, and units.
- Simpler methods are preferred when they explain the mechanism and meet accuracy requirements. Complexity requires a documented need.
- Continuous and discrete models can both be valid. Do not claim superiority merely because one is discrete or easier to compute.
- Innovation is written as `difficulty -> treatment -> measurable consequence`, not as a list of algorithm names.


---

## FILE: `rules/algorithm.md`

# Algorithm writing

The section must include five distinct artifacts.

1. **Selection rationale**: why this solver fits the model, scale, variable types, convexity, smoothness, and constraints.
2. **Principle summary**: normally a few lines, not several pages.
3. **Problem-bound steps**: name the actual decision variables, objective function, constraints, data structures, and stopping rule.
4. **Color flowchart**: readable direction, no unnecessary crossed arrows, clear stages and substeps.
5. **Pseudocode**: language-independent control logic, shorter than source code.

A three-line step table may supplement the section but does not replace pseudocode. Full runnable code and environment details go to the appendix.

For stochastic algorithms, include seed policy, repeated runs, convergence curve, and distribution or summary of objective values. For standard numerical solvers, include tolerance and stopping criteria.


## Algorithm applicability gate

Do not force an algorithm onto a pure analytic derivation or direct calculation. Each question declares `solution_mode` and `algorithm.required`. If exempt, record the reason and the derivation/calculation artifact. Numerical, optimization, statistical, simulation, and hybrid modes require the full algorithm bundle.


---

## FILE: `rules/results_validation.md`

# Results and validation

## Result presentation

- Create a result-to-question map before writing.
- State the answer in prose before or immediately after the table/figure.
- Bold only decisive results.
- Tables carry exact values; figures show trend, structure, spatial relation, uncertainty, or convergence.
- Explain every figure and table. Describe what is visible, why it occurs, and how it answers the question.

## Layered validation policy

- **MUST:** every question contains a result-analysis part.
- **MUST:** every complete paper contains at least one explicit sensitivity analysis in a prominent position.
- **SHOULD:** every independent parameterized model receives its own sensitivity analysis.
- **ALLOWED:** closely related questions sharing a model may use one consolidated sensitivity analysis, provided the covered question IDs, perturbed parameters, outputs, ranges, and conclusions are declared.
- **NOT REQUIRED:** a purely analytic question without uncertain inputs does not need an artificial sensitivity plot. Use derivation verification, limiting-case analysis, dimensional consistency, or numerical consistency instead.

## Validation triggered by model type

- A/B general models: error analysis.
- Intelligent optimization: convergence analysis; stochastic algorithms should also use repeated-run stability.
- Finite-difference PDE: scheme stability and grid/time-step convergence.
- Inverse problem: identifiability, conditioning, regularization sensitivity, or uncertainty.
- Prediction/classification: out-of-sample validation and task-appropriate metrics.
- Spatial/trajectory model: readable 3D result plus projection, local enlargement, or time encoding when needed, followed by prose interpretation.

Do not write “stable”, “accurate”, “robust”, “reliable”, or “better” without a corresponding quantitative test. A sensitivity plot is invalid when its baseline, perturbation range, controlled variables, or response metric is undefined.


---

## FILE: `rules/visuals_format.md`

# Visuals, formulas, and LaTeX format

## Baseline layout

- A4, 25 mm margins, no page header, centered footer page number.
- Chinese body 12 pt; baseline spacing about 19.9 pt; first-line indent 2 em.
- Title about 16 pt bold centered; abstract heading about 14 pt; level-1 heading about 15 pt centered; level-2/3 12 pt bold left.
- Formal CUMCM submission has no table of contents.

## Figures

- At least 10 figures is the teacher's paper-level target, but each figure must add information.
- Prefer vector output.
- Figure caption below.
- Axes, units, legends, labels, and typography must be complete and consistent.
- Three-dimensional plots with poor readability require planar projections, local enlargement, or time encoding.
- Heatmaps are used sparingly and must remain legible.
- Combination figures may increase information density, but do not overcrowd.

## Flowcharts

Use color, clear one-way progression, and layered stages. Avoid unnecessary crossing arrows. A flowchart must match the written method.

## Tables

Use `booktabs` three-line structure, caption above, no page split, unit in header, and notes below when necessary. Light color bands or emphasis are allowed without modifying data.

## Equations

Variables, vectors, and matrices are italic; units, operators, chemical elements, and functions are upright. Number display equations and punctuate them as parts of sentences. Do not use unnumbered display math for important model equations.


---

## FILE: `rules/literature.md`

# Literature research and use

A literature note must record material/problem system, method, observed result, contribution, limitation, and relation to the current question. Do not use “research shows” without identifying the study type and result.

Search recent high-quality sources first, then follow their references for classical methods. Read the original source before stating details. Register every source in `work/source_registry.csv` with purpose and intended citation location.

Literature is used to define mechanisms, parameter ranges, method choice, comparison baselines, or validation criteria. It is not used to decorate the introduction.


---

## FILE: `rules/end_matter.md`

# Model evaluation, references, and appendix

## Model evaluation

Use four parts:

1. concise paper summary;
2. strengths, tied to actual modeling or solution choices;
3. limitations, specific about what may be wrong or outside the model's scope;
4. improvement or outlook, preferably a concrete method for the unresolved issue.

Strengths should be more numerous and longer than limitations. Do not conceal important limitations, but do not write a self-rejection section.

## References

Use at least 10 references and at least 3 English references. Favor recent two-to-three-year high-quality sources while retaining necessary classical sources. Every entry must be cited in the text, and every citation must appear in the list. Use a consistent standard format; DOI and URL are normally omitted from the final list under the course convention.

## Appendix

Include complete runnable programs, code list/table, environment and dependency information, and the AI-use report. Program outputs must match the body. Main results may not be hidden only in the appendix.


---

## FILE: `workflows/01_full_paper.md`

# Full paper workflow

Execute in this order. Each phase creates observable files; no phase may be claimed complete from hidden reasoning.

## Phase 0 - route and load evidence

Initialize the project and record the selected route:

```bash
python scripts/init_project.py <project> --questions <N>
python scripts/record_load.py --project <project> --skill-root <skill-root> --route full_paper --task "<任务说明>"
python gates/check_load_log.py --project <project> --skill-root <skill-root>
```

## Phase 1 - problem, relation, evidence, and feasibility

- Decompose each question into input, output, constraints, required precision, and validation.
- Build `work/model_relation_graph.yaml`; declare inheritance, extension, simplification, replacement, or independence across questions.
- Register data and literature. Use `scripts/registry_upsert.py` rather than hand-editing comma-containing CSV fields.
- Review every model-relevant source in `work/literature_impact_log.yaml`; newly found literature may invalidate current assumptions or results.
- Create per-question plans, interfaces, and feasibility reviews. Select an implementable candidate before large-scale coding.
- Create `work/validation_plan.yaml`: every question needs result analysis, the paper needs explicit sensitivity analysis, and model-type triggers are declared.
- Run relation, literature, feasibility, validation-plan, and registry gates.
- Write the title builder fields but do not freeze the final title.

## Phase 2 - closed question units

For each question, execute `02_question_unit.md`.

- Use a specific model name.
- Include a model summary.
- Freeze results only after required validation.
- Save a question interface before moving to the next question.
- Any model or code change marks dependent results `STALE`.

## Phase 3 - front matter and end matter

- Write problem restatement, notation, and 3-6 justified assumptions.
- Compile `front_matter_check.tex`; the three parts together must occupy no more than 2 pages.
- Write model evaluation with summary, strengths, limitations, and improvement/outlook.
- Supply at least 10 references, including at least 3 English references.
- Supply complete runnable code and the AI-use report.

## Phase 4 - abstract and title

Execute `03_abstract.md` only after all abstracted results are `FROZEN`. Then finalize `work/title_builder.yaml` and make `\title{}` exactly match `final_title`.

## Phase 5 - style and final audit

- Run technical gates.
- Apply the Chinese style profile without changing technical content.
- Compile the front matter, abstract, and full paper.
- Execute `05_final_audit.md`.
- Complete `reports/manual_review.yaml`.
- Deliver only after `reports/gate_report.json` reports `overall_status: PASS`.


---

## FILE: `workflows/03_abstract.md`

# Abstract workflow - observable add then subtract

## Preconditions

- The body already contains the model, method, results, and validation statements being summarized.
- Every abstract result is `FROZEN` in `work/result_registry.csv` and marked `used_in_abstract=true`.
- Run `gates/check_registries.py` before writing the abstract. CSV row misalignment must be corrected first.

## Stage A - six-slot worksheet

Fill `work/abstract_slots.yaml`. Each question has six mandatory functions:

1. central sentence;
2. preliminary work;
3. mathematical model;
4. solution method or algorithm;
5. result;
6. result analysis.

For an analytic derivation question, the fourth slot states the derivation or direct-calculation route. Do not invent an algorithm.

Frozen result anchors need not be byte-for-byte copies. The gate normalizes typography and verifies the registered numerical/content anchor.

```bash
python gates/check_abstract_source.py --project <project> --stage slots
```

## Stage B - additive Chinese draft

Generate, do not manually copy, the additive draft:

```bash
python scripts/build_additive_draft.py --project <project>
```

This file preserves every slot and proves that the six functions were written before compression.

## Stage C - compressed Chinese draft

Write `work/abstract_compressed_zh.md` under the markers `INTRO`, `Q1...Qn`, optional `INNOVATION`, and `KEYWORDS`.

- one paragraph per question;
- each question begins with “针对问题…”;
- final paragraphs retain all frozen result anchors;
- keywords follow problem -> specific model -> method/algorithm;
- the compressed text is observably shorter than the additive draft;
- use Markdown `**...**` only for selective bolding.

```bash
python gates/check_abstract_source.py --project <project> --stage drafts
```

## Stage D - generated LaTeX source

Do not manually translate the compressed draft into custom LaTeX macros. Generate stable tagged content:

```bash
python scripts/build_abstract_tex.py --project <project>
```

The output `paper/abstract_content.tex` contains plain paragraphs inside `% <ABS:...>` blocks and a normal `\keywords{...}` command. The main document uses the standard `abstract` environment from `cumcmthesis.cls`.

```bash
python gates/check_abstract_source.py --project <project> --stage tex
```

## Stage E - compile and measure

```bash
python gates/run_all.py --project <project> --skill-root <skill-root> --scope abstract
```

Required rendered limits:

- overview: at most 3 lines;
- each question: 4-6 lines;
- innovation: at most 2 lines;
- abstract and keywords: one A4 page.

## Stage F - author-style revision

Revise the compressed Chinese draft, not the generated TeX. Preserve values, units, uncertainty qualifiers, model names, and conclusions. Then rerun `build_abstract_tex.py` and all abstract gates.

## Stage G - manual review

Complete every boolean in `reports/abstract_manual_review.yaml`. Automated pass with unfinished manual review is reported as `AUTOMATED_PASS_MANUAL_PENDING`, not as a final pass.


---

## FILE: `workflows/05_final_audit.md`

# Final teacher audit

Audit in this order:

1. Every question is answered and results match the task.
2. Every question has analysis, preliminary work, specific model, algorithm/solution, results, result analysis, and model summary.
3. Optimization models have variables, objective, constraints, and summary.
4. Algorithms have rationale, problem binding, flowchart, pseudocode, and code.
5. Required sensitivity/error/convergence/stability checks exist.
6. Abstract is consistent with body and passes rendered limits.
7. Front matter <= 2 pages.
8. Important results are concentrated, bolded, and explained.
9. Figures/tables/formulas satisfy format rules.
10. Evaluation, references, code appendix, and AI-use report are complete.
11. No stale result or unresolved TODO remains in a final section.
12. Run `gates/run_all.py` and complete manual review fields.


---

## FILE: `profiles/chinese_style_default.md`

# 中文作者修订型表达

技术内容和结构先通过，再执行本层。

## 写法

- 每段直接写对象、变量、方法、结果或限制，不用空泛背景起句。
- 判断必须有具体主语和依据。资料不足时保留缺口。
- 使用动作表达：定义、推导、拟合、计算、比较、扰动、检验、收敛。
- “影响、提升、优化、促进”后写清对象、方向和可测结果。
- 文献结论说明材料/问题体系、方法、观察和适用范围。
- 段落结尾给出具体后果、限制或下一步，不自动升华。

## 避免

- “不是……而是……”的模板化对比；
- “不仅……更是……”“从……到……”等排比；
- “具有重要意义、广阔前景、核心在于、本质上是、主线、抓手、闭环、赋能”；
- “值得注意的是、可以看出、不难发现”；
- 无来源的“研究表明、普遍认为、已有研究指出”；
- 为降低字数而堆名词和缩写；
- 把稳定性范围误写成严格置信区间；
- 机械重复“针对问题X，本文……”。摘要中心句可保留该形式，正文不必反复使用。

## 修订门禁

修订前后逐项比较公式、符号、数值、单位、误差范围和结论。任何变化均需回到技术层确认。修订后重新编译并运行门禁。


---

## FILE: `profiles/team_signature.md`

# Team signature

- Problem-driven rather than method-driven.
- One final model per question, generalized when possible.
- Small, verifiable modules instead of a large coupled model without evidence.
- A/B emphasize numerical correctness and reproducibility.
- C emphasizes data semantics, statistics, and interpretation; use machine learning cautiously.
- Innovation is expressed as a resolved difficulty and measured consequence.
- Visuals carry information and are edited for readability.


---

## FILE: `examples/exemplar/layout_baseline.md`

# 易良禹范文LaTeX版式反推

## 1. 可确认的技术参数

该PDF由LaTeX生成，生产器为 `xdvipdfmx`。页面为A4：595.28 pt × 841.89 pt（210.00 mm × 297.00 mm）。正文主字体为12.01 pt的Fandol宋体，拉丁字符主要使用Times New Roman，数学公式使用Computer Modern。

| 项目 | 测量值 | 后续用途 |
|---|---:|---|
| 左页边距 | 70.9 pt = 25.01 mm | 设为约25 mm |
| 右页边距 | 70.9 pt = 25.00 mm | 设为约25 mm |
| 正文宽度 | 453.5 pt = 159.98 mm | 约38个全角汉字/满行 |
| 正文字号 | 12.01 pt | 对应小四附近 |
| 正文基线距 | 约19.87 pt | 约为字号的1.65倍 |
| 首行缩进 | 24.0 pt | 正好2个12 pt汉字 |
| 论文标题 | 16 pt，加粗，居中 | 摘要页标题 |
| “摘要”标题 | 14 pt，加粗，居中 | 摘要单独标题 |
| 一级标题 | 15 pt，加粗，居中 | “4 问题一模型的建立与求解” |
| 二、三级标题 | 12 pt，加粗，左对齐 | 编号与文字间留空格 |
| 页码 | 页脚居中，基线约803.8 pt | 摘要页不显示页码，正文从1起 |

## 2. 摘要页的实际行数

自动按PDF基线统计得到：

- 总体段：2行；
- 问题一：6行；
- 问题二：5行；
- 问题三：5行；
- 问题四：5行；
- 问题五：4行；
- 亮点段：2行；
- 关键词：1行。

该结果与录音179的评价完全对应：总体段两行，中间各段最多六行，通常四至五行；问题一正好六行，其余为四至五行。以后不能再用“约多少字”替代行数门禁，必须用固定LaTeX模板编译后统计实际基线。

## 3. 前置部分的版面基准

摘要之后的第2-3页包含问题重述、模型假设和符号说明，合计正好两页。问题背景只有两小段并配一幅合成示意图；模型假设3条；符号说明采用带单位列的浅蓝色三线表。

## 4. 推荐模板参数与限制

以下参数可作为新版Skill的默认基准，最终仍以官方模板和当年提交要求为上限：

```yaml
paper: a4
margins_mm: {left: 25, right: 25, top: 25, bottom: 25}
body_font_zh: FandolSong-Regular
body_font_latin: Times New Roman
body_font_size_pt: 12
first_line_indent_em: 2
baseline_skip_pt: 19.9
title_size_pt: 16
abstract_heading_size_pt: 14
level1_size_pt: 15
level2_size_pt: 12
level3_size_pt: 12
figure_caption_position: below
table_caption_position: above
page_number: centered_footer
```

“每行约38字”只适用于纯中文、无加粗、无英文和无数学符号的满行估计。摘要、公式混排和英文术语会改变实际换行，所以最终门禁必须依据渲染页面。


---

## FILE: `examples/exemplar/section_naming_and_structure.md`

# 范文章节命名与结构标注

## 1. 老师明确认可的命名方式

每问一级标题统一采用“问题X模型的建立与求解”。每问内部先写“问题X的描述与分析”，随后直接写具体模型名称。优化问题不使用空泛的“模型的建立”，而写为：

- 单无人机单烟幕弹遮蔽优化模型；
- 单无人机多烟幕弹遮蔽优化模型；
- 多无人机多烟幕弹遮蔽优化模型；
- 多导弹多无人机遮蔽优化模型。

具体模型名称应体现对象、规模或任务，不能只写“优化模型”“预测模型”“评价模型”。

## 2. 计算型问题的推荐结构

```text
问题X模型的建立与求解
  问题X的描述与分析
  [问题X流程图]
  具体计算模型
    子模型/机制1
    子模型/机制2
    判定或状态模型
    输出量计算模型
    模型汇总
  模型求解和结果分析
    离散化或算法准备
    求解步骤
    求解结果
    必要的误差/灵敏度/稳定性分析
```

问题一的“模型汇总”受到老师明确强调。模型汇总应集中给出输入、关键状态方程、判定条件和输出量，不把模型散落在数页推导中。

## 3. 优化型问题的推荐结构

```text
问题X模型的建立与求解
  问题X的描述与分析
  [问题X流程图]
  具体优化模型名称
    决策变量
    目标函数
    约束条件
    模型汇总
  XX算法求解XX模型
    选择理由
    原理简述
    与本题模型结合的步骤
    流程图
    伪代码
  结果分析
  灵敏度分析
  收敛性分析（智能优化必需）
```

老师将“模型汇总”判定为高权重内容：缺少汇总会被视为模型没有完整建立。目标函数的长推导应移入“预备工作”，模型段只保留最终主体、符号解释和必要约束。

## 4. 本范文可保留但不应照抄的地方

- 将算法步骤写成三线表：视觉简洁，可作为一种呈现形式；但不能误称为伪代码，也不能替代流程图和真正伪代码。
- 三维轨迹图：信息完整但可读性一般，应补充二维投影、局部放大或时间编码。
- 模型评价只写优缺点：老师明确指出应补全文小结和改进/展望。
- “优化模型”作为关键词：范围过大，应替换为具体模型名。


---

## FILE: `examples/exemplar/flowchart_and_result_visuals.md`

# 范文流程图与结果图组织方式

## 1. 五幅逐问流程图的共同结构

问题一、二、三、四、五分别在PDF第4、11、17、24、29页给出流程图。共同布局为：

1. 横向排列3-4个阶段；
2. 顶部使用浅黄色箭头形标题标明阶段；
3. 每个阶段用虚线框限定边界；
4. 框内用圆角矩形、椭圆和箭头表示输入、模型、算法和输出；
5. 不同阶段使用浅红、浅蓝、浅绿等低饱和背景色；
6. 图题统一置于图下。

问题一采用“基础参数与运动分析—核心数学模型构建—算法应用求解—结果输出”；问题二采用“优化目标与决策变量定义—约束条件构建—算法求解—结果输出”。后续问题按变量规模和模型扩展调整模块名称。

## 2. 老师评价对应的使用规则

- 每问先写一段短的“描述与分析”，再放流程图；流程图不能替代文字分析。
- 流程图属于该问内容导航，框内应出现本题变量、模型和输出，不得套用通用“初始化—迭代—输出”模板。
- 算法章节还应另设算法流程图。范文只有逐问建模流程图，没有算法专用流程图，因此老师将其列为缺点。
- 流程图的主要作用是压缩结构信息，不应把完整公式或长句塞入图中。

## 3. 结果图的组织

范文对三维运动轨迹采用“3D图+xy/xz/yz投影图”的组合，并在图后逐图解释。该方式适合空间轨迹问题，但新版Skill应增加可读性判断：

- 三维图若遮挡严重、尺度差异大或无法判断时间关系，必须补二维投影、局部放大或时间颜色编码；
- 每幅图后写明图中对象、观察到的现象和该现象对结论的作用；
- 结果图与灵敏度图、收敛曲线分开，不用一幅图承担多个检验任务。


---

## FILE: `examples/exemplar/teacher_annotations.yaml`

version: 2.0
exemplar: "2025 CUMCM A, Yi Liangyu"
source_recording: "standard_recording_179"
labels: [APPROVED, REQUIRED, CRITIQUED, TOLERATED, OPTIONAL]
annotations:
  - id: EXM-TITLE-001
    pages: [1]
    recording: "00:18-00:37"
    label: APPROVED
    statement_zh: "标题保留研究问题和算法，省略模型后仍可接受。"
  - id: EXM-ABS-001
    pages: [1]
    recording: "00:37-01:17"
    label: APPROVED
    statement_zh: "总体段2行；各问4-6行；中心句、结果和重点加粗；最后1条亮点。"
  - id: EXM-KEY-001
    pages: [1]
    recording: "00:55-01:17"
    label: CRITIQUED
    statement_zh: "关键词‘优化模型’过宽。"
  - id: EXM-FRONT-001
    pages: [2,3]
    recording: "01:17-02:18"
    label: APPROVED
    statement_zh: "问题背景短、问题提出简洁、彩色三线符号表含单位，前置部分两页。"
  - id: EXM-ASM-001
    pages: [3]
    recording: "01:57-02:18"
    label: TOLERATED
    statement_zh: "假设未写理由仍可合格，但不覆盖课程中‘建议写理由’的规则。"
  - id: EXM-Q1-001
    pages: [4,10]
    recording: "02:45-03:39"
    label: REQUIRED
    statement_zh: "短问题分析、逐问流程图、具体模型、模型汇总、加粗结果。"
  - id: EXM-OPT-001
    pages: [11,13]
    recording: "03:48-04:28"
    label: REQUIRED
    statement_zh: "优化模型标题写具体名称；依次给出决策变量、目标函数、约束条件和模型汇总。"
  - id: EXM-ALG-001
    pages: [13]
    recording: "04:28-05:12"
    label: CRITIQUED
    statement_zh: "缺少算法选择理由、本题化步骤、算法流程图和真正伪代码。"
  - id: EXM-RES-001
    pages: [14,16]
    recording: "05:35-06:17"
    label: REQUIRED
    statement_zh: "结果加粗，彩色表格，图后解释，灵敏度分析；智能优化补收敛性。"
  - id: EXM-PRE-001
    pages: [17,20,24,26]
    recording: "06:17-07:40"
    label: REQUIRED
    statement_zh: "目标函数推导过长时移入预备工作，模型段保留主体表达。"
  - id: EXM-FORM-001
    pages: [29,34]
    recording: "08:09-08:33"
    label: APPROVED
    statement_zh: "公式编号和句末标点规范；所有问题均需模型汇总。"
  - id: EXM-EVAL-001
    pages: [34]
    recording: "08:33-09:00"
    label: CRITIQUED
    statement_zh: "模型评价缺全文小结和改进/展望。"
  - id: EXM-AI-001
    pages: [35,72]
    recording: "09:00-09:19"
    label: REQUIRED
    statement_zh: "提交论文必须包含AI使用报告。"


---

## FILE: `examples/failures/abstract_failure_patterns.md`

# Abstract failure patterns

1. **Direct final draft**: no six-slot worksheet and no additive draft. Fails `E_MISSING_INTERMEDIATE`.
2. **Miniature body section**: long mechanism derivation and several equations. Fails source gate and rendered line limit.
3. **Unknown variables**: uses `d`, `N`, `rho`, or other notation-table symbols. Replace with normal Chinese result prose.
4. **Pseudo confidence interval**: writes “95% confidence interval” for a perturbation range. Use “模型稳定性范围” unless a formal interval is constructed.
5. **Generic keyword**: “优化模型”. Replace with the specific model name.
6. **Missing result**: says “效果良好” without the numerical or requested qualitative result.
7. **No result analysis**: provides a value but no sensitivity/error/convergence/identifiability conclusion.
8. **Markdown leakage**: `**bold**` or `\(...\)` appears literally in DOCX/LaTeX output.
9. **One-paragraph abstract**: no per-question paragraph boundaries.
10. **Body mismatch**: abstract claims an algorithm or result absent from the body.


---

## FILE: `examples/failures/algorithm_failure_patterns.md`

# Algorithm failure patterns

- Copies generic algorithm steps without current variables, objective, constraints, or stopping rule.
- Calls a step table “pseudocode”.
- Gives no solver-selection reason.
- Uses black-and-white flowchart or crossed arrows that obscure direction.
- Gives only source code in the appendix and no pseudocode in the body.
- Claims faster convergence without repeated runs or a baseline.


---

## FILE: `rules/model_relation.md`

# Cross-question model relation rules

Every question must declare how it relates to the preceding model chain. The relation is not decorative metadata; it controls inheritance, repetition, stale-state propagation, and the paper's overall route.

Allowed relation types:

- `independent`: no mathematical component is inherited;
- `reuse`: the previous model is reused without structural change;
- `extend`: variables, mechanisms, data, or constraints are added;
- `specialize`: the previous model is restricted to a specific case;
- `relax`: an assumption or constraint is removed or weakened;
- `simplify`: a controlled approximation is introduced for tractability;
- `replace`: the previous model is no longer applicable;
- `validate`: the current question validates or compares a previous result.

Requirements:

1. Every question appears as a node in `work/model_relation_graph.yaml`.
2. From Q2 onward, each question has an incoming declared relation, including `independent` when appropriate.
3. Inherited equations, symbols, assumptions, code modules, and results are listed explicitly.
4. Added, removed, or modified components are recorded with a concrete reason.
5. `replace`, `simplify`, `relax`, and `independent` require a non-empty rationale.
6. Shared symbols retain the same meaning and unit. Any deliberate redefinition must use a new symbol or be explicitly justified.
7. The route stated in the abstract and overall-work figure must agree with the graph.
8. Reused derivations should be referenced rather than repeated verbatim.


---

## FILE: `rules/literature_impact.md`

# Literature impact and model rollback rules

Literature is allowed to revise or invalidate the current model. New sources must not be appended only to the bibliography when they alter mechanism, assumptions, parameter ranges, equations, or validation.

Impact levels:

- `no_impact`: reviewed, no change;
- `citation_only`: supports an existing statement;
- `parameter_update`: changes a value or range;
- `assumption_change`: changes a modeling assumption;
- `equation_change`: changes a governing relation;
- `model_revision`: changes model structure;
- `model_replacement`: invalidates the current model.

For every model-relevant source, record an entry or a reviewed-no-impact decision in `work/literature_impact_log.yaml`.

When impact is `parameter_update` or higher:

1. list affected questions and artifacts;
2. list dependent result IDs;
3. mark dependent results, figures, abstract slots, and conclusions `STALE` until recomputed;
4. record the adopted action and reason;
5. rerun the affected validation;
6. resolve the entry before freezing the paper.

A source that contradicts a key assumption cannot be ignored because the old result is convenient.


---

## FILE: `rules/feasibility.md`

# Model complexity and feasibility review

Before implementation, each question must select a candidate model through an explicit feasibility review. Do not use a synthetic weighted score.

Review dimensions:

1. mechanism completeness;
2. data and parameter availability;
3. identifiability or information sufficiency;
4. numerical implementability and expected runtime;
5. available validation path;
6. writing and explanation cost within the paper limit.

Each dimension is `PASS`, `RISK`, or `BLOCK`.

Candidate decisions:

- `ACCEPT`: ready to implement;
- `RISK`: may proceed only with named mitigations and no unresolved blocker;
- `REVISE`: revise before implementation;
- `REJECT`: do not implement in the competition project.

The selected candidate must be `ACCEPT` or a fully mitigated `RISK`, must contain no `BLOCK`, and must declare `implementation_ready: true` before code or final prose is produced.


---

## FILE: `rules/training_iteration.md`

# Four-training-run iteration policy

The skill core is read-only during a run. Training produces logs and candidate assets; rule changes occur only after review.

- Run 1: baseline observation. Collect failures, model relations, literature impacts, feasibility reviews, and candidate assets.
- Run 2: controlled reuse. Compare asset-assisted work with the baseline and check for old-problem leakage.
- Run 3: cross-type validation. Test the mechanisms and assets on a different A/B/C problem type.
- Run 4: release rehearsal. Freeze the core, use only reviewed assets, execute clean builds and final gates.

After each run, create a training review. Only human-approved changes are merged into the next release candidate.


---

## FILE: `rules/asset_library.md`

# Training-derived LaTeX asset library

Reusable assets are learned from completed training projects, never copied blindly from a problem-specific paper.

The pipeline is:

`training project -> candidate extraction -> de-problematization -> parameterization -> dependency check -> isolated validation -> human approval -> stable asset`.

Rules:

- Imported files enter `assets/candidates/`; they never become stable automatically.
- Remove old problem names, numbers, symbols, labels, paths, and conclusions before promotion.
- Every asset has an ID, version, category, source run, parameters, dependencies, applicable scope, prohibited scope, validation record, and rollback version.
- Stable assets must compile or pass the relevant static validation independently.
- Formal competition runs may use stable assets and may create candidates, but may not modify `SKILL.md` or auto-promote assets.
- A candidate should normally succeed in at least two training runs and one cross-problem-type use before stable promotion.


---

## FILE: `workflows/06_training_iteration.md`

# Training-run iteration workflow

1. Initialize a run with `scripts/init_training_run.py`.
2. Freeze the current skill version and asset manifest hash in the run record.
3. Execute the paper workflow; do not edit the stable skill core during the run.
4. Maintain the relation graph, literature-impact log, feasibility reviews, gate report, issue log, and decision log.
5. At the end, run `scripts/ingest_training_project.py` to extract candidate assets.
6. Run `scripts/build_training_review.py` to produce the run review.
7. Compare with previous runs: time, gate failures, repeated defects, asset reuse, and leakage.
8. Human reviewers choose which rule patches and assets become candidates for the next version.
9. Promote an asset only with `scripts/promote_asset.py --approved-by ...` after validation.


---

## FILE: `workflows/07_model_relation.md`

# Cross-question relation workflow

1. Fill all question nodes after problem decomposition.
2. From Q2 onward, classify the relation to the inherited model chain.
3. List inherited and changed equations, symbols, assumptions, code, and results.
4. Check whether a claimed extension actually changes the mathematical model.
5. Record shared-symbol meaning and units.
6. Update the overall paper route and abstract route.
7. Run `gates/check_model_relations.py` before drafting downstream questions and before final delivery.


---

## FILE: `workflows/08_literature_impact.md`

# Literature impact workflow

1. Add and verify the source in `work/source_registry.csv`.
2. Decide whether it is model-relevant.
3. Record its impact in `work/literature_impact_log.yaml`.
4. If the impact changes parameters, assumptions, equations, or model structure, list all dependent artifacts and result IDs.
5. Apply stale propagation with `scripts/apply_literature_impact.py --project <project> --source-id <S-id>`.
6. Revise the model, rerun code, regenerate figures, and update the abstract.
7. After recomputation, resolve with `scripts/resolve_literature_impact.py` and explicit revalidation confirmation.
8. Run `gates/check_literature_impacts.py` before result freezing and final delivery.


---

## FILE: `workflows/09_feasibility.md`

# Model feasibility workflow

1. Create at least one candidate model for each question.
2. Review mechanism, data, identifiability, implementation, validation, and writing cost.
3. Record blockers, risks, mitigations, expected runtime, and required dependencies.
4. Select one candidate.
5. Reject or revise any candidate with an unresolved blocker.
6. Set `implementation_ready: true` only after the solver and validation route are concrete.
7. Run `gates/check_feasibility.py` before large-scale coding or final drafting.


---

## FILE: `workflows/10_asset_learning.md`

# Historical-project and training-asset learning workflow

1. Import a previous project or ZIP with `scripts/ingest_training_project.py`.
2. Review the generated inventory and candidate list.
3. Remove problem-specific names, values, symbols, labels, and paths.
4. Convert reusable parts into parameterized snippets.
5. Declare dependencies and applicability limits.
6. Validate each candidate with `scripts/validate_asset.py`.
7. Reuse it in later training runs and record outcomes.
8. Promote only after human approval with `scripts/promote_asset.py`.


---

## FILE: `rules/A_pde_inverse.md`

# A problem: ODE/PDE and inverse problems

Focus on the physical phenomenon before choosing the equation.

- Diffusion: heat/mass transport without bulk motion; usually parabolic PDE.
- Flow/advection: transport with motion; use conservation and advection terms.
- Inverse problem: infer source, parameter, boundary, initial condition, or geometry from observations.

A PDE model summary should contain:

1. governing equation;
2. domain and coordinates;
3. initial condition;
4. boundary conditions;
5. source and constitutive terms;
6. unknown parameters and observations;
7. identifiability or regularization statement;
8. complete summarized system.

Numerical solution must state grid, time step, discretization, boundary implementation, solver tolerance, and convergence/stability checks. Mature numerical methods are acceptable; novelty is not a substitute for correctness.

Inverse results require sensitivity/identifiability analysis. Do not report a point estimate for a parameter that is not stably identifiable.

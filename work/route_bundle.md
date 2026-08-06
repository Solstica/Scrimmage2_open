# Route execution bundle

- route: `audit`
- domain: `mixed`
- task_zh: 审查并规范化全仓库文件位置，拆分Q1/Q2混合资产，编写队友AI协作规范

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

## FILE: `gates/manual_review.md`

# Manual review fields

Automated gates cannot establish physical correctness or genuine visual quality. Record these fields in `reports/manual_review.yaml`:

- Every question requirement is answered.
- Model mechanism and assumptions are physically/mathematically plausible.
- Parameter sources and units are correct.
- Figures are readable at normal PDF zoom and colors remain distinguishable.
- Flowcharts correspond to the written method.
- Pseudocode corresponds to the implementation.
- Literature claims were checked against original sources.
- Chinese prose reads as an author revision, without promotional or generic AI wording.
- Frozen values are identical across code output, tables, figures, body, abstract, and conclusion.

A reviewer must set each item to `true` before final delivery.


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


---

## FILE: `rules/B_optimization.md`

# B problem: optimization

Use a specific optimization model name. Present:

1. decision variables and domains;
2. objective function with physical meaning;
3. constraints grouped by mechanism/resource/time/geometry;
4. complete model summary.

Select the objective according to the task. For public-service location, mean distance may be appropriate; for emergency service, minimizing the maximum distance may be necessary. State the consequence of the chosen objective.

If using an intelligent optimizer:

- justify why exact/convex/standard solvers are insufficient or unsuitable;
- encode constraints explicitly rather than relying only on penalties when repair/projection is possible;
- give problem-bound pseudocode;
- record population, iterations, bounds, random seeds, stopping rule, and repeated-run statistics;
- include convergence and sensitivity analyses;
- compare with at least one meaningful baseline when claiming improvement.


---

## FILE: `rules/C_statistics.md`

# C problem: data and statistics

Start by identifying data semantics, not by applying a standard cleaning pipeline.

- Compositional data whose components sum to one are dependent and require appropriate transformations.
- In anomaly/health detection, deleting anomalous observations can remove the target signal.
- Missing-value treatment depends on mechanism and variable type; deletion is not the default.
- Standardization, transformation, encoding, discretization, and class balancing require a model-specific reason.

Use AHP cautiously in CUMCM. DEA requires a meaningful input-output structure. Entropy weighting, TOPSIS, variance-maximizing methods, regression, classification, clustering, dimensionality reduction, and time-series models must match the data structure.

Machine learning is not forbidden, but sample size, interpretability, leakage, validation, and mechanism fit must be checked. Do not use LSTM without a genuine sequence structure or Prophet without the corresponding seasonal/holiday mechanism.

Report statistical metrics appropriate to the task and explain their relation to the question, not only their numerical values.

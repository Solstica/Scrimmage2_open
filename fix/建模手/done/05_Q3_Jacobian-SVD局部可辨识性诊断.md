# 建模手任务 05：Q3 Jacobian–SVD 局部可辨识性诊断

## 1. 目标

当前 Q3 正式模型为四参数 Airy 反演：

\[
\boldsymbol p
=
(d,n_3,\log_{10}N,\log_{10}\Gamma_e).
\]

正文已经观察到部分附属参数触及边界，因此不能把
\(N,\Gamma_e\) 当作可靠材料学定量结果。

本任务进一步用 Jacobian–SVD 回答：

> 当前光谱对四个参数分别有多强的局部敏感性？参数方向之间是否近线性相关？厚度方向是否比载流子/碰撞率方向更可辨？

本诊断**不修改主反演结果**，只增强“为何固定振子背景量、为何只解释厚度”的数学依据。

---

## 2. 残差与 Jacobian

对某一角度，设观测反射率为 \(R_i^{\mathrm{obs}}\)，Airy预测为

\[
R_i(\boldsymbol p),
\]

定义残差

\[
r_i(\boldsymbol p)
=
R_i(\boldsymbol p)-R_i^{\mathrm{obs}}.
\]

在最优解 \(\widehat{\boldsymbol p}\) 处计算

\[
J_{ij}
=
\left.
\frac{\partial r_i}{\partial p_j}
\right|_{\widehat{\boldsymbol p}}.
\]

当前 `scipy.optimize.least_squares` 已经返回 `answer.jac`，因此首选直接使用优化器 Jacobian，而不是重新手工差分。

---

## 3. 为什么不能直接用 raw cond(J)

四个参数尺度差别很大：

- \(d\)：μm；
- \(n_3\)：无量纲；
- \(\log_{10}N\)：decade；
- \(\log_{10}\Gamma_e\)：decade。

直接对原始 \(J\) 做条件数会受参数单位影响。

因此必须同时报告两类量：

### A. 列绝对敏感性

对第 \(j\) 列，

\[
S_j=
\frac{\|J_{\cdot j}\|_2}{\sqrt m}.
\]

它描述“每改变一个原参数单位，平均残差变化多大”。

该量保留，但只作辅助，因为单位不同。

### B. 列归一化后的相关性 Jacobian

定义

\[
\widetilde J_{\cdot j}
=
\frac{J_{\cdot j}}
{\max(\|J_{\cdot j}\|_2,\epsilon)}.
\]

于是每列二范数为 1，消除了参数单位和一阶幅值差异。

对

\[
\widetilde J
=
U\Sigma V^\mathsf T
\]

做 SVD：

\[
\sigma_1\ge\sigma_2\ge\sigma_3\ge\sigma_4\ge0.
\]

定义列相关条件数

\[
\kappa_{\mathrm{corr}}
=
\frac{\sigma_1}{\sigma_4}.
\]

这主要回答“参数方向是否高度共线”。

**注意：列归一化会掩盖某参数本身几乎没有绝对敏感性的情况，所以必须与 \(S_j\) 同时报。**

---

## 4. 更适合论文的无量纲局部敏感度

为了同时保留幅值信息并减少单位影响，定义参数的局部特征尺度

\[
s_j=
\begin{cases}
\max(|\hat p_j|,10^{-6}), & j=d,n_3,\\
1, & j=\log_{10}N,\log_{10}\Gamma_e.
\end{cases}
\]

构造

\[
J^{(\mathrm{rel})}
=
J\,\mathrm{diag}(s_1,s_2,s_3,s_4).
\]

含义：

- \(d,n_3\) 按相对变化尺度；
- 两个 log 参数按“1 decade”尺度。

定义

\[
S_j^{(\mathrm{rel})}
=
\frac{
\|J^{(\mathrm{rel})}_{\cdot j}\|_2
}{
\sqrt m
}.
\]

论文主图优先画 \(S_j^{(\mathrm{rel})}\)，同时用列归一化 SVD 判断相关性。

---

## 5. 右奇异向量：识别“不可辨组合”

若最小奇异值对应右奇异向量为

\[
\boldsymbol v_{\min}
=
(v_d,v_{n_3},v_N,v_\Gamma)^\mathsf T,
\]

则组合

\[
v_d\,\delta d+
v_{n_3}\,\delta n_3+
v_N\,\delta\log N+
v_\Gamma\,\delta\log\Gamma_e
\]

是局部最难从光谱区分的参数变化方向。

建议输出绝对权重

\[
w_j=
\frac{|v_j|}{\sum_k|v_k|}.
\]

如果 \(w_N,w_\Gamma\) 占主导，而 \(w_d\) 较小，则可直接支持：

> 近零敏感方向主要由载流子浓度与碰撞率耦合构成，厚度并非主要退化方向。

如果实际结果不是这样，则必须如实报告，不能预设结论。

---

## 6. 参数相关矩阵

定义 Gauss–Newton 信息矩阵

\[
H=J^\mathsf TJ.
\]

在不作严格统计置信区间解释的前提下，可用伪逆

\[
C=(J^\mathsf TJ)^+
\]

构造局部相关系数

\[
\rho_{ij}
=
\frac{C_{ij}}
{\sqrt{C_{ii}C_{jj}}}.
\]

只解释“局部参数耦合”，不称为严格概率置信区间，因为：
- 存在参数边界；
- 残差未证明独立同方差高斯；
- 模型为非线性。

---

## 7. 边界活跃参数要单独标记

当前参数边界为

\[
d\in[0.1,100],
\quad
n_3\in[2,5],
\quad
\log_{10}N\in[12,20],
\quad
\log_{10}\Gamma_e\in[11,15].
\]

若某参数距离边界小于当前代码定义的比例阈值，则标记 `boundary_hit=True`。

对于边界活跃参数：

- SVD仍可作为前向灵敏度诊断；
- 但不要用普通协方差公式宣称“95%置信区间”。

---

## 8. Q3 Origin 图 19 的最终定义

将“参数可辨识性气泡图”改造成一个完全可复现的诊断图。

### 推荐图形：角度 × 参数 气泡图

每个角度四个点：

- X：参数名 \(d,n_3,\log N,\log\Gamma_e\)
- Y：\(\log_{10}S_j^{(\mathrm{rel})}\)
- 气泡大小：最弱右奇异向量权重 \(w_j\)
- 描边：
  - 实线：未触边
  - 红/特殊描边：触边

这样一张图同时表达：
1. 参数本身对反射率是否敏感；
2. 参数是否参与近不可辨方向；
3. 是否触边。

比把“RMSE、条件数、触边数”硬塞到不同轴更有数学意义。

---

## 9. Q3 Origin 图 23：多初值盆地

当前每角度只有 6 个确定性初值。

必须输出所有 6 次拟合，不仅是排序后的厚度和 RMSE。

建议：

- X：最终厚度
- Y：RMSE（百分点）
- 颜色：角度
- 标签：seed_id
- 气泡大小：若多个初值收敛到同一盆地，则为 basin_count

盆地可先按最简单可复现原则：
以厚度排序，并按“最终厚度数值相同到代码数值精度/明显聚集”分组。
若需要自动聚类，必须先由建模手另行确认，编程手不要自行选阈值。

---

## 10. 可选增强：固定背景 vs 扩展背景的敏感性比较

这是**可选项，不是当前必须项**。

若要进一步支撑“为什么不释放振子背景量”，可以在当前最优解处只做前向有限差分，不进行 11 参数重新拟合。

基础 4 参数：

\[
(d,n_3,\log N,\log\Gamma_e).
\]

额外背景参数：

\[
(\varepsilon_\infty,
A_1,\lambda_1,\Gamma_1,
A_2,\lambda_2,\Gamma_2).
\]

形成扩展 Jacobian

\[
J_{11}.
\]

比较：
- \(J_4\) 的奇异谱；
- \(J_{11}\) 的奇异谱；
- 新增背景参数后是否出现更多近零奇异值。

如果明显恶化，可作为附录或模型评价中的强证据。

**禁止**为了做该诊断而重新将 11 参数全部释放优化并据此改主厚度。

---

## 11. 编程手必须导出的数据

### `q3_identifiability_summary.xlsx`

每角度一行：

```text
angle_deg
n_points
thickness_um
substrate_index
log10N
log10Gamma
rmse_percentage_point
boundary_hits
jacobian_rank_numeric
jacobian_cond_raw
jacobian_cond_column_normalized
sigma1_colnorm
sigma2_colnorm
sigma3_colnorm
sigma4_colnorm
```

### `q3_identifiability_parameters.xlsx`

每角度 × 参数：

```text
angle_deg
parameter
estimate
column_norm_raw
relative_scale
relative_sensitivity
weakest_right_singular_weight
boundary_hit
```

### `q3_identifiability_correlation.xlsx`

长表：

```text
angle_deg
parameter_i
parameter_j
local_correlation
```

### `q3_multistart.xlsx`

```text
angle_deg
seed_id
d_init_um
n3_init
log10N_init
log10Gamma_init
d_final_um
n3_final
log10N_final
log10Gamma_final
rmse_percentage_point
success
boundary_hits
```

---

## 12. 数值计算注意

### SVD 容差

数值秩用

\[
\tau
=
\sigma_1\,
\max(m,n)\,
\varepsilon_{\mathrm{mach}}
\]

判断：

\[
\operatorname{rank}(J)
=
\#\{\sigma_i>\tau\}.
\]

### 条件数

若最小奇异值低于 \(\tau\)，条件数报告为 `inf`，不能人为截断成一个“好看的大数”。

### 输出精度

诊断表至少保存：
- 参数：8–10 有效数字；
- 奇异值：科学计数法，至少 8 有效数字；
- 相关系数：6 位小数。

---

## 13. 建模手验收

1. Jacobian 必须来自正式 Airy residual；
2. 10°、15°分别计算；
3. 不能把两个角度拼成一个共享参数联合 Jacobian；
4. 所有 4 参数都输出；
5. raw cond 与 normalized cond 分开，不能只报一个无说明条件数；
6. 边界参数不做普通置信区间解释；
7. 最弱奇异方向必须输出右奇异向量权重；
8. 若结果不支持“厚度最可辨”，论文必须如实调整表述；
9. frozen 厚度不能因为诊断结果重新拟合改变；
10. `verify_paper_a_results.py` 仍需 PASS。

---

## 14. 论文可用的最终结论模板

仅当实际计算支持时：

> 在两个入射角的最优Airy解处，本文进一步构造反射率残差关于 \(d,n_3,\log_{10}N,\log_{10}\Gamma_e\) 的局部Jacobian，并通过尺度化奇异值分解评价参数可辨识性。结果表明，最弱奇异方向主要由载流子浓度与碰撞率的耦合构成，而厚度方向保持更高的局部灵敏度；结合附属参数触边现象，说明继续释放振子背景量将进一步放大逆问题病态性。因此本文将厚度作为主要测量结论，而不对边界处载流子参数作材料学定量解释。

若最弱方向不是 \(N\)-\(\Gamma_e\)，删除对应句子，以实际右奇异向量为准。

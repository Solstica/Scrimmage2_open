
# 三、问题二：双角度共享参数非线性最小二乘模型

## 3.1 问题分析

附件 1 和附件 2 对应同一块 SiC 晶圆片，仅入射角分别为 (10^\circ) 和 (15^\circ)。因此两组数据应共享：

[
d,\quad N,\quad n_3,\quad A,\quad B_j,\quad C_j.
]

范文 A 分别拟合两个角度，再对两个厚度取平均；其结果为 (7.8522\ \mu\mathrm m) 和 (7.6233\ \mu\mathrm m)。 范文 B 指出同一晶圆的厚度和色散参数应完全相同，并采用双角度联合拟合。

因此问题二只修改范文 A 的求解组织：

[
\boxed{
\text{两个角度分别拟合}
\quad\longrightarrow\quad
\text{两个角度共享物理参数联合拟合}.
}
]

---

## 3.2 数据预处理

### 第一步：读取和单位转换

读取附件 1、附件 2 的

[
(\sigma,R_{\mathrm{obs}})
]

数据，并将百分数反射率转换为小数：

[
R_{\mathrm{obs}}
\leftarrow
\frac{R_{\mathrm{obs}}}{100}.
]

波长转换为

[
\lambda=\frac{10^4}{\sigma}.
]

### 第二步：选择拟合波段

主拟合波段取

[
\boxed{
2500\le\sigma\le3300\ \mathrm{cm^{-1}}.
}
]

实际光谱在该区域条纹规整、基线变化缓慢，范文 A 也采用这一范围，以降低低波数强吸收对拟合的影响。

### 第三步：异常点处理

只删除明确的缺失值或孤立测量异常，不对条纹做 Hilbert 变换、相位解包裹或复杂基线扣除。必要时采用轻微平滑仅用于峰谷初值，不使用平滑后的数据代替原始数据拟合。

---

## 3.3 决策变量

完整待估参数写为

[
\boxed{
\boldsymbol\theta
=================

\left(
d,N,n_3,A,B_1,\ldots,B_J,
C_1,\ldots,C_J
\right).
}
]

其中：

* (d) 是最终目标；
* (N) 回应题目中载流子浓度对折射率的影响；
* (n_3) 为选定波段内的常数衬底折射率；
* (A,B_j,C_j) 为外延层 Sellmeier 参数；
* (m^*) 固定为文献值；
* 弱吸收区不把 (\Gamma) 作为自由参数。

范文 A 的代码实际上同时拟合了厚度、衬底折射率、Sellmeier 参数、载流子浓度、阻尼及有效质量，参数数量较多。 本文仅删除不能与 (N) 独立分离的 (m^*)，并不改变 Sellmeier–Drude 模型。

---

## 3.4 双角度联合目标函数

记两个入射角为

[
i_1=10^\circ,
\qquad
i_2=15^\circ.
]

对第 (k) 个角度、第 (j) 个波数点，理论反射率为

[
R_{\mathrm{th}}
\left(
\sigma_{kj},i_k;\boldsymbol\theta
\right).
]

残差定义为

[
e_{kj}(\boldsymbol\theta)
=========================

## R_{kj}^{\mathrm{obs}}

R_{\mathrm{th}}
\left(
\sigma_{kj},i_k;\boldsymbol\theta
\right).
]

联合残差平方和为

[
\boxed{
J(\boldsymbol\theta)
====================

\sum_{k=1}^{2}
\sum_{j=1}^{m_k}
e_{kj}^2(\boldsymbol\theta).
}
]

最终参数估计为

[
\boxed{
\widehat{\boldsymbol\theta}
===========================

\arg\min_{\boldsymbol\theta\in\Omega}
J(\boldsymbol\theta).
}
]

其中 (\Omega) 为物理参数可行域。

这与范文 B 的双角度共享参数联合拟合形式一致，但正算模型仍沿用范文 A 的 Sellmeier–Drude–Fresnel 模型。

---

## 3.5 参数约束

为防止非线性拟合得到无物理意义结果，设置：

[
d_{\min}\le d\le d_{\max},
]

[
N_{\min}\le N\le N_{\max},
]

[
n_{3,\min}\le n_3\le n_{3,\max},
]

以及 Sellmeier 参数的材料合理范围。

还需在全部拟合波长上满足

[
n_2^2(\lambda,N)>0,
]

[
\lambda^2\ne C_j,
]

并保证折射角为实数：

[
\left|
\frac{n_1\sin i}{n_2}
\right|
\le1.
]

参数上下界依据材料文献值和范文初值附近的合理范围设置，不使用极宽无约束搜索。

---

# 四、问题二的求解算法

## 4.1 厚度初值

由相邻同类条纹间距 (\Delta\sigma) 可得到厚度近似：

[
\boxed{
d_0
\approx
\frac{5000}
{
n_2(\bar\sigma)\cos\gamma,
\Delta\sigma
}
\quad(\mu\mathrm m).
}
]

该式只用于确定初始厚度和搜索范围，不作为最终结果。

根据实际数据的条纹间距，初值位于约 (7\ \mu\mathrm m) 量级，因此可设置合理厚度搜索范围，例如

[
6.5\le d\le8.5\ \mu\mathrm m.
]

---

## 4.2 分步拟合

为保持与范文 A 的程序结构接近，同时降低初值敏感性，采用两阶段拟合。

### 阶段一：固定背景色散

固定文献或范文登记的

[
A,B_j,C_j,m^*,
]

联合拟合

[
d,\quad N,\quad n_3.
]

该阶段主要确定正确的条纹周期和厚度盆地。

### 阶段二：约束释放色散参数

以上一阶段结果为初值，在窄物理边界内释放

[
A,B_j,C_j,
]

对完整参数向量进行非线性最小二乘精修。

范文 A 的代码同样采用先固定晶格色散参数、再逐步释放参数的分阶段策略。

---

## 4.3 多初值非线性最小二乘

目标函数随厚度具有周期性，单次局部优化可能落入错误条纹级次。因此从若干组厚度和载流子浓度初值启动有界最小二乘：

[
\boldsymbol\theta_0^{(1)},
\boldsymbol\theta_0^{(2)},
\ldots,
\boldsymbol\theta_0^{(L)}.
]

每组初值求得一个局部解：

[
\widehat{\boldsymbol\theta}^{(\ell)}
====================================

\arg\min J(\boldsymbol\theta).
]

选取满足物理约束且目标函数最小的解：

[
\boxed{
\widehat{\boldsymbol\theta}
===========================

\arg\min_{\ell}
J\left(
\widehat{\boldsymbol\theta}^{(\ell)}
\right).
}
]

求解器仍采用普通有界非线性最小二乘，如 trust-region reflective 方法。范文 A 也指出非线性最小二乘对初值较敏感。

---

## 4.4 算法流程

```text
输入：附件1、附件2波数—反射率数据，入射角10°和15°

1. 读取数据并将反射率百分数转为小数；
2. 截取2500～3300 cm⁻¹弱吸收波段；
3. 由峰谷间距估计厚度初值和搜索范围；
4. 给定Sellmeier–Drude参数，计算n₂(λ,N)；
5. 根据Snell定律计算外延层和衬底折射角；
6. 分别计算s、p偏振的Fresnel系数；
7. 计算两束反射光振幅及非偏振理论反射率；
8. 将10°、15°残差合并为联合最小二乘目标；
9. 第一阶段固定Sellmeier参数，拟合d、N、n₃；
10. 第二阶段在窄边界内释放色散参数并精修；
11. 使用多组初值重复拟合，选取最小物理可行解；
12. 输出厚度、辅助材料参数、拟合曲线和可靠性指标。
```

---

# 五、结果可靠性分析

问题二不能只报告一个最小二乘厚度，应至少完成以下六项。

## 5.1 拟合优度

分别计算 10°、15°以及合并数据的：

[
\mathrm{RMSE}
=============

\sqrt{
\frac1m\sum_{j=1}^{m}
\left(
R_j^{\mathrm{obs}}-R_j^{\mathrm{fit}}
\right)^2
},
]

[
R^2
===

1-
\frac{
\sum_j
(R_j^{\mathrm{obs}}-R_j^{\mathrm{fit}})^2
}{
\sum_j
(R_j^{\mathrm{obs}}-\overline R^{\mathrm{obs}})^2
},
]

以及必要时的 MAPE。

范文 A 使用 RMSE、MAPE、(R^2) 和 Q–Q 图检验拟合效果。

---

## 5.2 残差分析

绘制

[
e_{kj}
======

## R_{kj}^{\mathrm{obs}}

R_{kj}^{\mathrm{fit}}
]

随波数变化的曲线。

重点检查：

* 残差是否围绕零随机分布；
* 是否仍存在与干涉条纹同周期的振荡；
* 两个角度是否出现相同方向的系统误差；
* 波段两端是否明显偏离。

若残差存在明显周期性，需要在问题三检验多光束影响，不能只依靠 (R^2) 宣称模型可靠。

---

## 5.3 双角度一致性

最终厚度以联合拟合结果为准，同时分别对 10°、15°做单独拟合：

[
d_{10},\qquad d_{15}.
]

比较

[
|d_{10}-d_{15}|
]

以及二者与联合厚度

[
d_{\mathrm{joint}}
]

的差异。

单角度结果只用于一致性检查，不再简单取算术平均。

---

## 5.4 多初值稳定性

检查不同初值是否收敛到同一厚度盆地。若多个明显不同的厚度具有相近残差，需要进一步缩小参数范围或利用峰谷初值确认干涉级次。

---

## 5.5 参数边界与相关性

检查：

* 是否有 Sellmeier 参数或载流子浓度到达边界；
* 参数标准误差是否过大；
* 厚度 (d) 与载流子浓度 (N) 是否高度相关。

由最优点处 Jacobian (J_\theta) 可估计协方差：

[
\operatorname{Cov}
(\widehat{\boldsymbol\theta})
\approx
\widehat s^2
\left(
J_\theta^{\mathsf T}
J_\theta
\right)^{-1}.
]

进一步计算

[
\operatorname{corr}(d,N).
]

若 (N) 对初值、边界或波段非常敏感，则仍保留 Drude 项，但不把 (N) 解释成高精度材料测量结果。范文 B 的部分色散参数相对误差很高或达到边界，说明这一检查有必要。

---

## 5.6 波段敏感性

在主波段

[
2500\sim3300\ \mathrm{cm^{-1}}
]

附近改变上下界，例如比较：

[
2400\sim3300,
\quad
2500\sim3300,
\quad
2500\sim3400\ \mathrm{cm^{-1}}.
]

若厚度变化很小，说明结果不依赖某个特定波段端点；若载流子浓度变化很大而厚度基本稳定，则只把 (N) 作为折射率修正参数。

---

# 六、问题二模型汇总

## 决策变量

[
\boxed{
\boldsymbol\theta
=================

(d,N,n_3,A,{B_j,C_j}).
}
]

其中 (m^*) 固定，(\Gamma) 在弱吸收主波段中不参与自由拟合。

## 目标函数

[
\boxed{
\min_{\boldsymbol\theta}
\left{
\sum_j
\left[
R_{10,j}^{\mathrm{obs}}
-----------------------

R_{\mathrm{th}}
(\sigma_{10,j},10^\circ;\boldsymbol\theta)
\right]^2
+
\sum_j
\left[
R_{15,j}^{\mathrm{obs}}
-----------------------

R_{\mathrm{th}}
(\sigma_{15,j},15^\circ;\boldsymbol\theta)
\right]^2
\right}.
}
]

## 约束

[
\boxed{
\begin{cases}
d_{\min}\le d\le d_{\max},\
N_{\min}\le N\le N_{\max},\
n_{3,\min}\le n_3\le n_{3,\max},\
n_2^2(\lambda,N)>0,\
\lambda^2\ne C_j,\
\text{全部参数位于材料合理范围内}.
\end{cases}
}
]

## 输出

[
\boxed{
\widehat d,\quad
\widehat N,\quad
\widehat n_3,\quad
\widehat A,\widehat B_j,\widehat C_j.
}
]

其中：

* (\widehat d) 是问题二的主要结果；
* 其他参数用于构成折射率模型和评价拟合；
* 若 (N) 可辨识性不足，不将其作为高精度物理结论。

---

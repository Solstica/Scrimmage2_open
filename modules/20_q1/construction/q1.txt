下面按已经锁定的路线梳理：

[
\boxed{
\text{范文 A 的 Sellmeier–Drude–Fresnel 模型}
+
\text{范文 B 的双角度联合拟合}
+
\text{相位口径与参数冗余修正}
}
]

问题一的公式、推导顺序和篇幅以范文 A 为准；问题二仍使用普通非线性最小二乘，只将“两个角度分别拟合后取平均”改为“同一晶圆共享参数联合拟合”。题目要求模型同时联系波长、折射率、入射角和厚度，并考虑折射率随载流子浓度与波长变化。

---

# 一、统一符号与模型假设

## 1. 符号

空气、外延层和衬底依次编号为 (1,2,3)。

| 符号               | 含义                           |
| ---------------- | ---------------------------- |
| (d)              | 外延层厚度，(\mu\mathrm m)         |
| (n_1)            | 空气折射率，取 (n_1=1)              |
| (n_2(\lambda,N)) | 外延层折射率                       |
| (n_3)            | 衬底折射率                        |
| (i)              | 空气侧入射角                       |
| (\gamma)         | 外延层内折射角                      |
| (\eta)           | 衬底内折射角                       |
| (\lambda)        | 真空波长，(\mu\mathrm m)          |
| (\sigma)         | 波数，(\mathrm{cm^{-1}})        |
| (N)              | 外延层载流子浓度，(\mathrm{cm^{-3}})  |
| (m^*)            | 载流子有效质量                      |
| (r_{ij}^{(u)})   | 介质 (i\to j) 的 Fresnel 振幅反射系数 |
| (t_{ij}^{(u)})   | 介质 (i\to j) 的 Fresnel 振幅透射系数 |
| (u)              | 偏振状态，(u\in{s,p})             |
| (R)              | 非偏振反射率                       |

波数和波长满足

[
\boxed{
\lambda(\mu\mathrm m)=\frac{10^4}{\sigma(\mathrm{cm^{-1}})}.
}
]

---

## 2. 模型假设

1. 外延层厚度均匀，上表面和外延层—衬底界面光滑且相互平行。
2. 外延层和衬底在测量区域内均匀，载流子浓度不随横向位置变化。
3. 问题一只保留上表面直接反射光和第一次到达衬底界面后返回的反射光。
4. 入射光为非偏振光，理论反射率取 s、p 两偏振反射率的算术平均。
5. SiC 主反演选取 (2500\sim3300\ \mathrm{cm^{-1}}) 弱吸收波段，因此问题二中忽略折射率虚部；低波数强吸收区不参与厚度主拟合。
6. 衬底折射率 (n_3) 在选定窄波段内近似为常数。
7. 有效质量 (m^*) 取文献或材料登记值，不与载流子浓度 (N) 同时自由拟合。

范文 A 同样采用平行均匀外延层、高波数弱吸收、非偏振平均和常数衬底折射率，并选择 (2500\sim3300\ \mathrm{cm^{-1}}) 进行拟合。

---

# 二、问题一：Sellmeier–Drude 双光束 Fresnel 测厚模型

## 2.1 问题分析

问题一考虑两束反射光：

* 光束 1：在空气—外延层界面直接反射；
* 光束 2：透入外延层，在外延层—衬底界面反射一次，再从上表面透射出来。

两束光的光程差决定条纹周期，外延层折射率决定传播速度和折射角，两个界面的 Fresnel 系数决定两束光的振幅。范文 A 采用“光程差—相位差—Drude/Sellmeier 色散—Fresnel 反射率”的完整顺序，我们沿用该结构。

---

## 2.2 两束光的光程差

设外延层厚度为 (d)，空气侧入射角为 (i)，外延层折射角为 (\gamma)。

由 Snell 定律，

[
\boxed{
n_1\sin i=n_2\sin\gamma.
}
]

两束光在外延层中产生的传播光程差为

[
\boxed{
\delta=2n_2d\cos\gamma.
}
]

范文 A 通过几何光路推导了同一结果。

由 Snell 定律还可消去 (\gamma)：

[
n_2\cos\gamma
=============

\sqrt{n_2^2-n_1^2\sin^2 i}.
]

因此

[
\boxed{
\delta
======

2d\sqrt{n_2^2-n_1^2\sin^2 i}.
}
]

空气折射率取 (n_1=1) 后，

[
\delta
======

2d\sqrt{n_2^2-\sin^2 i}.
]

---

## 2.3 相位差

传播光程差产生的相位差为

[
\Phi
====

\frac{2\pi}{\lambda}\delta.
]

代入 (\delta)，得到

[
\boxed{
\Phi
====

\frac{4\pi n_2d\cos\gamma}{\lambda}.
}
]

用波数表示时，若 (d) 以 (\mu\mathrm m) 为单位，

[
\boxed{
\Phi
====

4\pi\times10^{-4}
\sigma d,n_2\cos\gamma.
}
]

范文 A 在该式之后固定加入 (+\pi) 表示半波损失。 本文采用带正负号的 Fresnel 振幅系数，界面反射产生的 (0) 或 (\pi) 相变已经包含在 (r_{ij}) 的符号中，故不再额外加入固定的 (\pi)。

这一修订只统一相位口径，不改变范文的干涉结构。

---

## 2.4 外延层的 Sellmeier–Drude 折射率

### 2.4.1 Sellmeier 背景色散

外延层晶格与束缚电子的本征色散采用 Sellmeier 方程：

[
\boxed{
n_{\mathrm S}^2(\lambda)
========================

A+
\sum_{j=1}^{J}
\frac{B_j\lambda^2}
{\lambda^2-C_j}.
}
]

其中：

* (A) 为常数项；
* (B_j,C_j) 为材料色散参数；
* (J) 与范文 A 采用的 Sellmeier 项数保持一致。

范文 A 使用 Sellmeier 方程描述折射率的波长依赖。

---

### 2.4.2 Drude 自由载流子修正

自由载流子响应采用 Drude 模型：

[
\boxed{
\varepsilon_{\mathrm D}(\omega)
===============================

-\frac{\omega_p^2}
{\omega(\omega+i\Gamma)}.
}
]

等离子体频率与载流子浓度满足

[
\boxed{
\omega_p^2
==========

\frac{Ne^2}
{\varepsilon_0m^*}.
}
]

其中：

* (e) 为元电荷；
* (\varepsilon_0) 为真空介电常数；
* (m^*) 为有效质量；
* (\Gamma) 为载流子碰撞频率。

范文 A 也由 Drude 模型和 Sellmeier 方程在介电函数层面构造外延层折射率。

因此一般色散模型为

[
\boxed{
\widetilde n_2^{,2}(\lambda,N)
==============================

A+
\sum_{j=1}^{J}
\frac{B_j\lambda^2}
{\lambda^2-C_j}
---------------

\frac{\omega_p^2}
{\omega(\omega+i\Gamma)}.
}
]

---

### 2.4.3 问题二弱吸收近似

在 (2500\sim3300\ \mathrm{cm^{-1}}) 区间内，采用范文 A 的弱吸收处理，忽略折射率虚部及 Drude 阻尼的主要影响：

[
\omega(\omega+i\Gamma)
\approx\omega^2.
]

于是

[
\boxed{
n_2^2(\lambda,N)
================

A+
\sum_{j=1}^{J}
\frac{B_j\lambda^2}
{\lambda^2-C_j}
---------------

\frac{\omega_p^2}{\omega^2}.
}
]

再由

[
\omega=\frac{2\pi c}{\lambda_m},
\qquad
\lambda_m=10^{-6}\lambda_{\mu\mathrm m},
]

可得

[
\boxed{
n_2^2(\lambda,N)
================

A+
\sum_{j=1}^{J}
\frac{B_j\lambda^2}
{\lambda^2-C_j}
---------------

\frac{Ne^2\lambda_m^2}
{4\pi^2c^2\varepsilon_0m^*}.
}
]

这条公式明确实现了题目要求：

[
\boxed{
n_2=n_2(\lambda,N).
}
]

---

## 2.5 两个界面的 Fresnel 系数

令

[
\theta_1=i,\qquad
\theta_2=\gamma,\qquad
\theta_3=\eta.
]

各层折射角满足

[
n_1\sin\theta_1
===============

# n_2\sin\theta_2

n_3\sin\theta_3.
]

本文统一以界面切向电场为振幅变量。

### s 偏振

介质 (i\to j) 的振幅反射和透射系数为

[
\boxed{
r_{ij}^{(s)}
============

\frac{
n_i\cos\theta_i-n_j\cos\theta_j
}{
n_i\cos\theta_i+n_j\cos\theta_j
},
}
]

[
\boxed{
t_{ij}^{(s)}
============

\frac{
2n_i\cos\theta_i
}{
n_i\cos\theta_i+n_j\cos\theta_j
}.
}
]

### p 偏振

[
\boxed{
r_{ij}^{(p)}
============

\frac{
n_j\cos\theta_i-n_i\cos\theta_j
}{
n_j\cos\theta_i+n_i\cos\theta_j
},
}
]

[
\boxed{
t_{ij}^{(p)}
============

\frac{
2n_i\cos\theta_i
}{
n_j\cos\theta_i+n_i\cos\theta_j
}.
}
]

范文 A 同样分别计算 s、p 偏振的 Fresnel 振幅系数。

---

## 2.6 两束反射光的振幅叠加

对于偏振态 (u\in{s,p})，第一束光的振幅反射系数为

[
r_{12}^{(u)}.
]

第二束光依次经过：

[
1\to2\text{ 透射}
\rightarrow
2\to3\text{ 反射}
\rightarrow
2\to1\text{ 透射}.
]

因此第二束光的振幅为

[
t_{12}^{(u)}
r_{23}^{(u)}
t_{21}^{(u)}
e^{i\Phi}.
]

只考虑第一次内部反射时，总振幅反射系数为

[
\boxed{
\rho_u
======

r_{12}^{(u)}
+
t_{12}^{(u)}
r_{23}^{(u)}
t_{21}^{(u)}
e^{i\Phi}.
}
]

对应反射率为

[
\boxed{
R_u=|\rho_u|^2.
}
]

非偏振入射光的理论反射率为

[
\boxed{
R_{\mathrm{th}}
(\sigma,i;\boldsymbol\theta)
============================

\frac{
R_s+R_p
}{2}.
}
]

其中物理参数集合可写为

[
\boldsymbol\theta
=================

\left(
d,N,n_3,A,{B_j,C_j}
\right).
]

范文 A 和范文 B 的连续反射率模型均采用两束复振幅相加，再对 s、p 反射率取平均。

---

## 2.7 问题一模型汇总

[
\boxed{
\begin{cases}
n_1\sin i=n_2\sin\gamma,[1mm]
\delta=2n_2d\cos\gamma,[1mm]
\Phi=\dfrac{4\pi n_2d\cos\gamma}{\lambda},[3mm]
n_2^2(\lambda,N)
================

A+\displaystyle\sum_j
\dfrac{B_j\lambda^2}{\lambda^2-C_j}
-\dfrac{Ne^2\lambda_m^2}
{4\pi^2c^2\varepsilon_0m^*},[4mm]
\rho_u
======

r_{12}^{(u)}
+t_{12}^{(u)}r_{23}^{(u)}t_{21}^{(u)}
e^{i\Phi},
\quad u=s,p,[2mm]
R_{\mathrm{th}}
===============

\dfrac{|\rho_s|^2+|\rho_p|^2}{2}.
\end{cases}
}
]

问题一的输入为

[
\sigma,\ i,\ d,\ N,\ n_3,\ \text{Sellmeier 参数},
]

输出为可与附件直接比较的理论反射率

[
R_{\mathrm{th}}(\sigma,i).
]

厚度 (d) 通过传播相位 (\Phi) 控制干涉条纹周期。

---

# 七、问题一与问题二的连接

[
\boxed{
\begin{aligned}
\text{问题一：}\quad&
(\sigma,i,d,N,\text{色散参数})
\longrightarrow
R_{\mathrm{th}};
[1mm]
\text{问题二：}\quad&
R_{\mathrm{obs}}
\longrightarrow
\arg\min
|R_{\mathrm{obs}}-R_{\mathrm{th}}|^2
\longrightarrow
\widehat d.
\end{aligned}
}
]

完整流程为

[
\boxed{
\text{光程差}
\rightarrow
\text{Sellmeier–Drude 折射率}
\rightarrow
\text{Fresnel 双光束反射率}
\rightarrow
\text{双角度联合非线性最小二乘}
\rightarrow
\text{厚度与可靠性}.
}
]

这一版与范文 A 的核心公式、建模顺序和算法难度基本一致；微调仅包括：

1. 带符号 Fresnel 系数与半波损失口径统一；
2. 固定 (m^*)，避免 (N/m^*) 参数冗余；
3. 用范文 B 的双角度共享参数联合拟合替代分别拟合后取平均；
4. 增加多初值、边界、相关性和波段稳定性检查。

原有复 Fresnel、Hilbert 相位和谐波回归结果均不再继承；问题一、二的数值需按照这套模型重新计算。

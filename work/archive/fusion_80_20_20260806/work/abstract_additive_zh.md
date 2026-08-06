# 摘要加法稿

<!-- OVERVIEW.research_problem -->
研究红外干涉光谱反演碳化硅与硅外延层厚度的问题

<!-- OVERVIEW.overall_route -->
以复Fresnel正算子贯通双角度联合反演与Neumann/Airy多光束判别

<!-- Q1.central_sentence -->
针对问题一，建立复色散双光束Fresnel测厚模型

<!-- Q1.preliminary_work -->
统一复介电函数、被动平方根分支、s/p偏振和微米到厘米缩放

<!-- Q1.model -->
由复Snell关系和两界面Fresnel系数叠加表面束与第一束内部反射

<!-- Q1.algorithm -->
采用解析推导、极限情形和合成光谱直接恢复进行求解检验

<!-- Q1.result -->
合成厚度绝对误差为 0.00046 μm

<!-- Q1.analysis -->
零厚度退化和Neumann极限均通过，四联检查最大复数误差为1.25×10^-14

<!-- Q2.central_sentence -->
针对问题二，建立双角度共享参数复反射率联合反演

<!-- Q2.preliminary_work -->
审查共同边界异常点并由波段比较选择2000至3900波数带

<!-- Q2.model -->
同片双角度共享厚度与材料参数，各角度标定通过仿射剖面消元

<!-- Q2.algorithm -->
采用三种子差分进化粗搜、鲁棒最小二乘精修、SVD和移动块Bootstrap

<!-- Q2.result -->
SiC外延层厚度为 7.3840 μm；块Bootstrap的2.5%—97.5%分位范围为 7.3747—7.3943 μm

<!-- Q2.analysis -->
折射率尺度与厚度相关系数0.9996，故另报告7.2381至7.5359微米的系统范围

<!-- Q3.central_sentence -->
针对问题三，建立物理条件—复公比—Neumann/Airy多光束模型

<!-- Q3.preliminary_work -->
统一往返场因子与强度保持率口径并规定同波段同损失的公平比较

<!-- Q3.model -->
用有限阶Neumann级数连接双光束截断与Airy无穷阶极限

<!-- Q3.algorithm -->
逐阶联合重反演并以复公比、误差、AIC和阶数收敛决定回溯

<!-- Q3.result -->
SiC多光束厚度修正仅为 0.000088 μm；Si外延层厚度为 3.3960 μm；多光束使RMSE降低 70.47%

<!-- Q3.analysis -->
Si六束后收敛且波段结果为3.3949至3.4030微米，SiC高阶影响低于统计误差

""" Power analysis script
"""

###########
# Imports #
###########
# Import data science packages
from statsmodels.stats.power import TTestIndPower, TTestPower
import numpy as np
from matplotlib import pyplot as plt


#########
# BEGIN #
#########
effect_size = 0.7
alpha = 0.05
power = 0.8
#p_analysis = TTestIndPower()
p_analysis = TTestPower()
sample_size = p_analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power)

print("Required Sample Size: " + str(round(sample_size,2)))

#fig = TTestIndPower().plot_power(
fig = TTestPower().plot_power(
    dep_var='nobs',
    nobs=np.arange(2,50),
    effect_size=np.array([0.2, 0.5, 0.8]),
    alpha=0.05,
    title='Power of t-Test' + '\n' + r'$\alpha = 0.05$'
    )

plt.show()




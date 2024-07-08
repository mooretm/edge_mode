"""Playing around with ANOVA in Python.
"""

# Import data science packages
import numpy as np
import pandas as pd

import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from bioinfokit.analys import stat

import matplotlib.pyplot as plt
import seaborn as sns


# Create sample data
data = {
    'A': np.array([25,30,28,36,29]),
    'B': np.array([45,55,29,56,40]),
    'C': np.array([30,29,33,37,27]),
    'D': np.array([54,60,51,62,73])
}

# Make dataframe
df = pd.DataFrame(data)

df_melt = pd.melt(df.reset_index(),
    id_vars=['index'], 
    value_vars=['A', 'B', 'C', 'D'])
df_melt.columns = ['index', 'factor', 'value']

print(df_melt)

# Generate boxplot to see data distribution by factor
ax = sns.boxplot(x='factor', y='value', data=df_melt)
ax = sns.swarmplot(x='factor', y='value', data=df_melt)
plt.show()

# One-way ANOVA from scipy
fvalue, pvalue = stats.f_oneway(df['A'], df['B'], df['C'], df['D'])
print("\nOne-way ANOVA")
print(f"F: {round(fvalue,2)}\np: {pvalue:.3f}\n")

# One-way ANOVA with R-like table
res = stat()
res.anova_stat(df=df_melt, res_var='value', anova_model='value ~ C(factor)')
print("One-way ANOVA (with output table)")
print(res.anova_summary, '\n')

# Tukey HSD using bioinfokit.analys
res = stat()
res.tukey_hsd(df=df_melt, res_var='value', xfac_var='factor', anova_model='value ~ C(factor)')
print("Tukey HSD:")
print(res.tukey_summary, '\n')

# QQ plot
# res.anova_std_residuals are obtained from ANOVA above
sm.qqplot(res.anova_std_residuals, line='45')
plt.xlabel("Theoretical Quantiles")
plt.ylabel("Standardized Residuals")
#plt.show()
# histogram
plt.hist(res.anova_model_out.resid, bins='auto', histtype='bar', ec='k')
plt.xlabel("Residuals")
plt.ylabel("Frequency")
#plt.show()

# Normality testing
# Null hypothesis: data are drawn from a normal distribution
# p > 0.05, fail to reject null, data are normally distributed
w, pvalue = stats.shapiro(res.anova_model_out.resid)
print("Shapiro normality test:")
print(w, pvalue, '\n')


# Homogeneity of variances
# Null hypothesis: samples from populations have equal variances
# p > 0.05, fail to reject null, variances are equal
# Method 1
w, pvalue = stats.bartlett(df['A'], df['B'], df['C'], df['D'])
print('Barlett test of equal variances (assumes normal dist):')
print(w, pvalue, '\n')
# Method 2 (with output table)
res = stat()
print('Barlett test (with output table):')
res.bartlett(df=df_melt, res_var='value', xfac_var='factor')
print(res.bartlett_summary, '\n')

res = stat()
res.levene(df=df_melt, res_var='value', xfac_var='factor')
print("Levene's test for equal variances (for non-normal dist):")
print(res.levene_summary, '\n')


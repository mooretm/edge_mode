""" Data analysis script for DEM transition speed 
    pilot adaptive data.
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd

# Import stats packages
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Import system packages
from pathlib import Path


#########
# BEGIN #
#########
# Import all data files as a single dataframe
path = "C:/Users/MooTra/OneDrive - Starkey/Documents/Projects/EdgeMode/Transition Speed Pilot/Data/"
path = path + 'MOA Data'
files = Path(path).glob('*.csv')
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Rename the "filename_value" column to reflect the data
df.rename(columns = {'filename_value':'rating'}, inplace=True)

# Convert subject numbers to strings for plotting
df['subject'] = df['subject'].astype('string')

# Remove "INC_" from conditions
df['condition'] = df['condition'].str[4:]

# Split conditions column into two columns
df[['gain', 'speed']] = df.condition.str.split('_', expand=True)

# Grab just the relevant columns
data = df[['subject', 'gain', 'speed', 'rating']]
#print(data)


#########
# ANOVA #
#########
print('')
# Run ANOVA and print results
model = ols('rating ~ C(gain, Sum) + C(speed, Sum) + C(gain, Sum)*C(speed, Sum)', data=data).fit()
aov_table = sm.stats.anova_lm(model, typ=3)
print("ANOVA results with Type 3 sum of squares")
print(aov_table)

# model = ols('rating ~ C(gain) + C(speed) + C(gain)*C(speed)', data=data).fit()
# aov_table = sm.stats.anova_lm(model)
# print('\nANOVA results with incorrect Type 3 sum of squares')
# print(aov_table)

print('')


###############
# Effect Size #
###############
# Cohen's d function
def cohen_d(d1, d2):
    """ Calculate Cohen's d for independent samples
    """
    # Calculate the size of the samples
    n1, n2 = len(d1), len(d2)
    # Calculate the variance of the samples
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    # Calculate the pooled standard deviation
    s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 -2))
    # Calculate the means of the samples
    u1, u2 = np.mean(d1), np.mean(d2)
    # Calculate the effect size
    return (u1 - u2) / s

# Get ratings by speed
pref_ratings = df[df['speed']=='PREF']['rating']
fast_ratings = df[df['speed']=='FAST']['rating']
slow_ratings = df[df['speed']=='SLOW']['rating']

# Get ratings by gain
oag_ratings = df[df['gain']=='OAG']['rating']
lfg_ratings = df[df['gain']=='LFG']['rating'] 
hfg_ratings = df[df['gain']=='HFG']['rating']

condition_sets = {
    'PREF-FAST': (pref_ratings, fast_ratings), 
    'PREF-SLOW': (pref_ratings, slow_ratings),
    'SLOW-FAST': (slow_ratings, fast_ratings),
    'OAG-LFG': (oag_ratings, lfg_ratings),
    'OAG-HFG': (oag_ratings, hfg_ratings),
    'LFG-HFG': (lfg_ratings, hfg_ratings)
    }

for key in condition_sets.keys():
    d = cohen_d(condition_sets[key][0], condition_sets[key][1])
    print('-' * 60)
    print(f"Cohen's d for {key}")
    print(f"d = {np.round(d, 2)}")

print('')


####################
# Post-Hoc Testing #
####################
# Tukey's test
tukey = pairwise_tukeyhsd(
    endog=data['rating'],
    groups=data['speed'],
    alpha=0.05)

print(tukey)
print('\n')

#data.to_csv("travis_data.csv")

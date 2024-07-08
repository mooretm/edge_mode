""" Analysis for DEM lab study data

    Written by: Travis M. Moore
    Last edited: 04/25/2023
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

plt.style.use('seaborn-v0_8')

SMALL_SIZE = 8
MEDIUM_SIZE = 15
BIGGER_SIZE = 20

plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the figure title
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize
#plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

plt.xticks(rotation=45, ha='right')

# Import system packages
from pathlib import Path


#########
# Funcs #
#########
def to_percent(s):
    """ Calculate percentage based on number of positive outcomes.
    """
    return np.round(np.mean(s) * 100, 2)


#############
# Load Data #
#############
# To single df
_path = r'\\starfile\Public\Temp\MooreT\DEM\Vesta Data'
files = Path(_path).glob('*.csv')

try:
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
except ValueError:
    print('\nlab_data: No files were found!\n')
    quit()

# Reorganize data
df['condition'] = df['snapshot_A'] + '_' + df['snapshot_B'] + '_' + df['expected_response']
df.drop(['trial', 'audio_file', 'scaling_factor', 'snapshot_A', 
         'snapshot_B', 'actual_response', 'expected_response'], 
         axis=1, inplace=True)

# Subject level percents
sub_lvl = pd.DataFrame(df.groupby(['subject', 'condition'])['outcome'].agg(to_percent))
n = len(sub_lvl.index.get_level_values('subject').unique()) 

# Group level percents
group_lvl = pd.DataFrame(sub_lvl.groupby(['condition'])['outcome'].mean())
group_lvl.reset_index(inplace=True)
group_lvl['outcome'] = np.round(group_lvl['outcome'], 2) 

# Display dfs to console
print(sub_lvl)
print(group_lvl)

# Plot data by condition
#colors = ['red', 'blue', 'green', 'yellow', 'brown', 'cyan', 'orange', 'black']
colors = ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600']
plt.bar(group_lvl['condition'], group_lvl['outcome'], color=colors)
#plt.bar(group_lvl['condition'], group_lvl['outcome'])
plt.title(f"Paired Comparisons (n={n})")
plt.xlabel("Snapshot Pairs")
plt.ylabel("Percent 'Correct'")
plt.ylim([0, 100])
plt.axhline(y=50, color='green', linestyle='--')
plt.show()

# Write data to csv
#sub_lvl.to_csv('individual_lab_data.csv, index=False)
#group_lvl.to_csv('group_lab_data.csv', index=False)

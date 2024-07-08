""" Analysis for MOCS data """

# Import data science packages
from cProfile import label
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import seaborn as sns
import scipy.interpolate
from scipy.stats import kde
from scipy.stats import median_abs_deviation

# Import system packages
import glob
import os
from pathlib import Path


def find_closest(vals, high, low):
    """ Get the linear fit slope values for 
        plotting the polygon
    """
    # Round the linear slope values to integers
    rounded = [round(x) for x in vals]
    # Subtract the target high value from the rounded 
    # slope values. Take the minimum difference between 
    # the target high value and each of the rounded 
    # slope values.
    val_high = min(rounded, key=lambda x: abs(x-high))
    # Get the index of the rounded slope value that is
    # closest to the target high value
    idx_high = rounded.index(val_high)
    # Do the same for the target low value
    val_low = min(rounded, key=lambda x: abs(x-low))
    idx_low = rounded.index(val_low)
    return idx_high, val_high, idx_low, val_low


# Import all data files as a single dataframe
path = 'C:/Users/MooTra\Documents/Projects/EdgeMode/Transition Speed Pilot/Data/MOCS Sample Data'
files = Path(path).glob('*.csv')
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
# Rename the "filename_value" column to reflect the data
df.rename(columns = {'filename_value':'trans_dur'}, inplace=True)
df.rename(columns = {'awareness_rating':'aware'}, inplace=True)
df.rename(columns = {'acceptability_rating':'accept'}, inplace=True)
# Convert subject numbers to strings for plotting
df['subject'] = df['subject'].astype('string')

# NOTE: eventually will have to find the mean for multiple runs per subject FIRST
# Find mean across subjects for each value of trans_dur
aware_dstats = df.groupby(['condition', 'trans_dur'], as_index=False)['aware'].agg([np.mean, np.std])
aware_dstats.reset_index(inplace=True)

# New dfs by condition
aware_lfg = aware_dstats[aware_dstats['condition'] == 'LFG']
#aware_hfg = aware_dstats[aware_dstats['condition'] == 'HFG']
#aware_oag = aware_dstats[aware_dstats['condition'] == 'OAG']

# Create x axis values
x_axis = np.array(sorted(df['trans_dur'].unique()))
x_interp = scipy.interpolate.interp1d(aware_lfg['mean'], aware_lfg['trans_dur'])
val_high = 75
val_low = 50
idx_high = x_interp(val_high)
idx_low = x_interp(val_low)


# Linear regression
m, b = np.polyfit(x_axis, aware_lfg['mean'], 1)

# Get the high, low and indexes for the linear fit slope
#idx_high, val_high, idx_low, val_low = find_closest(m*x_axis+b, 75, 50)

# Plot data
plt.plot(x_axis, aware_lfg['mean'], marker='o')
plt.xlim(0,31)
plt.ylim(0,100)
plt.title("Judgments of Awareness by Transition Duration")
plt.ylabel("Awareness")
plt.xlabel("Transition Duration (s)")

# Plot linear regression
plt.plot(x_axis, m*x_axis+b)

# Make polygon: neagtive correlation
#coord = [[0,val_high], [x_axis[idx_high],val_high], [x_axis[idx_low],val_low], [x_axis[idx_low],0], [x_axis[idx_high],0], [x_axis[idx_high],val_low], [0,val_low]]
coord = [[0,val_high], [idx_high,val_high], [idx_low,val_low], [idx_low,0], [idx_high,0], [idx_high,val_low], [0,val_low]]
coord.append(coord[0]) # repeat the first point to create a 'closed loop'
p = Polygon(coord)
xs, ys = zip(*coord) # create lists of x and y values
plt.fill(xs,ys, edgecolor='none', facecolor="lightsalmon", alpha=0.25) 

# Plot text
plt.text(1,val_high-5,"Moderately\nAware")
plt.text(1,val_low-5,"Somewhat\nAware")
#plt.text(12,5,"X\nAdaptive Preference", color="green")

plt.show()

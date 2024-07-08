""" Analysis for MOA data 
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
import seaborn as sns
from scipy.stats import kde

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
# #df2['subject'] = pd.Categorical(df2.subject)

# Subset dataframes by gain condition
oag = df.loc[df.condition.str.contains('OAG')]
lfg = df.loc[df.condition.str.contains('LFG')]
hfg = df.loc[df.condition.str.contains('HFG')]


def mk_plot(gain_condition):
    """ Plot individual means and group density plots
        for each rating type (fast, pref, slow)
    """
    # Create new dataframe for descriptive stats
    dstats = gain_condition.groupby(
        ['subject', 'condition'], 
        as_index=False)['rating'].agg([np.mean, np.std])
    dstats.reset_index(inplace=True)
    # Sort descending for plotting
    dstats = dstats.sort_values(by='mean', ascending=False)

    # New dfs by rating type
    fast = dstats.loc[dstats.condition.str.contains('FAST')]
    pref = dstats.loc[dstats.condition.str.contains('PREF')]
    slow = dstats.loc[dstats.condition.str.contains('SLOW')]

    # Store gain condition in variable for easy access
    cond = gain_condition.iloc[1].condition.split('_')[1]

    # Show feedback on command line
    print('\n')
    print('-' * 60)
    print(f'{cond}')
    print('-' * 60)
    print(dstats.sort_values('condition'))
    print(f"{cond} Grand Average FAST: {round(fast['mean'].agg(np.mean), 2)} secs")
    print(f"{cond} Grand Average PREF: {round(pref['mean'].agg(np.mean), 2)} secs")
    print(f"{cond} Grand Average SLOW: {round(slow['mean'].agg(np.mean), 2)} secs")
    print('-' * 60)


    ############
    # Plotting #
    ############
    # Set style
    #plt.style.use('seaborn') # deprecated
    #print(plt.style.available)
    plt.style.use('seaborn-v0_8')

    # Main figure layout
    fig, ax = plt.subplot_mosaic(
        [['left', 'center', 'right'], 
        ['bottom', 'bottom', 'bottom']])
        #constrained_layout=True

    # Too fast bars
    ax['left'].bar(fast['subject'], fast['mean'], color='r')
    ax['left'].set(title='Too Fast', xlabel='Subject', 
        ylabel='Transition Speed (s)', ylim=(0, 30))
    ax['left'].errorbar(fast['subject'], fast['mean'], yerr=fast['std'], 
        color='black', fmt='o')

    # Preferred bars
    ax['center'].bar(pref['subject'], pref['mean'], color='g')
    ax['center'].set(title='Preferred', xlabel='Subject', ylim=(0, 30))
    ax['center'].errorbar(pref['subject'], pref['mean'], yerr=pref['std'], 
        color='black', fmt='o')

    # Too slow bars
    ax['right'].bar(slow['subject'], slow['mean'], color='b')
    ax['right'].set(title='Too Slow', xlabel='Subject', ylim=(0, 30))
    ax['right'].errorbar(slow['subject'], slow['mean'], yerr=slow['std'], 
        color='black', fmt='o')

    # Density: all conditions
    fast_all = gain_condition.loc[gain_condition.condition.str.contains('FAST')]
    pref_all = gain_condition.loc[gain_condition.condition.str.contains('PREF')]
    slow_all = gain_condition.loc[gain_condition.condition.str.contains('SLOW')]

    try:
        fast_all['rating'].plot(kind='density', ax=ax['bottom'], color='r')
    except np.linalg.LinAlgError:
        fast_all['rating'].plot(ax=ax['bottom'], color='r')

    pref_all['rating'].plot(kind='density', ax=ax['bottom'], color='g')
    slow_all['rating'].plot(kind='density', ax=ax['bottom'], color='b')
    
    ax['bottom'].set(title="Rating Density", xlabel="Transition Speed (s)",
        ylabel="Density")
    ax['bottom'].legend(labels=["Too Fast", "Preferred", "Too Slow"])
    #ax['bottom'].legend().set_visible(False)
    plt.suptitle(gain_condition.iloc[1].condition.split('_')[1])


# Call plotting function for each gain condition
mk_plot(oag)
mk_plot(lfg)
mk_plot(hfg)

# Show all plots
plt.show()


# """ Bar Plot """
# fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1)
# #fast.plot(kind='bar', x="subject", y="mean", ax=ax0)
# ax0.bar(fast['subject'], fast['mean'])
# ax0.errorbar(
#     fast['subject'], 
#     fast['mean'], 
#     yerr=fast['std'],
#     color='black',
#     fmt='o', # none
#     capsize=5)
# ax0.set(title='Barely Noticeable', xlabel='Subject', 
#     ylabel='Transition Speed (s)')
# ax0.legend().set_visible(False)
# fast.plot(kind='density', x="subject", y="mean", ax=ax1)
# plt.show()


# def custom_plot(x, y, ax=None, **plt_kwargs):
#     if ax is None:
#         ax = plt.gca()
#     ax.plot(x, y, **plt_kwargs)
#     return(ax)

# fig, axes = plt.subplots(2, figsize=(10,5))
# custom_plot([2,3], [4,5], ax=axes[0])
# axes[0].set(xlabel='x', ylabel='y', title='Custom plot')
# dstats.plot(kind='density', x="condition", y="rating", ax=axes[1])
# plt.tight_layout()
# plt.show()


#sns.displot(data=df['rating'], kde=True) # kind='kde'


# """ Density Plot """
# sns.distplot(jnd['rating'])
# sns.distplot(fast['rating'])
# #sns.distplot(df['pref'])
# ax1.set(title="Transition Speed Ratings", xlabel='Rating (s)',
#     ylabel='Density')
# plt.show()


# # Scatter plot with error bars
# """
# ms: markersize
# mec: markeredgecolor
# mfc: markerfacecolor
# ls: linestyle (solid, dotted, dashed, dashdot, None)
# c: color (for lines)
# lw: linewidth
# """
# # font_title = {'family':'sans-serif', 'color':'blue', 'size':15}
# # font_labels = {'family':'sans-serif', 'color':'black', 'size':11}
# # plt.errorbar(x=df['subject'].unique().tolist(), y=means, yerr=sds, capsize=5, capthick=2,
# #     marker='H', ms=10, mec='k', mfc='Coral',
# #     ls='None', c='r', lw=2.5)
# # plt.title("Acceptability Ratings (Mean of 4)", fontdict=font_title)
# # plt.xlabel("Subject", fontdict=font_labels)
# # plt.ylabel("Acceptability", fontdict=font_labels)
# # plt.ylim(0,100)
# # plt.grid(axis='both', c='red', ls=':', lw=1)
# # plt.show()

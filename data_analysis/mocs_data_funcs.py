"""Data analysis script for MOCS data.

    Author: Travis M. Moore
    Created: 9 Aug, 2022
    Last Edited: 31 Aug, 2022
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import seaborn as sns

# Import misc packages
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# Set plot style
plt.style.use('seaborn')


#####################
# Normality testing #
#####################
def do_norm_test(data):
    """Return histogram, probability density function, and QQ plot.
    """
    # All data
    vals = data.data['rating']
    data.normality_plots(data=vals, title="All Data")
    data.normality_tests(data=vals, title="All Data", output='silent')

    # Data by level
    levels = data.data['level'].unique()
    for level in levels:
        vals = data.data[data.data['level'] == level]['rating']
        data.normality_plots(data=vals, title=level)
        data.normality_tests(data=vals, title=level, output='silent')


###################
# Outlier testing #
###################

#######################
# Search for outliers #
def box_swarm_per_condition(data, info):
    """Box and swarm plots for each gain condition 
        (collapsed across durations). Plotted separately 
        for "aware" and "accept" data.
    """
    for sub in info['subs']:
        for level in info['levels']:
            vals = data.data[(data.data['subject'] =='999') & 
                (data.data['level'] == level)]
            ax = sns.boxplot(x='condition', y='rating',data=vals)
            ax = sns.swarmplot(x='condition', y='rating', data=vals, color='k')
            plt.title(f"'{level.upper()}' data for subject {sub}")
            plt.ylim([-1,101])
            plt.show()


def box_swarm_per_dur(data, info):
    """Box and swarm plots for each gain condition,
        with a plot for each duration. Each duration 
        plotted separately for "aware" and "accept" data.
    """
    for sub in info['subs']:
        for level in info['levels']:
            for dur in info['durs']:
                #x = d.loc[(sub, slice(None), dur), level]
                vals = data.data[
                    (data.data['subject'] == sub) & 
                    (data.data['level'] == level) & 
                    (data.data['trans_dur'] == dur)
                    ]
                ax = sns.boxplot(x='condition', y='rating',data=vals)
                ax = sns.swarmplot(x='condition', y='rating', data=vals, 
                    color='k')
                plt.title(f"SS {sub} '{level.upper()}' data for duration: {dur}")
                plt.ylim([-1,101])
                plt.show()


def box_swarm_condensed(data, info):
    """View all durations per condition on a single plot.
    """
    for sub in info['subs']:
        #ii_factor = 0
        for cond in info['conds']:
            ii_factor = 0
            for level in info['levels']:
                ii_factor += 1
                # Subset data
                vals = data.data[
                    (data.data['subject'] == sub) & 
                    (data.data['level'] == level) &
                    (data.data['condition'] == cond)
                    ]
                # Set up plotting space
                plt.subplot(len(info['levels']), 1, ii_factor)
                # Box plot
                ax = sns.boxplot(x='trans_dur', y='rating', data=vals)
                # Swarm plot
                ax = sns.swarmplot(x='trans_dur', y='rating', data=vals)
                # Plot parameters
                plt.title(f"SS {sub} '{level.upper()}' Ratings for '{cond}'")
                plt.xlabel("Transition Duration")
                plt.ylabel(f"{level.upper()} Rating")
                plt.ylim([-1,101])
            plt.show()


###################
# Remove outliers #
def delete_outliers(data, info):
    """Identify and remove outliers.
    """
    clean_data = []
    for sub in info['subs']:
        for cond in info['conds']:
            for level in info['levels']:
                for dur in info['durs']:
                    vals = data.data[
                        (data.data['subject'] == sub) & 
                        (data.data['condition'] == cond) &
                        (data.data['level'] == level) &
                        (data.data['trans_dur'] == dur)
                        ]
                    # Call remove outliers function
                    num_outliers, clean_df = data.remove_outliers(
                        vals=vals, values_colname='rating', 
                        dist='symmetrical', k=3, plts='n')
                    # Display number of outliers removed per iteration
                    if num_outliers > 0:
                        print(f"Found {num_outliers} outliers for index " +
                        f"{sub}, {cond}, {dur}, {level}")
                    # Add cleaned df to list
                    clean_data.append(clean_df)

                    # # For testing only!!
                    # # Remove some data to test outlier plots
                    # if cond == 'OAG': 
                    #     clean_data.append(clean_df)
                    # else:
                    #     clean_data.append(clean_df[1:])

    # Add newly-cleaned dataframe to object: self.clean_data
    clean_data_df = pd.concat(clean_data)
    #clean_data_df.reset_index(inplace=True)
    print(f"Total number of outliers removed: " +
       f"{data.data.shape[0] - clean_data_df.shape[0]}")
    data.clean_data = clean_data_df
    #print(data.clean_data)


def plot_outliers(data, info):
    """View all durations per condition on a single plot.
    """
    for sub in info['subs']:
        #ii_factor = 0
        for cond in info['conds']:
            ii_factor = 0
            for level in info['levels']:
                ii_factor += 1

                # Subset original data
                vals = data.data[
                    (data.data['subject'] == sub) & 
                    (data.data['condition'] == cond) &
                    (data.data['level'] == level)
                    ]

                # Subset cleaned data
                clean = data.clean_data[
                    (data.clean_data['subject'] == sub) & 
                    (data.clean_data['condition'] == cond) &
                    (data.clean_data['level'] == level)
                    ]

                # Set up plotting space
                plt.subplot(len(info['levels']), 1, ii_factor)

                # Swarm plot
                ax = sns.swarmplot(x='trans_dur', y='rating', data=vals, color='red')
                ax = sns.swarmplot(x='trans_dur', y='rating', data=clean, color='green')

                # Plot parameters
                plt.title(f"SS {sub} '{level.upper()}' Ratings for '{cond}'")
                plt.xlabel("Transition Duration")
                plt.ylabel(f"{level.upper()} Rating")
                plt.ylim([-1,101])
            plt.show()

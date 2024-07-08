""" Analysis for DEM field trial app data. 

    Concatenate and organize data into single dataframe from 
    multiple log files. Display tables and pie charts for 
    response counts for each question. Display tables for 
    rating counts by snapshot pair. 

    Written by: Travis M. Moore
    Created: 04/10/2023
    Last edited: 05/16/2023
"""

###########
# Imports #
###########
# Data science
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

plt.rcParams['figure.figsize'] = [12, 8]

#plt.style.use('seaborn-v0_8')

SMALL_SIZE = 8
MEDIUM_SIZE = 15
BIGGER_SIZE = 22

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the figure title
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize


#####################
# Organize Raw Data #
#####################
# Read in binder data
data_file = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\Journals.csv'
data = pd.read_csv(data_file)
data.columns = ['journal_id', 'subject', 'entry_date', 'q1', 'q2', 'q3', 'q5', 'q6a', 
 'q6b', 'q6c', 'q6d', 'q7a', 'q7b', 'q4', 'q8']
df = data.iloc[:, [1, 6, 7, 8, 9, 10, 11, 12]].copy()
df.to_csv('binder_data.csv', index=False)

# Read in app data from csv (created using: app_data.py)
app_data = pd.read_csv('app_data.csv')

df = pd.concat([df, app_data])
df.reset_index(drop=True, inplace=True)
df.to_csv('all_data.csv', index=False)


#########################
# Toggled vs. automatic #
#########################
print("\n* Toggled v. Automatic *")
print(f"Total records: {len(df)}")
print(f"Toggled: {df['q6b'].isna().sum()}")
#print(f"Automatic: {len(q6a) - q6a.isna().sum()}")
print(f"Automatic: {df['q7b'].isna().sum()}")
print(f"Percent toggled: {np.round(df['q6b'].isna().sum() / len(df) * 100, 1)}")
print(f"Percent automatic: {np.round(df['q7b'].isna().sum() / len(df) * 100, 1)}")


####################
# Stacked Bar Plot #
####################
# List of plot titles
label_list = ['Satisfaction', 'Appropriate Time for Change', 
              'Awareness of Transition', 'Preference Pre-Post Change',
              'Speed of Transition', 'DEM vs Normal Program', 
              'Satisfaction with Snapshot (Toggling)']
results = {}
def stacked_bar(show='y', save='n'):
    for ii, q in enumerate(list(df.columns[1:])):
        # Get response counts
        vals = pd.DataFrame(df.loc[:, ['subject', q]].value_counts())
        vals.rename(columns={0:'count'}, inplace=True)
        print(f"\nOriginal Counts: {vals}")

        total_count = vals.groupby(['subject']).sum()

        # Get list of subjects
        subs = list(vals.index.get_level_values('subject').unique())

        # Add 0 for missing responses
        # Convert existing reponse counts to percentage
        for resp in vals.index.get_level_values(q).unique():
            for sub in subs:
                try:
                    vals.loc[(sub, resp), :] = np.round(float(vals.loc[(sub, resp)]) / float(total_count.loc[sub]), 2) * 100
                except KeyError:
                    vals.loc[(sub, resp), :] = 0.0
        print(f"\nPercentages: {vals}")
    
        # Make wide dataframe for stacked bar plot func
        y = vals.reset_index()
        y.sort_values(by='subject', inplace=True)
        y_wide = y.pivot(index='subject', columns=q, values='count').reset_index()

        # Add group data
        newrow = list(y_wide.mean()[1:])
        newrow = [round(num, 2) for num in newrow]
        newrow.insert(0, 'Average')
        y_wide.loc[len(y_wide.index)] = newrow
        print(y_wide)
        results[q] = y_wide

        # Display the plot
        y_wide.plot(x='subject', kind='bar', stacked=True)
        plt.ylabel('Percent of Responses')
        plt.xlabel('Subject Number')
        plt.title(q.capitalize() + ': ' + label_list[ii])
        plt.legend(loc='upper left', facecolor='white', framealpha=1)

        # Display percents on the stacked bars
        df_rel = y_wide[y_wide.columns[1:]]
        for n in df_rel:
            for i, (cs, ab, pc, tot) in enumerate(zip(y_wide.iloc[:, 1:].cumsum(1)[n], y_wide[n], df_rel[n], y_wide[n])):
                #plt.text(tot, i, str(tot), va='center')
                #plt.text(i, tot, str(round(tot,1)), va='center', ha='center')
                #plt.text(cs - ab/2, i, str(np.round(pc, 1)) + '%', va='center', ha='center')
                #plt.text(i, cs - ab/2, str(np.round(pc, 1)) + '%', ha='center')
                plt.text(i, cs - ab/2, str(int(pc)) + '%', ha='center')

        # Save/show?
        if save == 'y':
            desktop = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\DEM Plots'
            plt.savefig(desktop + f'\{q + "_all_data_stacked"}.png')

        if show == 'y':
            plt.show()

        plt.close()

# Call stacked bar plot func
stacked_bar(show='n', save='n')


#####################
# Statistical Tests #
#####################
#NOTE: must run stacked_bar() to generate formatted data for analyses
title1 = 'Statistical Tests by Question'
print('\n' + '-' * len(title1))
print(title1)
print('-' * len(title1))

print('Question 5: Satsfaction while toggling')
print(stats.friedmanchisquare(results['q5']['dissatisfied'], results['q5']['neutral'], results['q5']['satisfied']))

print('\nQuestion 6a: Good time for change')
print(stats.wilcoxon(results['q6a']['yes'], results['q6a']['no']))

print('\nQuestion 6b: Awareness of transitions')
print(stats.friedmanchisquare(results['q6b']['slightly'], results['q6b']['somewhat'], results['q6b']['moderately']))

print('\nQuestion 6c: Snapshot before v. after')
print(stats.wilcoxon(results['q6c']['before'], results['q6c']['after']))

print('\nQuestion 6d: Awareness of transition')
print(stats.friedmanchisquare(results['q6d']['too fast'], results['q6d']['acceptable'], results['q6d']['too slow']))

print('\nQuestion 7a: DEM v. *Normal')
print(stats.wilcoxon(results['q7a']['dem'], results['q7a']['personal']))

print('\nQuestion 7b: Satsfaction Toggling')
print(stats.friedmanchisquare(results['q7b']['dissatisfied'], results['q7b']['neutral'], results['q7b']['satisfied']))

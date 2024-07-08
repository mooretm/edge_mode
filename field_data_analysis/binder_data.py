""" Analysis for DEM field trial app data. 

    Concatenate and organize data into single dataframe from 
    multiple log files. Display tables and pie charts for 
    response counts for each question. Display tables for 
    rating counts by snapshot pair. 

    Written by: Travis M. Moore
    Created: 04/10/2023
    Last edited: 05/11/2023
"""

###########
# Imports #
###########
# Data science
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})



# Generate dict of questions and responses for plotting
question_list = []
for ii in range(1, 8):
    x = 'q' + str(ii)
    question_list.append(x)

label_list = ['Satisfaction', 'Appropriate Time for Change', 
              'Awareness of Transition', 'Preference Pre-Post Change',
              'Speed of Transition', 'DEM vs Normal Program', 
              'Satisfaction with Snapshot (Toggling)']

results_dict = dict(zip(question_list, label_list))



#####################
# Organize Raw Data #
#####################
# Read in data
data_file = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\Journals.csv'
data = pd.read_csv(data_file)


# Toggled vs. automatic
print("\n* Toggled v. Automatic *")
q6a = data['q6a_appropriate_change']
print(f"Toggled: {q6a.isna().sum()}")
print(f"Automatic: {len(q6a) - q6a.isna().sum()}")
print(f"Percent toggled: {np.round(q6a.isna().sum() / len(q6a) * 100, 1)}")

data.columns = ['journal_id', 'subject', 'entry_date', 'q1', 'q2', 'q3', 'q5', 'q6a', 
 'q6b', 'q6c', 'q6d', 'q7a', 'q7b', 'q4', 'q8']

df = data.iloc[:, [1, 6, 7, 8, 9, 10, 11, 12]].copy()

df.to_csv('binder_data.csv', index=False)



####################
# Stacked Bar Plot #
####################
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

        # Display the plot
        y_wide.plot(x='subject', kind='bar', stacked=True)
        plt.ylabel('Percent of Responses')
        plt.xlabel('Subject Number')
        plt.title(q.capitalize() + ': ' + label_list[ii])

        # Display percents on the stacked bars
        df_rel = y_wide[y_wide.columns[1:]]
        for n in df_rel:
            for i, (cs, ab, pc, tot) in enumerate(zip(y_wide.iloc[:, 1:].cumsum(1)[n], y_wide[n], df_rel[n], y_wide[n])):
                #plt.text(tot, i, str(tot), va='center')
                #plt.text(i, tot, str(round(tot,1)), va='center', ha='center')
                #plt.text(cs - ab/2, i, str(np.round(pc, 1)) + '%', va='center', ha='center')
                plt.text(i, cs - ab/2, str(np.round(pc, 1)) + '%', ha='center')

        # Save/show?
        if save == 'y':
            desktop = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\DEM Plots'
            plt.savefig(desktop + f'\{q + "_binder_stacked"}.png')

        if show == 'y':
            plt.show()

        plt.close()

# Call stacked bar plot func
#stacked_bar(show='y', save='y')


##############
# Pie Charts #
##############
def pie_chart(data, question, blurb, show='y', save='n'):
    """ Create a pie chart with custom labels.
    """
    # Organize data
    vals = data[data['question']==question]
    responses = vals['response'].value_counts()

    # Print to console
    #q1_text = "*** Q1 Data ***"
    print(f"\n\nfield: {'*' * len(blurb)}")
    print(f"field: {blurb}")
    print(f"field: {'*' * len(blurb)}")
    print(responses)

    # Pie chart
    plt.pie(responses, labels=responses.index,
            autopct=lambda p: '{:.0f}%'.format(p)
            )
    plt.title(f"{blurb}")

    if save == 'y':
        desktop = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\DEM Plots'
        plt.savefig(desktop + f'\{question}.png', bbox_inches='tight')
        #time.sleep(1)

    if show == 'y':
        plt.show()

    plt.close()

# # Call pie chart function for each question
# for key in results_dict:
#     pie_chart(data, key, results_dict[key], show='n', save='y')



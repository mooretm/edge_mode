""" Analysis for DEM field trial app data. 

    Concatenate and organize data into single dataframe from 
    multiple log files. Display tables and pie charts for 
    response counts for each question. Display tables for 
    rating counts by snapshot pair. 

    Written by: Travis M. Moore
    Created: 04/10/2023
    Last edited: 04/14/2023
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

# GUI
import tkinter as tk
from tkinter import filedialog

# System
from pathlib import Path
import glob
import os
import csv


#####################
# Organize Raw Data #
#####################
# Dictionary of snapshot abbreviations for renaming
SNAPS = {
    'QuietRestaurantSpeech': 'QRS',
    'TransportationNoiseWithSpeech': 'TRS',
    'LargeRoomSpeech': 'LRS',
    'TransportationNoise': 'TRN',
    'ModerateLoudRestaurant': 'MLR',
    'DefaultLowLevel': 'DLL',
    'DefaultHighLevel': 'DHL'
}

QUESTIONS = {
    'QuestionnariesEntryTime': 'survey_start',
    'QuestionnarieOne': 'q1',
    'QuestionnarieTwo': 'q2',
    'QuestionnaireThree': 'q3',
    'QuestionnaireFour': 'q4',
    'QuestionnaireFive': 'q5',
    'QuestionnaireSix': 'q6',
    'QuestionnaireSeven': 'q7',
    'QuestionnaireEight': 'q8'
}

_path = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\all_responses'
# Directory
if not _path:
    # Show file dialog to get path
    root = tk.Tk()
    root.withdraw()
    _path = filedialog.askdirectory()
    print(_path)

# Get list of feedback logs only
#all_files = glob.glob(_path + r'\[!Right, !Left]*.csv') # Exclude files with Right/Left in name
#files = [fn for fn in glob.glob(_path + r'\*.csv')
#         if os.path.basename(fn).find('Right') < 0]

all_files = Path(_path).glob('*.csv')
files = []
for f in all_files:
    if (os.path.basename(f).find('Left') < 0) and (os.path.basename(f).find('Right') < 0):
        files.append(f)

#files = list(files)
print(f"\nfield: Found {len(files)} files")


# Concatenate all log files into single df
df_list = []
counter = 0
for file in files:
    data = pd.read_csv(file, usecols=[0,1], nrows=11, header=None)
    
    # Check that file name ID matches the ID in the file
    if data.iloc[0,1] == os.path.basename(file)[:4]:
        data.drop(0, axis=0, inplace=True)
    else:
        print(f"\n\nfield: Filename ID does not match ID in file: {os.path.basename(file)}")
        raise AttributeError

    # Update field names in file
    for ii in range(0, len(data)): 
        # Questions
        try:
            data.iloc[ii,0] = QUESTIONS[data.iloc[ii,0]]
        except KeyError:
            pass

        # Snapshots
        try:
            data.iloc[ii,1] = SNAPS[data.iloc[ii,1]]
        except KeyError:
            pass

        # Previous shapshot
        try:
            if len(data.iloc[ii,0].split('-')) == 6:
                data.iloc[ii,0] = 'Previous Snapshot'
        except:
            print(f'Problem reading file: {os.path.basename(file)}')
            print(data.iloc[ii,:])
            print('')


    data.rename(columns = {0:'question', 1:'response'}, inplace=True)
    data.insert(loc=0, column='subject', value=os.path.basename(file)[:4])
    data.insert(loc=1, column='counter', value=counter)
    data['pair'] = data.iloc[1, 3] + '_' + data.iloc[2, 3]
    counter += 1

    df_list.append(data)

data = pd.concat(df_list)
data.reset_index(drop=True, inplace=True)

print('Reorganized data:')
print(data)


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

# # Call pie chart function for each question
# for key in results_dict:
#     pie_chart(data, key, results_dict[key], show='n', save='y')


############################
# Ratings By Snapshot Pair #
############################
def answers_by_pair(data, question, blurb):
    # Organize data
    vals = data[data['question']==question][['pair', 'response']].value_counts()
    vals = pd.DataFrame(vals)
    vals.reset_index(inplace=True)
    vals.rename(columns={0:'count'}, inplace=True)

    # Print to console
    _text = f"*** Ratings By Pair: {blurb} ***"
    print(f"\n\nfield: {'*' * len(_text)}")
    print(f"field: {_text}")
    print(f"field: {'*' * len(_text)}")
    print(vals)

    vals.insert(loc=0, column="question", value=question)

    vals.to_csv('ratings_by_pair.csv', mode='a', header=False, index=False)

# Call ratings by pair function for all questions
with open('ratings_by_pair.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['question', 'pair', 'response', 'count'])
for key in results_dict:
    answers_by_pair(data, key, results_dict[key])


####################
# Stacked Bar Plot #
####################
survey = {
    'q1': ['Dissatisfied', 'Neutral', 'Satisfied'],
    'q2': ['Yes', 'No'],
    'q3': ['Slightly', 'Somewhat', 'Moderately'],
    'q4': ['Before', 'After'],
    'q5': ['Too Slow', 'Acceptable', 'Too Fast'],
    'q6': ['Personal Program', 'Adaptive Feature'],
    'q7': ['Dissatisfied', 'Neutral', 'Satisfied']
}


def stacked_bar(survey, show='y', save='n'):
    for ii, q in enumerate(survey):
        # Get response counts
        vals = data[data['question']==q][['subject', 'response']].value_counts()
        x = pd.DataFrame(vals)
        x.rename(columns={0:'count'}, inplace=True)
        total_count = x.groupby(['subject']).sum()

        # Get list of subjects
        subs = list(x.index.get_level_values('subject').unique())

        # Add 0 for missing responses
        # Convert existing reponse counts to percentage
        for resp in survey[q]:
            for sub in subs:
                try:
                    x.loc[(sub, resp), :] = round(x.loc[(sub, resp)] / total_count.loc[sub], 2) * 100
                except KeyError:
                    x.loc[(sub, resp), :] = 0

        # Make wide dataframe for stacked bar plot func
        y = x.reset_index()
        y.sort_values(by='subject', inplace=True)
        y_wide = y.pivot(index='subject', columns='response', values='count').reset_index()

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
            plt.savefig(desktop + f'\{q + "_stacked"}.png')

        if show == 'y':
            plt.show()

        plt.close()

# Call stacked bar plot func
stacked_bar(survey, show='y', save='n')

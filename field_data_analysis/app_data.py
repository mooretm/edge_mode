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

# System
from pathlib import Path


#####################
# Organize Raw Data #
#####################
_path = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\all_responses'
files = Path(_path).glob('*.csv')
files = list(files)
print(f"\nfield: Found {len(files)} files")

df_list = []
counter = 0
for file in files:
    try:
        data = pd.read_csv(file, nrows=12, header=None)
    except pd.errors.ParserError:
        try: 
            data = pd.read_csv(file, nrows=11, header=None)
        except pd.errors.ParserError:
            print(f"Problem with file: {file}")
            
    data = data.transpose()
    data.columns = data.iloc[0]
    data = data[1:]
    data = data[['ParticipantID', 'QuestionnarieOne', 'QuestionnarieTwo',
                 'QuestionnaireThree', 'QuestionnaireFour', 
                 'QuestionnaireFive', 'QuestionnaireSix', 
                 'QuestionnaireSeven']]
    new_names = ['subject', 'q5', 'q6a', 'q6b', 'q6c', 
             'q6d', 'q7a', 'q7b']
    data.columns = new_names

    df_list.append(data)

data = pd.concat(df_list)
data.reset_index(drop=True, inplace=True)

# Set all values to lowercase
cols = list(data.columns)
cols.pop(0)
for col in cols:
    data[col] = data[col].str.lower()

# Convert q7a responses
for ii in range(0,len(data)):
    if data.loc[ii, 'q7a'] == 'personal program':
        data.loc[ii, 'q7a'] = 'personal'

    if data.loc[ii, 'q7a'] == 'adaptive feature':
        data.loc[ii, 'q7a'] = 'dem'

print('Reorganized data:')
print(data)

data.to_csv('app_data.csv', index=False)

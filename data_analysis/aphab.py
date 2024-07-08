""" Data organization and analysis for Qualtrics-based APHAB results.

    Author: Travis M. Moore
    Created: 10/19/2022
    Last Edited: 10/19/2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd


#######################
# Organize APHAB Data #
#######################
# Read in data
data_full = pd.read_csv('APHAB.csv')
# Subset only pertinent data
data = data_full.iloc[2:, 17:].copy()
# Generate new column names
colnames = list(range(1,28))
colnames.insert(0, 'subject')
data.columns = colnames
# Convert from wide to long format
data = pd.melt(data, id_vars='subject', value_vars=list(range(1,28)))
# Rename variable column after melt
data = data.rename(columns={'variable': 'q_num'})
# Convert responses to integers
data['value'] = data['value'].astype(int)
# Retain only questions 1:24
data = data[data['q_num'].isin(range(0,25))]


######################
# Create new columns #
######################
# Identify reversed questions
data['reversed'] = data['q_num'].isin([1, 16, 19, 9, 11, 21])

# Create scoring key dict for
# reversed and not reversed questions
scores = [99, 87, 75, 50, 25, 12, 1]
not_reversed_score = {}
for idx, score in enumerate(scores, start=1):
    not_reversed_score[idx] = score
scores.reverse()
reversed_score = {}
for idx, score in enumerate(scores, start=1):
    reversed_score[idx] = score

# Create converted score column
data['score'] = np.where(
    data['reversed']==True, # condition
    data['value'].map(reversed_score), # if True
    data['value'].map(not_reversed_score) # if False
    )

# Create subscales from question numbers
EC = [4, 10, 12, 14, 15, 23]
BN = [1, 6, 7, 16, 19, 24]
RV = [2, 5, 9, 11, 18, 21]
AV = [3, 8, 13, 17, 20, 22]

# Create subscale column
data['subscale'] = np.repeat(0,len(data))
for ii in range(0, len(data)):
    if data['q_num'][ii] in EC:
        data.loc[ii, 'subscale'] = 'EC'
    elif data['q_num'][ii] in BN:
        data.loc[ii, 'subscale'] = 'BN'
    elif data['q_num'][ii] in RV:
        data.loc[ii, 'subscale'] = 'RV'
    elif data['q_num'][ii] in AV:
        data.loc[ii, 'subscale'] = 'AV'


####################
# Calculate scores #
####################
# Subscale scores
print('-' * 60)
print('APHAB Subscale Scores')
print('-' * 60)
print(data.groupby(['subject', 'subscale'])['score'].apply(np.mean))
print('-' * 60)
print('\n')

# Global scores
# Drop AV subscale to calculate global score
data_global = data.loc[data['subscale'].isin(['BN', 'EC', 'RV'])]
print('-' * 60)
print('APHAB Global Scores')
print('-' * 60)
print(data_global.groupby(['subject'])['score'].apply(np.mean))
print('-' * 60)
print('\n')

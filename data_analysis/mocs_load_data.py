# Import data science packages
import pandas as pd

# Import system packages
from pathlib import Path

#################
# Organize Data #
#################
def load_data(path):
    # Import all data files as a single dataframe
    #path = 'C:/Users/MooTra/Documents/Projects/EdgeMode/Transition Speed Pilot/Data/'
    #path = path + 'MOCS Sample Data'
    files = Path(path).glob('*.csv')
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    # Rename the "filename_value" column to reflect the data
    df.rename(columns = {'filename_value':'trans_dur'}, inplace=True)
    df.rename(columns = {'awareness_rating':'aware'}, inplace=True)
    df.rename(columns = {'acceptability_rating':'accept'}, inplace=True)
    # Convert subject numbers to strings for plotting
    df['subject'] = df['subject'].astype('string')
    # Put "aware" and "accept" data in long format
    df = df.melt(id_vars=['subject', 'condition', 'trans_dur'], 
        value_vars=['aware', 'accept'], 
        var_name='level', 
        value_name='rating')

    return df

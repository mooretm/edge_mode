"""Data analysis script for MOCS data.

    Author: Travis M. Moore
    Created: 9 Aug, 2022
    Last Edited: 31 Aug, 2022
"""

###########
# Imports #
###########
# Import custom modules
import mocs_data_funcs as mocs
from mocs_load_data import load_data
from data import Data
import mocs_plots


################
# Prepare data #
################
# Load data
path = 'C:/Users/MooTra/Documents/Projects/EdgeMode/Transition Speed Pilot/Data/'
path = path + 'MOCS Simulation Data'
data_df = load_data(path)
data = Data(data_df)

# Create data info dict
info = {
    'index': ['subject', 'condition', 'trans_dur'],
    'levels': ['aware', 'accept'],
    'subs': data.data['subject'].unique(),
    'conds': data.data['condition'].unique(),
    'durs': data.data['trans_dur'].unique()
    }


##############################
# Call exploratory functions #
##############################
# Normality testing
#mocs.do_norm_test(data)

# Box and swarm plots
#mocs.box_swarm_per_condition(data, info)
#mocs.box_swarm_per_dur(data, info)
#mocs.box_swarm_condensed(data, info)

# Remove and plot outliers
mocs.delete_outliers(data, info) # must be called before plot_outliers()
#mocs.plot_outliers(data, info)


############
# Plotting #
############
# Subset data for plotting
aware_dstats, accept_dstats = mocs_plots.subset_data(data.clean_data)

# Awareness data object
aware = mocs_plots.Aware()
aware.data = aware_dstats
aware.ylab = 'Awareness'
aware.gains = {
    'LFG': 'left',
    #'HFG': 'center',
    #'OAG': 'right'
    }
aware.range = {
    'Moderately\nAware': 75, 
    'Somewhat\nAware': 50
    }

# Acceptability data object
accept = mocs_plots.Accept()
accept.data = accept_dstats
accept.ylab = 'Acceptability'
accept.gains = {
    'LFG': 'left',
    #'HFG': 'center',
    #'OAG': 'right'
    }
accept.range = {
    'Extremely\nAcceptable': 100, 
    'Somewhat\nAcceptable': 50
    }

mocs_plots.plot_data(aware_obj=aware, accept_obj=accept)

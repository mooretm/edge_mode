"""Plot MOCS data Figure
"""

###################
# Import Packages #
###################
# Import data science packages
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


################
# Prepare data #
################
def subset_data(df):
    # Find mean across subjects for each value of trans_dur
    # AWARENESS DATA
    df_aware = df[df['level'] == 'aware']
    aware_dstats = df_aware.groupby(['condition', 'trans_dur'], 
        as_index=False)['rating'].agg([np.mean, np.std])
    aware_dstats.reset_index(inplace=True)

    # ACCEPTANCE DATA
    df_accept = df[df['level'] == 'accept']
    accept_dstats = df_accept.groupby(['condition', 'trans_dur'], 
        as_index=False)['rating'].agg([np.mean, np.std])
    accept_dstats.reset_index(inplace=True)

    return aware_dstats, accept_dstats


###########
# Classes #
###########
class Aware:
    """ Object to store awareness data """
    pass


class Accept:
    """ Object to store acceptability data """
    pass


################
# Create Plots #
################
def mk_plots(data_obj, cond, ax=None):
    """ Plot data """
    # Get x axis values
    x_axis = np.array(sorted(data_obj.data['trans_dur'].unique()))

    # Subset df by condition
    data = data_obj.data[data_obj.data['condition'] == cond]

    # Get data object ratings of interest
    d_labs = list(data_obj.range.keys())

    # Linear regression
    try:
        m, b = np.polyfit(x_axis, data['mean'], 1)
    except TypeError:
        print("Some conditions might not have data!")

    # Interpolate linear fit for polygon
    # Interpolates between actual data points
    #x_interp = scipy.interpolate.interp1d(aware_lfg['mean'], aware_lfg['trans_dur'])
    # Interpolates between linear fit points
    x_interp = scipy.interpolate.interp1d(m*x_axis+b, x_axis)

    val_high = data_obj.range[d_labs[0]]
    val_low = data_obj.range[d_labs[1]]
    try:
        idx_high = x_interp(val_high)
    except ValueError:
        idx_high = np.max(m*x_axis+b)
    try:
        idx_low = x_interp(val_low)
    except ValueError:
        idx_low = np.min(m*x_axis+b)

    # Plot data
    ax.plot(x_axis, data['mean'], marker='o')
    ax.set_xlim(0,31)
    ax.set_ylim(0,100)
    plt.suptitle(f"Judgments of {data_obj.ylab} by Transition Duration")
    ax.set_title(cond)
    ax.set_ylabel(data_obj.ylab)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Transition Duration (s)")

    # Plot linear regression
    ax.plot(x_axis, m*x_axis+b)

    # Make polygon
    #if data_obj.corr == 'negative':
    reg = m*x_axis+b
    if reg[0] > reg[-1]:
        # Make polygon: negative correlation
        coord = [[0,val_high], [idx_high,val_high], [idx_low,val_low], [idx_low,0], [idx_high,0], [idx_high,val_low], [0,val_low]]
        coord.append(coord[0]) # repeat the first point to create a 'closed loop'
    #elif data_obj.corr == 'positive':
    elif reg[0] < reg[-1]:
        # Make polygon: positive correlation
        coord = [[0,val_high], [idx_high,val_high], [idx_high,0], [idx_low,0], [idx_low,val_low], [0,val_low]]
        coord.append(coord[0]) # repeat the first point to create a 'closed loop'
    else:
        print("No correlation type provided!")
    # Plot polygon
    xs, ys = zip(*coord) # create lists of x and y values
    ax.fill(xs, ys, edgecolor='none', facecolor="lightsalmon", alpha=0.25)

    # Plot text
    ax.text(1, val_high, d_labs[0], va='center') # va == vertical alignment
    ax.text(1, val_low, d_labs[1], va='center')
    #plt.text(12,5,"X\nAdaptive Preference", color="green")


#################
# Display Plots #
#################
def plot_data(aware_obj, accept_obj):
    # Set matplotlib style
    plt.style.use('seaborn')

    # Set up AWARENESS data figure
    fig, ax = plt.subplot_mosaic([
        ['left', 'center', 'right']])
    #Call AWARENESS data plotting function
    for gain in aware_obj.gains.keys():
        mk_plots(data_obj=aware_obj, cond=gain, ax=ax[aware_obj.gains[gain]])

    # Set up ACCEPTABILITY data figure
    fig2, ax2 = plt.subplot_mosaic([
        ['left', 'center', 'right']])
    #Call ACCEPTABILITY data plotting function
    for gain in accept_obj.gains.keys():
        mk_plots(data_obj=accept_obj, cond=gain, ax=ax2[accept_obj.gains[gain]])

    # Display all plots
    plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.optimize import curve_fit

import pandas as pd


def exponential(x, a, b):
    return a*np.exp(b*x)

def power_law(x, a, b):
    return a*np.power(x, b)

def inverse_power_law(x, a, b):
    return x**(1/b) / a

rating_scale = np.arange(1,101)
x_axis = np.arange(1,31)
s1 = np.linspace(100,1,30)
#s1 = np.flip(s1)
noise = [np.random.randint(-10,10) for x in s1]
s1 = s1 + noise

s1_data = []
for i in s1:
    if i >= 100:
        i = 99
    if i <= 0:
        i = 1
    s1_data.append(i)

# Convert scale from 1:100 to 100:1
#s1_data = [100-y for y in s1_data]




# Exponential Curve
#pars, cov = curve_fit(f=exponential, xdata=x_axis, ydata=s1_data, p0=[0, 0], bounds=(-np.inf, np.inf))
# Power Law Curve
pars_power_law, cov_power_law = curve_fit(f=power_law, xdata=x_axis, ydata=s1_data, p0=[0,0], bounds=(-np.inf, np.inf))
print(pars_power_law)

# Linear regression
m, b = np.polyfit(x_axis, s1_data, 1)
print(m, b)


def find_closest(vals, high, low):
    rounded = [round(x) for x in vals]
    val_high = min(rounded, key=lambda x: abs(x-high))
    idx_high = rounded.index(val_high)
    val_low = min(rounded, key=lambda x: abs(x-low))
    idx_low = rounded.index(val_low)
    return idx_high, val_high, idx_low, val_low


idx_high, val_high, idx_low, val_low = find_closest(m*x_axis+b, 75, 50)


# Plot raw data
plt.plot(x_axis,s1_data,marker='o')
plt.xlim(0,30)
plt.ylim(0,100)
plt.title("Judgments of Awareness by Transition Duration")
plt.ylabel("Awareness")
plt.xlabel("Transition Duration (s)")
# Plot power law curve
#plt.plot(x_axis, power_law(x_axis, *pars_power_law))
#plt.plot(x_axis, pl_list)
# Plot exponential curve
#plt.plot(x_axis, exponential(x_axis, *pars))
plt.plot(x_axis, m*x_axis+b)

"""
# Make polygon: positive correlation
# For positive correlation
coord = [[0,curve_val_low], [idx_low+1,curve_val_low], [idx_low+1,0], [idx_high+1,0], [idx_high+1,curve_val_high], [0,curve_val_high]]
# For negative correlation - blocky
#coord = [[0,curve_val_high], [idx_low+1,curve_val_high], [idx_low+1,0], [idx_high+1,0], [idx_high+1,curve_val_low], [0,curve_val_low]]
coord.append(coord[0]) # repeat the first point to create a 'closed loop'
p = Polygon(coord)
xs, ys = zip(*coord) # create lists of x and y values
plt.fill(xs,ys, edgecolor='none', facecolor="lightsalmon", alpha=0.25) 
"""

# Make polygon: neagtive correlation
#coord = [[0,curve_val_low], [idx_low+1,curve_val_low], [idx_low+1,0], [idx_high+1,0], [idx_high+1,curve_val_high], [0,curve_val_high]]
# For negative correlation - blocky
coord = [[0,val_high], [idx_high+1,val_high], [idx_low+1,val_low], [idx_low+1,0], [idx_high+1,0], [idx_high+1,val_low], [0,val_low]]
coord.append(coord[0]) # repeat the first point to create a 'closed loop'
p = Polygon(coord)
xs, ys = zip(*coord) # create lists of x and y values
plt.fill(xs,ys, edgecolor='none', facecolor="lightsalmon", alpha=0.25) 

# Lines only 
#plt.plot([0, idx_high+1, idx_high+1], [curve_val_high, curve_val_high, 0], color='black')
#plt.plot([0, idx_low+1, idx_low+1], [curve_val_low, curve_val_low, 0], color='black')


# Plot text
plt.text(1,val_high-5,"Moderately\nAware")
plt.text(1,val_low-5,"Somewhat\nAware")

# Plot adaptive preference
#plt.text(18,10,"X\nAdaptive Preference", color="green")
plt.text(12,5,"X\nAdaptive Preference", color="green")



plt.show()

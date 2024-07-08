import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.optimize import curve_fit

def power_law(x, a, b):
    return a*np.power(x, b)

x_dummy = np.linspace(start=1, stop=1000, num=100)
y_dummy = power_law(x_dummy, 1, 0.5)# Add noise from a Gaussian distribution
noise = 1.5*np.random.normal(size=y_dummy.size)
y_dummy = y_dummy + noise
y_dummy = np.flip(y_dummy)

# Fit the dummy power-law data
pars, cov = curve_fit(f=power_law, xdata=x_dummy, ydata=y_dummy, p0=[0, 0], bounds=(-np.inf, np.inf))# Get the standard deviations of the parameters (square roots of the # diagonal of the covariance)
stdevs = np.sqrt(np.diag(cov))# Calculate the residuals
res = y_dummy - power_law(x_dummy, *pars)

pars[0] = pars[0] * -1
pars[1] = pars[1] * -1

plt.plot(x_dummy, y_dummy, marker='o')
plt.plot(x_dummy, power_law(x_dummy, *pars))
plt.show()

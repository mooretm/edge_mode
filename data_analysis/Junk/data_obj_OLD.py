"""Object for cleaning and exploring data, 
    as well as calculating some descriptive 
    stats.

    Author: Travis M. Moore
    Created: 9 Aug, 2022
    Last Edited: 12 Aug, 2022
"""

# Import data science packages
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt


class Data():
    """Object to clean, set up and perform 
        descriptive stats on a list of data.
    """
    def __init__(self, data):
        self.data = data


    ############################
    # Remove Outliers with MAD #
    ############################
    def remove_outliers(self, dist='normal', k=3):
        """Create a new data list with outliers removed.
        """
        # Call MAD function
        self.calc_mad(dist, k)

        # Get list of data with outliers removed
        vals_clean = []
        for val in self.data:
            if val > self.mad_lwr_lmt and val < self.mad_upr_lmt:
                vals_clean.append(val)
        self.data_no_outliers = vals_clean
        self.removed_outliers = list(set(self.data).symmetric_difference(set(vals_clean)))



    def calc_mad(self, dist='normal', k=3):
        """Calculate the median absolute deviation (MAD) 
            using a slightly different approach.
            
            Values for "k" from Miller (1991):
                *very conservative: 3
                *moderately conservative: 2.5
                *poorly conservative: 2
        """
        # Median of raw values
        raw_median = np.median(self.data)

        # Choose "C" value based on data distribution
        if dist == 'normal':
            C = 1.4826
        elif dist == 'skewed':
            C = 1.4826 # filler value until I figure this out

        # Calculate MAD
        mad = C * np.median([abs(xi - raw_median) for xi in self.data])

        # Calculate upper and lower thresholds for outliers
        upr_lmt = raw_median + (mad * k)
        lwr_lmt = raw_median - (mad * k)

        # Update object attributes
        self.mad = mad
        self.mad_upr_lmt = upr_lmt
        self.mad_lwr_lmt = lwr_lmt





    def calc_mad2(self, dist='normal', strictness='moderately conservative'):
        """Calcuate the median absolute deviation.
            Based on Leys et al. (2013)
        """
        # Set b value based on distribution type
        b = self._calc_b(dist)

        # Set rejection criterion
        # Values from Miller (1991)
        reject_crit_dict = {
            'very conservative': 3,
            'moderately conservative': 2.5,
            'poorly conservative': 2
        }
        reject_criterion = reject_crit_dict[strictness]

        # Calculate median absolute deviation
        med1 = np.median(self.data)
        abs_minus_med = sorted([abs(val - med1) for val in self.data])
        med2 = np.median(abs_minus_med)
        mad = b * med2
        self.mad = mad

        # Calculate upper and lower cutoffs for outliers
        upr_lmt = med1 + (mad * reject_criterion)
        lwr_lmt = med1 - (mad * reject_criterion)
        self.mad_upr_lmt = upr_lmt
        self.mad_lwr_lmt = lwr_lmt



        # Method 2 for upper and lower limits
        med = np.median(self.data)
        abs_minus_med = sorted([abs(val - med1) for val in self.data])
        mad = np.median(abs_minus_med)
        upr_lmt = med + (b * reject_criterion * mad)
        lwr_lmt = med - (b * reject_criterion * mad)
        self.mad = mad
        self.mad_upr_lmt = upr_lmt
        self.mad_lwr_lmt = lwr_lmt



        # # Second method: distance from decision criterion
        # devs = [(val - med1) / mad for val in self.data]
        # for x in devs:
        #     if x > reject_criterion:
        #         print(f"{x} is greater than {reject_criterion}")
        #     elif x < (reject_criterion * -1):
        #         print(f"{x} is less than -{reject_criterion}")


    def _calc_b(self, dist='normal'):
        """Calculate or lookup the value for the constant 
            "b" in the MAD formula.
        """
        # Create ideal distribution
        if dist == 'normal':
            # Create a "perfect" normal dist
            dist = np.random.normal(loc=0, scale=1.0, size=10000)
        else:
            print("{dist} is not supported yet!")

        # Find the 75th quantile
        q75 = np.quantile(dist, 0.75)

        # Calculate b
        b = 1/q75

        # Instead use published value for normal dist
        b = 1.4826 # for normal distributions
        return b


    #####################
    # Normality Testing #
    #####################
    def normal_test(self, plts='n'):
        """Test whether data are normally distributed using 
            the Shapiro test (from scipy.stats).
        """
        # Run Shapiro test
        res = stats.shapiro(self.data)
        # Update dist type attribute
        if res.pvalue < 0.05:
            self.dist_type = 'non-normal'
        else:
            self.dist_type = 'normal'
        # Update mad p-value attribute
        self.shapiro_pvalue = res.pvalue

        # Plot
        if plts == 'y':
            mu = np.mean(self.data)
            sigma = np.std(self.data, ddof=1)
            count, bins, ignored = plt.hist(self.data, 30, density=True)
            plt.plot(bins, 
                1/(sigma * np.sqrt(2 * np.pi))
                * np.exp( - (bins - mu)**2 / (2 * sigma**2)),
                linewidth=2, color='r')
            plt.title(f"The distribution is: {self.dist_type}" + 
                f"\np value: {round(res.pvalue, 2)}")
            plt.show()

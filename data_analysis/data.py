"""Object for cleaning and exploring data.

    Author: Travis M. Moore
    Created: 9 Aug, 2022
    Last Edited: 31 Aug, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import jarque_bera
from scipy.stats import kstest
from scipy.stats import anderson
from scipy.stats import shapiro
from matplotlib import pyplot as plt

# Import system packages
import sys
import os


##############
# Data class #
##############
class Data():
    """Object to clean, set up and perform 
        descriptive stats on a list of data.
    """

    def __init__(self, data):
        self.data = data


    ###################
    # Outlier Testing #
    ###################
    """Think about the Harrell_davis quantile estimator method
        REGARDLESS: comment on the limitations in the code

        https://aakinshin.net/posts/harrell-davis-double-mad-outlier-detector/#conclusion
    """

    def remove_outliers(self, vals, values_colname, dist='normal', k=3, plts='n'):
        """Create new dataframe with outliers removed.
            Optionally plot removed/retained data for inspection.
        """

        # Call MAD function based on distribution type
        if dist == 'normal' or dist == 'symmetrical':
            M, mad = self.calc_mad(dist, vals, values_colname)
            lwr, upr = self._calc_mad_limits(M, mad, k)
        elif dist == 'skewed':
            M, mad_lower, mad_upper = self.calc_double_mad(vals)
            lwr, upr = self._calc_double_mad_limits(M, mad_lower, mad_upper, k)

        # Remove outliers
        clean = vals[vals[values_colname] >= lwr]
        clean = vals[vals[values_colname] <= upr]
        # Alternative method:
        # Used with: _calc_double_mad_distance
        #double_mad_distance = self._calc_double_mad_distance(lwr, upr)
        #removed_outliers = self.data[double_mad_distance > k]
        #data_no_outliers = self.data[double_mad_distance < k]

        num_outliers = vals.shape[0] - clean.shape[0]

        # Plot outliers
        if plts == 'y':
            plt.plot(list(vals), 'ro')
            plt.plot(list(clean), 'go')
            #plt.title(str([clean.index[0][0], clean.index[0][1], clean.index[0][2]]))
            plt.show()

        return num_outliers, clean


    def calc_mad(self, dist='normal', data=None, values_colname=None):
        """Calculate the median absolute deviation (MAD) 
            using a slightly different approach.
        """
        # Median of raw values
        M = np.median(data[values_colname])

        # Choose "C" value based on data distribution
        # Strategies from: https://eurekastatistics.com/using-the-median-absolute-deviation-to-find-outliers/
        if dist == 'normal':
            C = 1.4826
        elif dist == 'symmetrical':
            C = 2/np.sqrt(3) # from 

        # Calculate MAD
        mad = C * np.median([abs(xi - M) for xi in data[values_colname]])

        # Update object attributes
        self.mad = mad

        return M, mad


    def _calc_mad_limits(self, M, mad, k):
        """Values for "k" from Miller (1991):
                *very conservative: 3
                *moderately conservative: 2.5
                *poorly conservative: 2
        """
        # Calculate upper and lower thresholds for outliers
        lwr_lmt = M - (mad * k)
        upr_lmt = M + (mad * k)
        # Update attributes
        self.mad_lwr_lmt = lwr_lmt
        self.mad_upr_lmt = upr_lmt
        
        return lwr_lmt, upr_lmt


    def calc_double_mad(self, data):
        # Set C to 1.4862 until I find a better solution
        C = 1.4862

        # Median of raw values
        M = np.median(data)

        # Get absolute deviation from median for each value
        abs_dev = [abs(xi - M) for xi in data]
        abs_dev = np.array(abs_dev) # convert to numpy array

        # Find data LESS THAN the median
        left_bools = np.array(data <= M)
        left_mad = C * np.median(abs_dev[left_bools])
        # Find data GREATER THAN the median
        right_bools = np.array(data >= M)
        right_mad = C * np.median(abs_dev[right_bools])

        # Check for MAD == 0
        if left_mad == 0:
            left_mad = None
            print('Oops! Less-than MAD is 0')
        if right_mad == 0:
            right_mad == None
            print('Oops! Greater-than MAD is 0')

        # Update attributes
        self.left_mad = left_mad
        self.right_mad = right_mad
        self.mad = (left_mad, right_mad)

        return M, left_mad, right_mad


    def _calc_double_mad_limits(self, M, left_mad, right_mad, k):
        lwr_lmt = M - (k * left_mad)
        upr_lmt = M + (k * right_mad)

        # Update attributes
        self.mad_lwr_lmt = lwr_lmt
        self.mad_upr_lmt = upr_lmt

        return lwr_lmt, upr_lmt


    # Alternative method for double mad outliers
    # def _calc_double_mad_distance(self, lwr, upr):
    #     M = np.median(self.data)
    #     x_mad = np.repeat(lwr,len(self.data))
    #     x_mad[self.data > M] = upr
    #     double_mad_distance = abs(self.data - M) / x_mad
    #     double_mad_distance[self.data==M] = 0

    #     # Update attributes
    #     self.double_mad_distance = double_mad_distance

    #     return(double_mad_distance)


    #####################
    # Normality Testing #
    #####################
    def normality_plots(self, data, title):
        """Create plots that show histogram, probability 
            density function, and QQ plot
        """
        # Histogram
        mu = np.mean(data)
        sigma = np.std(data, ddof=1)
        count, bins, ignored = plt.hist(data, density=True)
        plt.plot(bins, 
            1/(sigma * np.sqrt(2 * np.pi))
            * np.exp( - (bins - mu)**2 / (2 * sigma**2)),
            linewidth=2, color='r')
        plt.title(f"'{title.upper()}' Histogram and PDF")
        plt.xlabel("Raw Data")
        plt.ylabel("Frequency")
        plt.show()

        # QQ plot
        stats.probplot(data, dist='norm', plot=plt)
        plt.title(f"'{title.upper()}' QQ Plot")
        plt.show()


    def normality_tests(self, data, title, output='verbose'):
        """Arsenal of normality tests, complete with summary
        """
        # Formal statistical tests
        jb = Jarque_Bera(data, output)
        jb.run()
        ks = Kolmogorov_Smirnov(data, output)
        ks.run()
        ad = Anderson_Darling(data, output)
        ad.run()
        sw = Shapiro_Wilk(data, output)
        sw.run()
        print('-'*80)
        print(f"Tests for {title.upper()} condition")
        ad.show_summary()


#################################
# CLASSES FOR NORMALITY TESTING #
#################################
class NormalityTestTemplate():
    """Class for a battery of normality tests, using
         the template pattern
    """

    # Class-level variable to hold all test results
    test_results = {}

    def __init__(self, data, output='verbose'):
        """Initialize attributes
        """
        self.data = data
        self.output = output
        self.test_name = None
        self.hypothesis = None
        self.pvalue = None
        self.statistic = None

    def perform_test(self):
        """This method should be overriden with a specific 
            normality test when subclassed.
        """
        raise NotImplementedError()

    def show_results(self):
        """Print results to command line
        """
        print('-' * 80)
        print(f"{self.test_name} statistic: {self.statistic}")
        print(f"{self.test_name} p-value: {self.pvalue}")
        print('')
        print(self.hypothesis1)
        print(self.hypothesis2)
        print(('-' * 80) + '\n')

    def show_summary(self):
        """Print summary table to command line
        """
        summary = pd.Series(self.test_results)
        print('-' * 80)
        print("SUMMARY")
        print(summary)
        print(('-' * 80) + '\n')

    def run(self):
        """Carry out steps for normality testing
        """
        self.perform_test()
        if self.output == 'verbose':
            self.show_results()


class Jarque_Bera(NormalityTestTemplate):
    """Jarque-Bera test for skewness and kurtosis.

        -H0: skewness and kurtosis are not significantly 
            different from a normal distribution
        -p > 0.05, fail to reject H0, normally distributed
    """

    def perform_test(self):
        """Perform Jarque-Bera test of normality and 
            interpret results
        """
        jb = (jarque_bera(self.data))
        self.test_name = 'Jarque-Bera'
        self.statistic = np.round(jb[0], 4)
        self.pvalue = np.round(jb[1], 4)

        result = jb[1] < 0.05
        if not result:
            self.hypothesis1 = "Jarque-Bera p-value > 0.05"
            self.hypothesis2 = "Fail to reject H0: data are normally distributed"
            self.test_results['Jarque-Bera'] = 'normal'
        else:
            self.hypothesis1 = "Jarque-Bera p-value < 0.05"
            self.hypothesis2 = "Reject H0: data NOT normally distributed"
            self.test_results['Jarque-Bera'] = 'NOT normal'


class Kolmogorov_Smirnov(NormalityTestTemplate):
    """Kolmogorov-Smirnov normality test
    
        -This compares "empirical cumulative distribution functions"
        -H0: two samples are from the same distribution
        -p > 0.05, fail to reject H0, normally distributed
        -Can plot, but unnecessary
    """

    def perform_test(self):
        """Perform Kolmogorov test of normality and 
            interpret results
        """
        ks = (kstest(self.data, cdf='norm'))
        self.test_name = 'Kolmogorov_Smirnov'
        self.statistic = np.round(ks[0], 4)
        self.pvalue = np.round(ks[1], 4)

        result = ks[1] < 0.05
        if not result:
            self.hypothesis1 = "Kolmogorov_Smirnov p-value > 0.05"
            self.hypothesis2 = "Fail to reject H0: data normally distributed"
            self.test_results['Kolmogorov_Smirnov'] = 'normal'
        else:
            self.hypothesis1 = "Kolmogorov_Smirnov p-value < 0.05"
            self.hypothesis2 = "Reject H0: data NOT normally distributed"
            self.test_results['Kolmogorov_Smirnov'] = 'NOT normal'

        # Plotting, but not implemented
        # data_norm = np.random.normal(np.mean(data), 
        #     np.std(data), len(data))
        # sns.ecdfplot(data, c='blue')
        # sns.ecdfplot(data_norm, c='green')
        # if plts == 'y':
        #     plt.show()


class Anderson_Darling(NormalityTestTemplate):
    """Anderson-Darling test for normality.

        -More powerful than K-S because it considers all values
        -H0: the data come from a specified distribution
        -p > 0.05, fail to reject H0, normally distributed
        -Test at alpha=0.05, but other levels are possible
    """

    def perform_test(self):
        """Perform Anderson-Darling test of normality and 
            interpret results
        """
        ad = (anderson(self.data, dist='norm'))
        self.test_name = 'Anderson-Darling'
        self.statistic = np.round(ad[0], 4)
        # Note this is not really a p-value, but
        # a critical value
        self.pvalue = np.round(ad[1][2], 4)
        #print(f"Significance levels: {ad[2]}")

        result = ad[0] < ad[1][2]
        if not result:
            self.hypothesis1 = f"Test stat {np.round(ad[0],4)} > crit val {np.round(ad[1][2],4)}"
            self.hypothesis2 = "Reject H0: data NOT normally distributed"
            self.test_results['Anderson-Darling'] = 'NOT normal'
        else:
            self.hypothesis1 = f"Test stat {np.round(ad[0],4)} < crit val {np.round(ad[1][2],4)}"
            self.hypothesis2 = "Fail to reject H0: data normally distributed"
            self.test_results['Anderson-Darling'] = 'normal'


class Shapiro_Wilk(NormalityTestTemplate):
    """Shapiro-Wilk test for normality.
    
        -H0: sample dist not different from normal dist
        -p > 0.05, fail to reject H0, normally distributed
    """

    def perform_test(self):
        """Perform Shapiro-Wilk test of normality and 
            interpret results
        """
        sw = (shapiro(self.data))
        self.test_name = 'Shapiro-Wilk'
        self.statistic = round(sw[0], 4)
        self.pvalue = np.round(sw[1], 4)

        result = sw[1] < 0.05
        if not result:
            self.hypothesis1 = "Shapiro-Wilk p-value > 0.05"
            self.hypothesis2 = "Fail to reject H0: data normally distributed"
            self.test_results['Shapiro-Wilk'] = 'normal'
        else:
            self.hypothesis1 = "Shapiro-Wilk p-value < 0.05"
            self.hypothesis2 = "Reject H0: data NOT normally distributed"
            self.test_results['Shapiro-Wilk'] = 'NOT normal'


########################
# MISCELLANEOUS CLASSES #
########################
class NoStdStreams():
    """Context manager to suppress print statements
    """
    def __init__(self, stdout=None, stderr=None):
        self.devnull = open(os.devnull, 'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._sdterr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()

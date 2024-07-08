"""Unit tests for Data class. 

    Author: Travis M. Moore
    Created: 11 Aug, 2022
    Last Edited: 15 Aug, 2022
"""

###################
# Import packages #
###################
# Import testing packages
import unittest
from unittest import mock

# Import data science packages
import numpy as np
import pandas as pd

# Import custom module for testing
import data as do


###################
# Normality Tests #
###################
class TestNormalityTests(unittest.TestCase):
    def setUp(self):
        # Set class random seed
        r = np.random.RandomState(1)
        self.normal_dist = r.normal(loc=0, scale=1.0, size=200)
        self.exp_dist = r.exponential(scale=2, size=200)

    def test_jarque_bera_normal(self):
        jb = do.Jarque_Bera(self.normal_dist, 'verbose')
        jb.run()
        self.assertGreater(jb.pvalue, 0.05)

    def test_jarque_bera_nonnormal(self):
        jb = do.Jarque_Bera(self.exp_dist, 'verbose')
        jb.run()
        self.assertLess(jb.pvalue, 0.05)

    def test_kolmogorov_smirnov_normal(self):
        ks = do.Kolmogorov_Smirnov(self.normal_dist, 'verbose')
        ks.run()
        self.assertGreater(ks.pvalue, 0.05)

    def test_kolmogorov_smirnov_nonnormal(self):
        ks = do.Kolmogorov_Smirnov(self.exp_dist, 'verbose')
        ks.run()
        self.assertLess(ks.pvalue, 0.05)

    def test_anderson_darling_normal(self):
        ad = do.Anderson_Darling(self.normal_dist, 'verbose')
        ad.run()
        self.assertGreater(ad.pvalue, ad.statistic)

    def test_anderson_darling_nonnormal(self):
        ad = do.Anderson_Darling(self.exp_dist, 'verbose')
        ad.run()
        self.assertLess(ad.pvalue, ad.statistic)

    def test_shapiro_wilk_normal(self):
        sw = do.Shapiro_Wilk(self.normal_dist, 'verbose')
        sw.run()
        self.assertGreater(sw.pvalue, 0.05)

    def test_shapiro_wilk_nonnormal(self):
        sw = do.Shapiro_Wilk(self.exp_dist, 'verbose')
        sw.run()
        self.assertLess(sw.pvalue, 0.05)


@unittest.skip("Don't know how to test plots...")
class TestNormalityPlots(unittest.TestCase):
    def setUp(self):
        vals = {
            'subject':[1, 1, 1, 2, 2, 2],
            'A': np.array([25,30,28,36,29,27]),
            'B': np.array([55,55,59,56,50,5]),
            'C': np.array([30,29,133,37,27,35])
        }
        vals = pd.DataFrame(vals)
        df = pd.melt(vals.reset_index(),
            id_vars=['subject'], 
            value_vars=['A', 'B', 'C'])
        df.columns = ['subject', 'condition', 'rating']
        self.data = do.Data(df)


#################
# Outlier Tests #
#################
class TestMADFunc(unittest.TestCase):
    def setUp(self):
        vals = {
            'subject': np.repeat(1,8),
            'values': np.array([1,3,3,6,8,10,10,1000])
        }
        df = pd.DataFrame(vals)
        self.data = do.Data(df)

    def test_mad(self):
        M, mad = self.data.calc_mad(dist='normal', data=self.data.data['values'])
        self.assertEqual(M, 7)
        self.assertEqual(round(mad, 4), 5.1891)

    def test_mad_limits(self):
        M, mad = self.data.calc_mad(dist='normal', data=self.data.data['values'])
        self.data._calc_mad_limits(M, mad, k=3)
        self.assertEqual(round(self.data.mad_upr_lmt, 2), 22.57)
        self.assertEqual(round(self.data.mad_lwr_lmt, 2), -8.57)


class TestDoubleMADFunc(unittest.TestCase):
    def setUp(self):
        vals = {
            'subject': np.repeat(1,19),
            'values': np.array([100,101,102,103,110,111,112,120,
            121,122,140,160,180,200,220,240,2000,2001,2002])
        }
        df = pd.DataFrame(vals)
        self.data = do.Data(df)
        self.k = 3

    def test_double_mad(self):
        M, l, r = self.data.calc_double_mad(self.data.data['values'])
        self.assertEqual(M, 122)
        self.assertEqual(self.data.mad, (17.0913, 130.7856))

    def test_double_mad_limits(self):
        M, l, r = self.data.calc_double_mad(self.data.data['values'])
        self.data._calc_double_mad_limits(M,l,r,self.k)
        self.assertEqual(self.data.mad_lwr_lmt, 70.7261)
        self.assertEqual(self.data.mad_upr_lmt, 514.3568)


@unittest.skip('Under construction')
class TestRemoveOutliersMAD(unittest.TestCase):
    """Remove outliers using normal MAD.
    """
    def setUp(self):
        vals = {
            'subject': np.repeat(1,8),
            'values': np.array([1,3,3,6,8,10,10,1000])
        }
        df = pd.DataFrame(vals)
        self.data = do.Data(df)
        self.data.remove_outliers(
            dist='normal', 
            k=3, 
            factor_colname='values', 
            colname='values', 
            plts='n')

    def test_mad_removed(self):
        self.assertEqual(self.data.removed_outliers, np.array([1000]))
        self.assertNotIn(self.data.removed_outliers, np.array([1,3,3,6,8,10,10]))

    def test_mad_retained(self):
        self.assertIn(self.data.data_no_outliers, np.array([1,3,3,6,8,10,10]))
        self.assertNotIn(self.data.data_no_outliers, np.array([1000]))


@unittest.skip('Under construction')
class TestRemoveOutliersDoubleMAD(unittest.TestCase):
    """Remove outliers using double MAD.
    """
    def setUp(self):
        self.vals = np.array([100,101,102,103,110,111,
            112,120,121,122,140,160,180,200,220,240,2000,
            2001,2002])
        self.x = Data(self.vals)
        self.x.remove_outliers(dist='skewed', k=3)

    def test_double_mad_removed(self):
        self.assertEqual(list(self.x.removed_outliers), 
            [2000, 2001, 2002])

    def test_double_mad_retained(self):
        self.assertNotIn(list(self.x.removed_outliers), 
            [100,101,102,103,110,111,112,
                120,121,122,140,160,180,200,220,240])

# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 13:08:37 2020

Author: Josef Perktold
License: BSD-3

"""

import numpy as np
import pandas as pd

from numpy.testing import assert_equal, assert_allclose

from statsmodels.regression.linear_model import WLS
from statsmodels.genmod.generalized_linear_model import GLM

from statsmodels.stats.meta_analysis import (
    effectsize_smd, combine_effects, _fit_tau_iterative,
    _fit_tau_mm, _fit_tau_iter_mm)

from .results import results_meta


class TestMetaK1(object):

    @classmethod
    def setup_class(cls):

        cls.eff = np.array([61.00, 61.40, 62.21, 62.30, 62.34, 62.60, 62.70,
                            62.84, 65.90])
        cls.var_eff = np.array([0.2025, 1.2100, 0.0900, 0.2025, 0.3844, 0.5625,
                                0.0676, 0.0225, 1.8225])

    def test_tau_kacker(self):
        # test iterative and two-step methods, Kacker 2004
        # PM CA DL C2 from table 1 first row p. 135
        # test for PM and DL are also against R metafor in other tests
        eff, var_eff = self.eff, self.var_eff
        t_PM, t_CA, t_DL, t_C2 = [0.8399, 1.1837, 0.5359, 0.9352]

        tau2, converged = _fit_tau_iterative(eff, var_eff,
                                             tau2_start=0.1, atol=1e-8)
        assert_equal(converged, True)
        assert_allclose(np.sqrt(tau2), t_PM, atol=6e-5)

        k = len(eff)
        # cochrane uniform weights
        tau2_ca = _fit_tau_mm(eff, var_eff, np.ones(k) / k)
        assert_allclose(np.sqrt(tau2_ca), t_CA, atol=6e-5)

        # DL one step, and 1 iteration, reduced agreement with Kacker
        tau2_dl = _fit_tau_mm(eff, var_eff, 1 / var_eff)
        assert_allclose(np.sqrt(tau2_dl), t_DL, atol=1e-3)

        tau2_dl_, converged = _fit_tau_iter_mm(eff, var_eff, tau2_start=0,
                                               maxiter=1)
        assert_equal(converged, False)
        assert_allclose(tau2_dl_, tau2_dl, atol=1e-10)

        # C2 two step, start with CA
        tau2_c2, converged = _fit_tau_iter_mm(eff, var_eff,
                                              tau2_start=tau2_ca,
                                              maxiter=1)
        assert_equal(converged, False)
        assert_allclose(np.sqrt(tau2_c2), t_C2, atol=6e-5)

    def test_pm(self):
        res = results_meta.exk1_metafor
        eff, var_eff = self.eff, self.var_eff

        tau2, converged = _fit_tau_iterative(eff, var_eff,
                                             tau2_start=0.1, atol=1e-8)
        assert_equal(converged, True)
        assert_allclose(tau2, res.tau2, atol=1e-10)

    def test_dl(self):
        res = results_meta.exk1_dl
        eff, var_eff = self.eff, self.var_eff

        tau2 = _fit_tau_mm(eff, var_eff, 1 / var_eff)
        assert_allclose(tau2, res.tau2, atol=1e-10)

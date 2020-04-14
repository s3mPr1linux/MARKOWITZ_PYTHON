import math
import warnings

import numpy as np
import pandas as pd
import cvxpy as cp
import pandas_datareader as data

from .Exceptions import *
from .MetricGen import *

### https://www.portfolioprobe.com/features/constraints/


class ConstraintGen(MetricGen):


    def __init__(self, weight_param, ret_vec, moment_mat, moment, assets):

        # self.weight_param = weight_param
        # self.ret_vec = ret_vec
        # self.moment_mat = moment_mat
        # self.moment = moment
        super().__init__(weight_param, ret_vec, moment_mat, moment, assets)

        self.method_dict = {"weight": self.weight,
                            "leverage": self.leverage,
                            "max_num_assets": self.num_assets,
                            "concentration": self.concentration}

    def create_constraint(self, constraint_type, **kwargs):
        return self.method_dict[constraint_type](**kwargs)

    # Weight Only
    def weight(self, weight_bound, total_weight):

        constraints = []
        if isinstance(weight_bound, (list, tuple)):
            if isinstance(weight_bound[0], (list, tuple)):
                if all([len(ind_weights) == 2 for ind_weights in weight_bound]) and len(weight_bound) == self.ret_vec.shape[0]:
                    weight_bound = np.array(weight_bound)
                else:
                    raise DimException("""If specifying weight for each individual asset, must be passed in pairs and 
                                            its length must equal the number of assets""")
            elif isinstance(weight_bound[0], (float, int)):
                constraints += [self.weight_param >= weight_bound[0]]
                constraints += [self.weight_param <= weight_bound[1]]
            else:
                raise FormatException("""Please pass in weight boundaries in an accepted format. List/Tuple/Np.ndarray""")

        if isinstance(weight_bound, np.ndarray):
            if weight_bound.ndim == 1:
                constraints += [self.weight_param >= weight_bound[0]]
                constraints += [self.weight_param <= weight_bound[1]]
            elif weight_bound.ndim == 2:
                if weight_bound.shape != (self.ret_vec.shape[0], 2):
                    raise DimException("Dimension of Weights does not match number of assets")
                constraints += [self.weight_param >= weight_bound[:, 0]]
                constraints += [self.weight_param <= weight_bound[:, 1]]
            else:
                raise DimException("Dimension of Weight Bound Array must be 1/2")
        else:
            raise FormatException("Weight bound needs to be in list/tuple/np.ndarray format")

        constraints += [cp.sum(self.weight_param) == total_weight]
        return constraints

    def leverage(self, upper_bound):
        return [cp.norm(self.weight_param, 1) == upper_bound]

    def num_assets(self, max_num_assets):
        if self.ret_vec[0].shape <= max_num_assets:
            warnings.warn("""The number of assets to hold exceeds the number of assets available, 
            default to a 1 asset only scenario""")
            max_num_assets = self.ret_vec[0].shape - 1
        return [cp.sum_smallest(self.weight_param, self.ret_vec[0].shape - max_num_assets) == 0]

    def concentration(self, top_holdings, top_concentration):
        if self.ret_vec[0].shape <= top_holdings:
            warnings.warn("""Number of Top Holdings Exceeds Total Available Assets. 
            Will default top_holdings to be number of holdings available""")
            top_holdings = self.ret_vec[0].shape
        return [cp.sum_largest(cp.abs(self.weight_param), top_holdings) <= top_concentration]

    ### Market Data Needed/Calculation Needed
    def market_neutral(self, bound):

        market_cap_weight = self.market_cap_data()
        return [market_cap_weight @ self.moment_mat @ self.weight_param >= bound[0],
                market_cap_weight @ self.moment_mat @ self.weight_param <= bound[1]]


    ### Portfolio Variance is easy to calculate but others are hard
    def beta(self):
        pass

    def risk_fraction(self):
        pass

    def sortino(self):
        pass

    def calmar(self):
        pass

    def omega(self):
        pass

    def treynor(self):
        pass

    def sharpe(self):
        pass

    def tracking_error(self):
        pass

    def expected_return_const(self, bound):
        return [self.expected_return() >= bound[0], self.expected_return() <= bound[1]]

    def volatility_const(self, bound):
        return [self.volatility() >= bound[0], self.volatility <= bound[1]]

    def variance_const(self, bound):
        if self.moment != 2:
            raise DimException("Did not pass in a correlation/covariance matrix")
        return [self.variance() >= bound[0],
                self.variance() <= bound[1]]

    def skew_const(self, bound):
        if self.moment != 3:
            raise DimException("Did not pass in a coskewness matrix")
        return [self.higher_moment(3) >= bound[0], self.higher_moment(3) <= bound[1]]

    def kurt_const(self, bound):
        if self.moment != 5:
            raise DimException("Did not pass in a cokurtosis matrix")
        return [self.higher_moment(4) >= bound[0], self.higher_moment(4) <= bound[1]]









    # def __init__(self, ret_data, moment_data, moment, weight_params):
    #
    #     self.ret_data = ret_data
    #     self.moment_data = moment_data
    #     self.moment = moment
    #     self.weight_params = weight_params
    #
    #     self.objective = None
    #     self.constraints = []
    #
    #     self.constraint_dict = {}
    #     self.objective_dict = {}
    #
    #
    # def add_objective(self, obj_type, **kwargs):
    #     self.objective = self.objective_dict[obj_type](**kwargs)
    #
    # def add_constraint(self, const_type, **kwargs):
    #     self.constraints += self.constraint_dict[const_type](**kwargs)










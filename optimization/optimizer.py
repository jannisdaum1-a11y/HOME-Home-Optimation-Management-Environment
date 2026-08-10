import numpy as np
import pandas as pd
import pyomo.environ as pyo

from data_collection.config import get_config
from data_collection.prices import Prices


class Optimizer():
    objects = {}

    def __init__(self, import_prices: Prices = None, export_prices: Prices = None):
        self.import_prices = import_prices
        self.export_prices = export_prices

        self.model = pyo.ConcreteModel()
        


    @staticmethod
    def register_object(obj):
        Optimizer.objects[obj.name] = obj

    def implementation(self):
        active_config = get_config()
        self.model.t = pyo.Set(initialize=pd.date_range(start=active_config.start_date, end=active_config.end_date, freq=active_config.timestep))

        # Variables
        self.model.p_exchange = pyo.Var(self.model.t, domain=pyo.Reals, bounds=(active_config.p_grid_min, active_config.p_grid_max), initialize=0)
        for obj in Optimizer.objects.values():
            #ToDo
        

        
from .asset import Asset
from ..optimization.optimizer import Optimizer
from ..data_collection.weather import Weather
from ..data_collection.config import get_config
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from pyomo.environ import ConcreteModel, Param, Var, NonNegativeReals

class LoadProfile(Asset):
    loads = {}
    total_load = pd.Series(dtype=float)
    def __init__(self):
        active_config = get_config()
        start_date = active_config.start_date
        end_date = active_config.end_date
        time_delta = active_config.timestep
        self.load_profile = pd.Series(
            index=pd.date_range(start=start_date, end=end_date - time_delta, freq=time_delta),
            dtype=float,
            data=np.zeros(len(pd.date_range(start=start_date, end=end_date - time_delta, freq=time_delta)))
            )
        self.calculate_load_profile()

        super().__init__()

        Optimizer.register_object(self)

    def create_variables(self, model:ConcreteModel):
        p_load = Param(model.t, initialize=self.load_profile.to_dict())
        setattr(model, f"p_{self.name}", p_load)
        return 

    def create_constraints(self, model:ConcreteModel):
        model.power_balance_rhs_terms.append(getattr(model, f"p_{self.name}"))
        return


    def register_load(self):
        LoadProfile.loads[self.name] = self
        LoadProfile.total_load += self.load_profile

    @abstractmethod
    def calculate_load_profile(self):
        pass


class ConstantLoadProfile(LoadProfile):
    counter = 0
    def __init__(self, constant_load, name="ConstantLoad"):
        self.name = f"{name}_{ConstantLoadProfile.counter}"
        ConstantLoadProfile.counter += 1
        self.constant_load = constant_load
        super().__init__()
        
    def calculate_load_profile(self):
        self.load_profile[:] = self.constant_load
from .asset import Asset
from ..optimization.optimizer import Optimizer
from ..data_collection.weather import Weather
from ..data_collection.config import get_config
from ..data_collection.timeseries import TimeSeries
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from pyomo.environ import ConcreteModel, Param, Var, NonNegativeReals

class LoadProfile(Asset):
    counter = 0
    loads = {}
    total_load = pd.Series(dtype=float)
    def __init__(self, name, **kwargs):
        active_config = get_config()
        self.name = f"{name}_{LoadProfile.counter}"
        LoadProfile.counter += 1
        start_date = active_config.start_date
        end_date = active_config.end_date
        time_delta = active_config.timestep
        self.load_profile = TimeSeries(
            self.calculate_load_profile()["load"]
        ).data
        

        super().__init__()

        Optimizer.register_object(self)

    def create_variables(self, model:ConcreteModel):
        p_load = Param(model.t, initialize=self.load_profile.to_dict())
        setattr(model, f"p_{self.name}", p_load)
        return 

    def create_constraints(self, model:ConcreteModel):
        model.power_balance_rhs_terms.append(getattr(model, f"p_{self.name}"))
        return

    def expand_objective(self, model:ConcreteModel):
        return


    def register_load(self):
        LoadProfile.loads[self.name] = self
        LoadProfile.total_load += self.load_profile

    @abstractmethod
    def calculate_load_profile(self):
        pass


class ConstantLoadProfile(LoadProfile):
    def __init__(self, constant_load, **kwargs):
        self.constant_load = constant_load
        super().__init__(**kwargs)
        
    def calculate_load_profile(self):
        config = get_config()
        start = config.start_date
        end = config.end_date
        timedelta = config.timestep
        index = pd.date_range(start=start, end=end, freq=timedelta)
        return pd.DataFrame([self.constant_load]*len(index), index=index, columns=["load"])

class StandardLoadProfile(LoadProfile):
    def __init__(self, normalized_load=1000, **kwargs):
        self.normalized_load = normalized_load
        super().__init__(**kwargs)
        
    def calculate_load_profile(self):
        data = pd.read_csv("data/StandardLoadProfile.csv", encoding="cp1252", sep=";", header=[0,1], index_col=0, decimal=",")

        config = get_config()
        start = config.start_date
        end = config.end_date
        timedelta = config.timestep
        timerange = pd.date_range(start=start, end=start + pd.DateOffset(years=1), freq=timedelta)

        data.index = data.index.str[:5]

        series = []
        for t in timerange:
            n_month= t.month
            n_day = t.day_of_week
            n_h = data.index.get_loc(t.strftime("%H:%M"))
            month_col = (n_month -1) * 3
            if n_day == 7: #Sonntag
                month_col += 1
            elif n_day == 6: #Samstag
                month_col += 0
            else:
                month_col += 2
            series.append(data.iloc[n_h, month_col])

        load_series = pd.DataFrame(index=timerange)
        load_series["load"] = series

        timestep_hours = timedelta.total_seconds() / 3600
        load_series = load_series/load_series.sum()
        load_series = load_series *self.normalized_load*1000/timestep_hours #*1000->kWh->Wh

        return load_series
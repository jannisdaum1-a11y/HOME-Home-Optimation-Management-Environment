import numpy as np
from ..data_collection.weather import Weather
from ..optimization.optimizer import Optimizer

from ..data_collection.config import get_config
from ..data_collection.timeseries import TimeSeries
from .asset import Asset

from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Param, Constraint

class PV(Asset):
    counter = 0
    def __init__(self,
                 rated_power,
                 name= "PV",
                 lat=None,
                 lon=None,
                 tilt=0,
                 azimuth=0,
                 performance_ratio=100,
                 temperature_coefficient=-0.005,
                 spec_capex=1000,
                 lifetime=False,
                 wacc=False,
                 expandable=False,
                 power_limit=1000000,
                **kwargs
                 ):
        active_config = get_config()
        self.name = f"{name}_{PV.counter}"
        PV.counter += 1
        self.rated_power = rated_power
        self.capacity = rated_power
        self.lat = lat if lat is not None else getattr(active_config, "lat", None)
        self.lon = lon if lon is not None else getattr(active_config, "lon", None)
        self.tilt = tilt
        self.azimuth = azimuth
        self.performance_ratio = performance_ratio/100
        self.temperature_coefficient = temperature_coefficient
        self.weather = Weather(self.lat, self.lon, tilt=tilt, azimuth=azimuth)

        self.expandable = expandable
        self.power_limit = power_limit
        self.spec_capex = spec_capex

        super().__init__(expandable,lifetime, wacc) 
        Optimizer.register_object(self)
        

    def calculate_pv_output_factor(self):
        weather_data = self.weather.fetch_weather_data()
        pv_output_factor = self.performance_ratio * (weather_data["specific_radiation"] / 1000) * (1 + self.temperature_coefficient * (weather_data["temperature"] - 25))
        return pv_output_factor

    def create_variables(self, model: ConcreteModel):

        pv_output_factor = self.calculate_pv_output_factor()
        output_factor = Param(
            model.t,
            initialize=lambda _, t: float(pv_output_factor.loc[t]),
            mutable=False,
        )
        setattr(model, f"pv_output_factor_{self.name}", output_factor)

        if self.expandable:
            capacity = Var(
                domain=NonNegativeReals,
                bounds=(0, self.power_limit)
            )
        else:
            capacity = Param(
                initialize=self.capacity,
                mutable=False
            )

        setattr(model, f"P_rated_{self.name}", capacity)

        p_pv = Var(
            model.t,
            domain=NonNegativeReals,
            initialize=0
        )

        setattr(model, f"p_{self.name}", p_pv)


    def create_constraints(self, model:ConcreteModel):
        model.power_balance_lhs_terms.append(getattr(model, f"p_{self.name}"))

        def pv_limit_rule(model, t):
            return getattr(model, f"p_{self.name}")[t] <= getattr(model, f"P_rated_{self.name}") * getattr(model, f"pv_output_factor_{self.name}")[t]

        model.add_component(
            f"pv_limit_{self.name}",
            Constraint(model.t, rule=pv_limit_rule)
        )
        
        return

    def expand_objective(self, model:ConcreteModel):
        if self.expandable:
            model.obj +=  self.spec_capex * getattr(model, f"P_rated_{self.name}") * self.annuity_factor()
        else:
            model.obj += self.spec_capex * self.capacity * self.annuity_factor()
        return

    def get_capex(self, model):
        return self.spec_capex * getattr(model, f"P_rated_{self.name}")

    def get_discounted_capex(self, model):
        return self.spec_capex * getattr(model, f"P_rated_{self.name}") * self.annuity_factor()



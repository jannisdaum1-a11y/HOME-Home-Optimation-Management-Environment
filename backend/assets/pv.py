import numpy as np
from ..data_collection.weather import Weather
from ..optimization.optimizer import Optimizer

from ..data_collection.config import get_config
from .asset import Asset

from pyomo.environ import ConcreteModel, Var, NonNegativeReals

class PV(Asset):
    counter = 0
    def __init__(self,
                 rated_power,
                 name= "PV",
                 lat=None,
                 lon=None,
                 tilt=0,
                 azimuth=0,
                 performance_ratio=1,
                 temperature_coefficient=-0.005,
                 spec_capex=1000,
                 lifetime=False,
                 wacc=False,
                 expandable=False,
                **kwargs
                 ):
        active_config = get_config()
        self.name = f"{name}_{PV.counter}"
        PV.counter += 1
        self.rated_power = rated_power
        self.lat = lat if lat is not None else getattr(active_config, "lat", None)
        self.lon = lon if lon is not None else getattr(active_config, "lon", None)
        self.tilt = tilt
        self.azimuth = azimuth
        self.performance_ratio = performance_ratio
        self.temperature_coefficient = temperature_coefficient
        self.weather = Weather(self.lat, self.lon, tilt=tilt, azimuth=azimuth)
        self.pv_output = self.calculate_pv_output()

        super().__init__(expandable,rated_power*spec_capex, lifetime, wacc) 
        Optimizer.register_object(self)
        

    def calculate_pv_output(self):
        weather_data = self.weather.fetch_weather_data()
        pv_output = self.rated_power * self.performance_ratio * (weather_data["specific_radiation"] / 1000) * (1 + self.temperature_coefficient * (weather_data["temperature"] - 25))
        return pv_output

    def create_variables(self, model:ConcreteModel):
        def _p_bounds(model, t):
            return (0, self.pv_output[t])
        p_pv = Var(model.t, domain=NonNegativeReals, bounds=_p_bounds, initialize=0)
        setattr(model, f"p_{self.name}", p_pv)

    def create_constraints(self, model:ConcreteModel):
        model.power_balance_lhs_terms.append(getattr(model, f"p_{self.name}"))
        return



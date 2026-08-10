import numpy as np
from data_collection.weather import Weather
from optimization.optimizer import Optimizer

from data_collection.config import get_config

class PV():
    counter = 0
    def __init__(self, rated_power, name= "PV",lat=None, lon=None, tilt=0, azimuth=0, performance_ratio=1, temperature_coefficient=-0.005):
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

        Optimizer.register_object(self)
        

    def calculate_pv_output(self):
        weather_data = self.weather.fetch_weather_data()
        pv_output = self.rated_power * self.performance_ratio * (weather_data["specific_radiation"] / 1000) * (1 + self.temperature_coefficient * (weather_data["temperature"] - 25))
        return pv_output
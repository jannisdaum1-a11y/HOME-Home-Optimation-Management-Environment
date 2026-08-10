import numpy as np
from data_collection.weather import Weather
import pandas as pd
from data_collection.config import get_config
from abc import ABC, abstractmethod

class LoadProfile(ABC):
    def __init__(self):
        active_config = get_config()
        start_date = active_config.start_date
        end_date = active_config.end_date
        time_delta = active_config.timestep
        self.load_profile = pd.Series(index=pd.date_range(start=start_date, end=end_date, freq=time_delta))
        self.calculate_load_profile()

    @abstractmethod
    def calculate_load_profile(self):
        pass

class ConstantLoadProfile(LoadProfile):
    def __init__(self, constant_load):
        self.constant_load = constant_load
        super().__init__()
        
    def calculate_load_profile(self):
        self.load_profile[:] = self.constant_load
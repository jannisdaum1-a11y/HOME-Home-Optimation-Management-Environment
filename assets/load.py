from data_collection.demand import LoadProfile
from optimization.optimizer import Optimizer
import numpy as np
import pandas as pd


class ConstantLoadProfile(LoadProfile):
    counter = 0
    def __init__(self, constant_load, name="ConstantLoad"):
        self.name = f"{name}_{ConstantLoadProfile.counter}"
        ConstantLoadProfile.counter += 1
        self.constant_load = constant_load
        super().__init__()
        
    def calculate_load_profile(self):
        self.load_profile[:] = self.constant_load
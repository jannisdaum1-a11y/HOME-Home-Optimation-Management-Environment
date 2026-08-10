import numpy as np
import pandas as pd
import pyomo.environ as pyo

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
        
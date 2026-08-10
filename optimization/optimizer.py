import numpy as np
import pandas as pd
import pyomo.environ as pyo


class Optimizer():
    objects = {}

    def __init__(self):
        self.model = pyo.ConcreteModel()

    @staticmethod
    def register_object(obj):
        Optimizer.objects[obj.name] = obj
        
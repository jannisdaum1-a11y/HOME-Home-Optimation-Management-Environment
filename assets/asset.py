from abc import abstractmethod
from pyomo.environ import ConcreteModel

class Asset:

    @abstractmethod
    def __init__(self):
        return

    @abstractmethod
    def create_variables(self, model:ConcreteModel):
        return 

    @abstractmethod
    def create_constraints(self, model:ConcreteModel):
        return 


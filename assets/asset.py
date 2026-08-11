from abc import abstractmethod
from pyomo.environ import ConcreteModel

class Asset:

    @abstractmethod
    def __init__(self):
        return

    @abstractmethod
    def create_variables(self, model:ConcreteModel):
        """
        Create the variables for the asset in the optimization model.
        """
        return 

    @abstractmethod
    def create_constraints(self, model:ConcreteModel):
        """
        Create the constraints for the asset in the optimization model.
        """
        return


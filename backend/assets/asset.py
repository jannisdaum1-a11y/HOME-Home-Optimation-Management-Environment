from abc import abstractmethod
from pyomo.environ import ConcreteModel

from ..data_collection.config import get_config

class Asset:

    @abstractmethod
    def __init__(self,expandable=False, lifetime=0, wacc=0, **kwargs):
        self.lifetime = lifetime
        self.expandable = expandable

        # General wacc or specific
        if wacc:
            self.wacc = wacc/100
        elif get_config().wacc:
            self.wacc = get_config().wacc/100
        else:
            self.wacc = 0

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

    @abstractmethod
    def expand_objective(self, model:ConcreteModel):
        """
        Add cost terms for objective function
        """
        return

    def annuity_factor(self):
        """Return the annualized Factor using the capital recovery factor."""
        if self.lifetime <= 0:
            raise ValueError("lifetime must be greater than zero")

        if self.wacc == 0:
            return 1 / self.lifetime

        growth_factor = (1 + self.wacc) ** self.lifetime
        startdate = get_config().start_date
        enddate = get_config().end_date
        year_share = (enddate-startdate).total_seconds() / (365*24*60*60)
        return  self.wacc * growth_factor / (growth_factor - 1) *year_share

    def get_discounted_capex(self, model):
        return 0

    def get_capex(self, model):
        return 0


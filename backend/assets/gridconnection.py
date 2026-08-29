from .asset import Asset
from .asset import Asset
from ..optimization.optimizer import Optimizer
from ..data_collection.weather import Weather
from ..data_collection.config import get_config
from ..data_collection.timeseries import TimeSeries
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from pyomo.environ import ConcreteModel, Param, Var, NonNegativeReals, Binary, Constraint, Reals

class GridConnection(Asset):
    counter = 0
    def __init__(self, import_prices:pd.DataFrame, export_prices:pd.DataFrame,p_grid_max:float, p_grid_min:float,name:str,**kwargs):
        self.name = f"{name}_{GridConnection.counter}"
        GridConnection.counter+=1

        self.import_prices = import_prices.prices_t
        self.export_prices = export_prices.prices_t

        self.p_grid_max = p_grid_max
        self.p_grid_min = p_grid_min

        Optimizer.register_object(self)

    def create_variables(self, model:ConcreteModel):

        p_import = Var(model.t, domain=NonNegativeReals, bounds=(0, self.p_grid_max), initialize=0)
        p_export = Var(model.t, domain=NonNegativeReals, bounds=(0, abs(self.p_grid_min)), initialize=0)
        costs = Var(model.t, domain=Reals, bounds=(0, abs(self.p_grid_min)), initialize=0)

        setattr(model, f"p_import_{self.name}", p_import)
        setattr(model, f"p_export_{self.name}", p_export)
        setattr(model, f"costs_{self.name}", costs)
    
    def create_constraints(self, model:ConcreteModel):

         # Power balance constraints
        model.power_balance_lhs_terms.append(getattr(model, f"p_import_{self.name}"))
        model.power_balance_rhs_terms.append(getattr(model, f"p_export_{self.name}"))

        # Binary formulation to avoid simultan import/export
        if get_config().formulate_binary:
            # Avoid simultaneously import/export with binary variable
            b_export = Var(model.t, domain=Binary, initialize=False)
            setattr(model, f"b_export_{self.name}", b_export)

            def import_limit(model, t):
                return getattr(model, f"p_import_{self.name}")[t] <= abs(self.p_grid_max)*(1-getattr(model, f"b_export_{self.name}")[t])
            def export_limit(model, t):
                return getattr(model, f"p_export_{self.name}")[t] <= abs(self.p_grid_min)*getattr(model, f"b_export_{self.name}")[t]
        else:
            # Avoid simultaneously import/export with export restriction in case of negative import prices
            def import_limit(model, t):
                return getattr(model, f"p_import_{self.name}")[t] <= abs(self.p_grid_max)
            def export_limit(model, t):
                if self.import_prices[t]>=0:
                    return getattr(model, f"p_export_{self.name}")[t] <=abs(self.p_grid_min)
                else:
                    return getattr(model, f"p_export_{self.name}")[t] == 0

        import_constraint = Constraint(
            model.t,
            rule=lambda model, t: import_limit(model, t)
        )
        setattr(model, f"import_constraint_{self.name}", import_constraint)

        export_constraint = Constraint(
            model.t,
            rule=lambda model, t: export_limit(model, t)
        )
        setattr(model, f"export_constraint_{self.name}", export_constraint)

        # Cost Constraint
        def cost_constraint(model, t):
            hour_share = get_config().timestep.seconds / (60*60)
            import_cost = getattr(model, f"p_import_{self.name}")[t] * self.import_prices[t] / 1000 * hour_share
            export_revenue = getattr(model, f"p_export_{self.name}")[t] * self.export_prices[t] / 1000 * hour_share
            return getattr(model, f"costs_{self.name}")[t] == import_cost - export_revenue
        setattr(model, f"cost_const_{self.name}", Constraint(
            model.t,
            rule= lambda model, t: cost_constraint(model, t)
        ))

    def expand_objective(self, model:ConcreteModel):
        time_factor = (get_config().timestep.total_seconds() / 3600)  # Convert timestep to hours


        # /1000 -> €/kWh to €/Wh
        model.obj += sum(
            time_factor*(
                self.import_prices[t]/1000 * getattr(model, f"p_import_{self.name}")[t]
                - self.export_prices[t]/1000 * getattr(model, f"p_export_{self.name}")[t]
            ) for t in model.t
        )
        
        return

    
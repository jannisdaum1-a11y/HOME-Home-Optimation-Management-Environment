import numpy as np
import pandas as pd
import pyomo.environ as pyo

from data_collection.config import get_config
from data_collection.prices import Prices


class Optimizer():
    objects = {}

    def __init__(self, import_prices: Prices = None, export_prices: Prices = None):
        self.import_prices = import_prices
        self.export_prices = export_prices

        self.model = pyo.ConcreteModel()

        self.implementation()
        self.objective_function()
        self.solve()

        self.results_t = None
        self.objective_value = None
        


    @staticmethod
    def register_object(obj):
        Optimizer.objects[obj.name] = obj

    def implementation(self):
        active_config = get_config()
        self.model.t = pyo.Set(initialize=pd.date_range(start=active_config.start_date, end=active_config.end_date - active_config.timestep, freq=active_config.timestep))

        # Variables
        self.model.p_import = pyo.Var(self.model.t, domain=pyo.NonNegativeReals, bounds=(0, active_config.p_grid_max), initialize=0)
        self.model.p_export = pyo.Var(self.model.t, domain=pyo.NonNegativeReals, bounds=(0, abs(active_config.p_grid_min)), initialize=0)

        if True:#get_config().formulate_binary:
            # Avoid simultaneously import/export with binary variable
            self.model.b_export = pyo.Var(self.model.t, domain=pyo.Binary, initialize=False)
            def import_limit(model, t):
                return model.p_import[t] <= abs(active_config.p_grid_max)*(1-model.b_export[t])
            def export_limit(model, t):
                return model.p_export[t] <= abs(active_config.p_grid_min)*model.b_export[t]
        else:
            # Avoid simultaneously import/export with export restriction in case of negative import prices
            def import_limit(model, t):
                return model.p_import[t] <= abs(active_config.p_grid_max)
            def export_limit(model, t):
                if self.import_prices.prices_t[t]>=0:
                    return model.p_export[t] <=abs(active_config.p_grid_min)
                else:
                    return model.p_export[t] == 0
        self.model.import_constraint = pyo.Constraint(
            self.model.t,
            rule=lambda model, t: import_limit(model, t)
        )
        self.model.export_constraint = pyo.Constraint(
            self.model.t,
            rule=lambda model, t: export_limit(model, t)
        )
        

        # Power Balance
        self.model.power_balance_lhs_terms = [self.model.p_import]
        self.model.power_balance_rhs_terms = [self.model.p_export]

        for obj in Optimizer.objects.values():
            obj.create_variables(self.model)
            obj.create_constraints(self.model)


    def objective_function(self):
        if self.import_prices is None or self.export_prices is None:
            raise ValueError("Import and export prices must be provided for the objective function.")


        self.model.power_balance_constraint = pyo.Constraint(
            self.model.t,
            rule=lambda model, t: sum(term[t] for term in model.power_balance_lhs_terms) - sum(term[t] for term in model.power_balance_rhs_terms) == 0,
        )

        time_factor = (get_config().timestep.total_seconds() / 3600)  # Convert timestep to hours
        self.model.obj = pyo.Objective(

            # Objective function: Minimize the total cost of electricity import and export
            # /1000 -> €/kWh to €/Wh
            # TimeFactor considers the interevall-length
            expr=sum(
                time_factor
                *(self.import_prices.prices_t[t]/1000 * self.model.p_import[t]
                - self.export_prices.prices_t[t]/1000 * self.model.p_export[t])
                for t in self.model.t),
            sense=pyo.minimize
        )

    def get_results(self):

        results = {}

        for var in self.model.component_objects(
            pyo.Var,
            active=True
        ):

            results[var.name] = [
                pyo.value(var[t])
                for t in self.model.t
            ]

        results_df = pd.DataFrame(
            results,
            index=self.model.t
        )

        self.results_t = results_df
        self.objective_value = pyo.value(self.model.obj)
        


        return 

    def solve(self):
        solver = pyo.SolverFactory("appsi_highs")
        solver.options["mip_rel_gap"] = 0.02
        solver.options["time_limit"] = 180
        solver.options["threads"] = 0
        solver.options["presolve"] = "on"    # schnell eine gute Lösung finden

        result = solver.solve(
            self.model,
            tee=True
        )

        return result
        
        

        
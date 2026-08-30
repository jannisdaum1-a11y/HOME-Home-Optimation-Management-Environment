import numpy as np
import pandas as pd
import pyomo.environ as pyo

from ..data_collection.config import get_config
from ..data_collection.prices import Prices


class Optimizer():
    objects = {}

    def __init__(self):
        self.model = pyo.ConcreteModel()

        self.implementation()
        self.objective_function()
        self.solve()
        self.getSystemCosts()

        self.results_t = None
        self.objective_value = None
        


    @staticmethod
    def register_object(obj):
        Optimizer.objects[obj.name] = obj

    def implementation(self):
        active_config = get_config()
        self.model.t = pyo.Set(initialize=pd.date_range(start=active_config.start_date, end=active_config.end_date - active_config.timestep, freq=active_config.timestep))

        # Variables
        ## Energy not served
        self.model.ens = pyo.Var(self.model.t, domain=pyo.NonNegativeReals, bounds=(0, np.inf), initialize=0)
        ## Dump Energy
        self.model.dump = pyo.Var(self.model.t, domain=pyo.NonNegativeReals, bounds=(0, np.inf), initialize=0)
        ##

        # Power Balance
        self.model.power_balance_lhs_terms = [self.model.ens] #Positive Power (Generation)
        self.model.power_balance_rhs_terms = [self.model.dump] #Negative Power (Load)

        for obj in Optimizer.objects.values():
            obj.create_variables(self.model)
            obj.create_constraints(self.model)

        # Investment Constraint
        investment_limit = get_config().investment_limit
        if investment_limit:
            self.model.investment_constraint = pyo.Constraint(
                expr= sum(object.get_capex(self.model) for object in Optimizer.objects.values()) <= investment_limit
            )


        return

    def objective_function(self):
       
        self.model.power_balance_constraint = pyo.Constraint(
            self.model.t,
            rule=lambda model, t: sum(term[t] for term in model.power_balance_lhs_terms) - sum(term[t] for term in model.power_balance_rhs_terms) == 0,
        )

        time_factor = (get_config().timestep.total_seconds() / 3600)  # Convert timestep to hours
        ens_cost = get_config().ens_cost
        self.model.obj = pyo.Objective(

            # Objective function: Minimize the total cost of electricity import and export
            # /1000 -> €/kWh to €/Wh
            # TimeFactor considers the interevall-length
            expr=sum(
                time_factor*(
                    (self.model.ens[t]+self.model.dump[t])*ens_cost
                    )
                for t in self.model.t),
            sense=pyo.minimize
        )

        for obj in Optimizer.objects.values():
            obj.expand_objective(self.model)

    def getSystemCosts(self):
        system_costs_t = pd.DataFrame(index=self.model.t)

        initial_discounted_cost = 0.0
        initial_cost = {"total_capex": 0.0}
        for object in Optimizer.objects.values():
            initial_discounted_cost += float(pyo.value(object.get_discounted_capex(self.model)))
            capex = float(pyo.value(object.get_capex(self.model)))
            initial_cost["capex_" + object.name] = capex
            initial_cost["total_capex"] += capex

        total_costs = [
            float(pyo.value(pyo.quicksum(
                getattr(self.model, f"costs_{asset}")[t]
                for asset in Optimizer.objects.keys()
                if hasattr(self.model, f"costs_{asset}")
            )))
            for t in self.model.t
        ]
        system_costs_t["system_costs"] = total_costs
        if not system_costs_t.empty:
            system_costs_t.loc[system_costs_t.index[0], "system_costs"] += initial_discounted_cost
            system_costs_t["system_costs_aggregated"] = system_costs_t["system_costs"].cumsum()
        self.system_costs_t = system_costs_t
        self.capex = pd.DataFrame([initial_cost])
        return system_costs_t

    def get_results(self):

        results = {}
        for component_type in (pyo.Var, pyo.Param):
            for var in self.model.component_objects(
               component_type,
                active=True
            ):
                if var.is_indexed():
                    results[var.name] = [
                        pyo.value(var[t])
                        for t in self.model.t
                    ]
                else:
                    value = pyo.value(var)
                    results[var.name] = [value] * len(self.model.t)

        results_df = pd.DataFrame(
            results,
            index=self.model.t
        )
        self.getSystemCosts()
        results_df = pd.concat([results_df, self.system_costs_t], axis=1)

        self.results_t = results_df
        self.objective_value = pyo.value(self.model.obj)

        return results_df

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
        
        

        
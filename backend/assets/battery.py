import numpy as np
import pandas as pd

from assets.asset import Asset
from optimization.optimizer import Optimizer
from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Binary, Constraint

class Battery(Asset):
    counter = 0
    def __init__(self, capacity, max_charge_rate, max_discharge_rate, initial_rel_soc=0.5, charge_efficiency=1, discharge_efficiency=1, name="Battery"):
        self.name = f"{name}_{Battery.counter}"
        Battery.counter += 1
        self.capacity = capacity
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.initial_rel_soc = initial_rel_soc
        self.soc_profile = pd.Series(dtype=float)
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency  

        Optimizer.register_object(self)

    def create_variables(self, model):
        # Create state of charge variable
        soc = Var(model.t, domain=NonNegativeReals, bounds=(0, self.capacity))
        setattr(model, f"soc_{self.name}", soc)

        # Create charge and discharge power variables
        p_charge = Var(model.t, domain=NonNegativeReals, bounds=(0, self.max_charge_rate))
        p_discharge = Var(model.t, domain=NonNegativeReals, bounds=(0, self.max_discharge_rate))
        b_charge = Var(model.t, domain=Binary)
        setattr(model, f"p_charge_{self.name}", p_charge)
        setattr(model, f"p_discharge_{self.name}", p_discharge)
        setattr(model, f"b_charge_{self.name}", b_charge)

    def create_constraints(self, model):
        # State of charge dynamics
        def state_of_charge(model, t):
            t0 = min(model.t)
            timestep = model.t[2]-model.t[1]
            if t == t0:
                return getattr(model, f"soc_{self.name}")[t] == self.initial_rel_soc * self.capacity
            else:
                return getattr(model, f"soc_{self.name}")[t] == getattr(model, f"soc_{self.name}")[t- timestep ] + self.charge_efficiency * getattr(model, f"p_charge_{self.name}")[t] - getattr(model, f"p_discharge_{self.name}")[t] / self.discharge_efficiency
            
        setattr(
            model,
            f"soc_constraint_{self.name}",
            Constraint(
                model.t,
                rule=lambda model, t: state_of_charge(model, t)
            )
        )
        
        # Power balance constraints
        model.power_balance_lhs_terms.append(getattr(model, f"p_discharge_{self.name}"))
        model.power_balance_rhs_terms.append(getattr(model, f"p_charge_{self.name}"))

        # Charge and discharge cannot happen simultaneously
        def no_bidirectional_use_1(model, t):
            return getattr(model, f"p_charge_{self.name}")[t] <= self.max_charge_rate * getattr(model, f"b_charge_{self.name}")[t]
        setattr(
            model,
            f"one_way_1_{self.name}",
            Constraint(
                model.t,
                rule=lambda model, t: no_bidirectional_use_1(model, t)
            )
        )

        def no_bidirectional_use_2(model, t):
            return getattr(model, f"p_discharge_{self.name}")[t] <= self.max_discharge_rate * (1 - getattr(model, f"b_charge_{self.name}")[t])

        setattr(
            model,
            f"one_way_2_{self.name}",
            Constraint(
                model.t,
                rule=lambda model, t: no_bidirectional_use_2(model, t)
            )
        )

        return
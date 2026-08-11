import numpy as np
import pandas as pd

from assets.asset import Asset
from optimization.optimizer import Optimizer

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
        soc = model.soc = model.Var(model.t, domain=model.NonNegativeReals, bounds=(0, self.capacity))
        setattr(model, f"soc_{self.name}", soc)

        # Create charge and discharge power variables
        p_charge = model.p_charge = model.Var(model.t, domain=model.NonNegativeReals, bounds=(0, self.max_charge_rate))
        p_discharge = model.p_discharge = model.Var(model.t, domain=model.NonNegativeReals, bounds=(0, self.max_discharge_rate))
        b_charge = model.b_charge = model.Var(model.t, domain=model.Binary)
        setattr(model, f"p_charge_{self.name}", p_charge)
        setattr(model, f"p_discharge_{self.name}", p_discharge)
        setattr(model, f"b_charge_{self.name}", b_charge)

    def create_constraints(self, model):
        # State of charge dynamics
        t0 = min(model.t)
        for t in model.t:
            if t == t0:
                # Set initial state of charge
                model.add_constraint(getattr(model, f"soc_{self.name}")[t] == self.initial_rel_soc * self.capacity)
            else:
                # Update state of charge based on charge and discharge
                model.add_constraint(getattr(model, f"soc_{self.name}")[t] == getattr(model, f"soc_{self.name}")[t-1] + self.charge_efficiency * getattr(model, f"p_charge_{self.name}")[t] - getattr(model, f"p_discharge_{self.name}")[t] / self.discharge_efficiency)

        # Power balance constraints
        model.power_balance_lhs_terms.append(getattr(model, f"p_discharge_{self.name}"))
        model.power_balance_rhs_terms.append(getattr(model, f"p_charge_{self.name}"))

        # Charge and discharge cannot happen simultaneously
        for t in model.t:
            model.add_constraint(getattr(model, f"p_charge_{self.name}")[t] <= self.max_charge_rate * getattr(model, f"b_charge_{self.name}")[t])
            model.add_constraint(getattr(model, f"p_discharge_{self.name}")[t] <= self.max_discharge_rate * (1 - getattr(model, f"b_charge_{self.name}")[t]))
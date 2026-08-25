import numpy as np
import pandas as pd

from .asset import Asset
from ..optimization.optimizer import Optimizer
from ..data_collection.config import get_config
from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Binary, Constraint, Param

class Battery(Asset):
    counter = 0
    def __init__(self,
                 capacity=0,
                 max_charge_rate=1000,
                 max_discharge_rate=1000,
                 initial_rel_soc=0.5,
                 charge_efficiency=1,
                 discharge_efficiency=1,
                 name="Battery",
                 spec_capex=1000,
                 lifetime=False,
                 wacc=False,
                 expandable=False,
                 capacity_limit=np.inf
                 ):
        
        self.name = f"{name}_{Battery.counter}"
        Battery.counter += 1
        self.capacity = capacity
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.initial_rel_soc = initial_rel_soc
        self.soc_profile = pd.Series(dtype=float)
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency 

        self.expandable = expandable
        self.capacity_limit = capacity_limit
        self.spec_capex = spec_capex

        super().__init__(expandable,capacity*spec_capex, lifetime, wacc) 

        Optimizer.register_object(self)

    def create_variables(self, model):

        # Create charge and discharge power variables
        p_charge = Var(model.t, domain=NonNegativeReals, bounds=(0, self.max_charge_rate))
        p_discharge = Var(model.t, domain=NonNegativeReals, bounds=(0, self.max_discharge_rate))
        setattr(model, f"p_charge_{self.name}", p_charge)
        setattr(model, f"p_discharge_{self.name}", p_discharge)

        if get_config().formulate_binary:
            b_charge = Var(model.t, domain=Binary)
            setattr(model, f"b_charge_{self.name}", b_charge)

        # Create Capacity variable
        if self.expandable:
            e_capacity = Var(domain=NonNegativeReals, bounds=(0, self.capacity_limit))
        else:
            e_capacity = Param(initialize=self.capacity, mutable=False)
        setattr(model, f"e_capacity_{self.name}", e_capacity)

        # Create state of charge variable
        soc = Var(model.t, domain=NonNegativeReals)
        setattr(model, f"soc_{self.name}", soc)


    def create_constraints(self, model):

        # State of charge dynamics
        def state_of_charge(model, t):
            t0 = min(model.t)
            timestep = model.t[2]-model.t[1]
            time_factor = timestep.total_seconds() / 3600
            if t == t0:
                return getattr(model, f"soc_{self.name}")[t] == self.initial_rel_soc * getattr(model, f"e_capacity_{self.name}")
            else:
                return getattr(model, f"soc_{self.name}")[t] == getattr(model, f"soc_{self.name}")[t- timestep ] + time_factor * (self.charge_efficiency * getattr(model, f"p_charge_{self.name}")[t-timestep] - getattr(model, f"p_discharge_{self.name}")[t-timestep] / self.discharge_efficiency)
            
        setattr(
            model,
            f"soc_constraint_{self.name}",
            Constraint(
                model.t,
                rule=lambda model, t: state_of_charge(model, t)
            )
        )

        def state_of_charge_capacity(model, t):
            return getattr(model, f"soc_{self.name}")[t] <= getattr(
                model, f"e_capacity_{self.name}"
            )

        setattr(
            model,
            f"soc_capacity_constraint_{self.name}",
            Constraint(model.t, rule=state_of_charge_capacity),
        )
        
        # Power balance constraints
        model.power_balance_lhs_terms.append(getattr(model, f"p_discharge_{self.name}"))
        model.power_balance_rhs_terms.append(getattr(model, f"p_charge_{self.name}"))

        # Charge and discharge cannot happen simultaneously
        if get_config().formulate_binary:
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

    def annualized_invest(self, model):
        if self.expandable:
            annuity_factor = self.annuity_factor()
            spec_capex = self.spec_capex
            e_capacity = getattr(model, f"e_capacity_{self.name}")
            return annuity_factor * spec_capex * (e_capacity)
        return 0

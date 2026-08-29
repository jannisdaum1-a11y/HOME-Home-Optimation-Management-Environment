import pandas as pd

from backend.data_collection.config import Config, set_config
from backend.optimization.optimizer import Optimizer


def test_optimizer_includes_system_costs_and_capex_in_results():
    Optimizer.objects = {}
    set_config(
        Config(
            start_date="01.01.2025 00.00",
            end_date="01.01.2025 00.30",
            lat=0,
            lon=0,
            ens_cost=0.3,
            timestep=15,
        )
    )

    optimizer = Optimizer()
    results = optimizer.get_results()

    assert 'system_costs' in results.columns
    assert 'total_capex' in results.columns or 'total_capex' in getattr(optimizer, 'capex', pd.DataFrame()).columns

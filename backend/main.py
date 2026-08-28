from assets.load import ConstantLoadProfile
from pathlib import Path
from assets.pv import PV
from assets.battery import Battery
from data_collection.config import Config, set_config
from data_collection.prices import ConstPrice, SpotMarktPrices
from optimization.optimizer import Optimizer


def run() -> None:
    set_config(
        Config(
            start_date="30.09.2025 22.15",
            end_date="30.06.2026 22.00",
            lat=51.1657,
            lon=10.4515,
        )
    )

    prices = SpotMarktPrices(Path(__file__).resolve().parent.parent / "data" / "spotmarktpreise.csv")
    export_prices = ConstPrice(const_price=0.08)

    PV(rated_power=1000, tilt=30, azimuth=180, temperature_coefficient=-0.005)
    ConstantLoadProfile(constant_load=300)

    Battery(expandable=True, lifetime=25, wacc=0, spec_capex=0.18, capacity=1000, max_charge_rate=1000, max_discharge_rate=1000)

    optimizer = Optimizer(import_prices=prices, export_prices=export_prices)
    results = optimizer.get_results()


if __name__ == "__main__":
    run()

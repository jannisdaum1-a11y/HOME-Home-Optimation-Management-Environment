from assets.pv import PV
from assets.load import ConstantLoadProfile
from data_collection.prices import SpotMarktPrices, ConstPrice
from optimization.optimizer import Optimizer
from data_collection.config import Config, set_config

config = set_config(
    Config(start_date="30.09.2025 22.15", end_date="30.06.2026 22.00", lat=51.1657, lon=10.4515)
)

prices = SpotMarktPrices("data\\spotmarktpreise.csv")
export_prices = ConstPrice(const_price=0.08)  # Example constant export price in €/kWh
start_date = prices.start_date
end_date = prices.end_date
time_delta = prices.timestep_length


pv = PV(rated_power=0, tilt=30, azimuth=180, temperature_coefficient=-0.005)
load = ConstantLoadProfile(constant_load=300)


optimizer = Optimizer(import_prices=prices, export_prices=export_prices)

results = optimizer.get_results()
sum([optimizer.results_t["p_import"][t] * prices.prices_t[t] /4 for t in prices.prices_t.index])
print("hi")
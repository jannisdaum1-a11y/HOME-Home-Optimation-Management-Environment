from assets import *
from assets.pv import PV
from data_collection.prices import SpotMarktPrices
from data_collection.config import Config, set_config


prices = SpotMarktPrices("C:\\Users\\WD2935\\PycharmProjects\\HOME-Home-Optimation-Management-Environment\\data\\spotmarktpreise.csv")
start_date = prices.start_date
end_date = prices.end_date
time_delta = prices.timestep_length

config = set_config(
    Config(start_date=start_date.strftime("%d.%m.%Y"), end_date=end_date.strftime("%d.%m.%Y"), lat=51.1657, lon=10.4515)
)
pv = PV(rated_power=5000, tilt=30, azimuth=180, efficiency=0.15, temperature_coefficient=-0.005)
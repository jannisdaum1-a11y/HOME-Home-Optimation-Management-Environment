import pandas as pd 
import requests

from .config import get_config
from ..data_collection.timeseries import TimeSeries

url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

class Weather():
    def __init__(self, lat=None, lon=None, start_date=None, end_date=None, tilt=0, azimuth=180):
        active_config = get_config()

        self.lat = lat if lat is not None else getattr(active_config, "lat", None)
        self.lon = lon if lon is not None else getattr(active_config, "lon", None)
        self.tilt = tilt
        self.azimuth = azimuth
        self.start_date = start_date if start_date is not None else getattr(active_config, "start_date", None)
        self.end_date = end_date if end_date is not None else getattr(active_config, "end_date", None)
        self.radiation_data = None
        self.temperature_data = None
        self.windspeed = None
        self.cloud_cover = None

    def fetch_weather_data(self):
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "hourly": [
                "temperature_2m",
                "cloud_cover",
                "shortwave_radiation",
                "global_tilted_irradiance"
            ],
            "tilt": self.tilt,
            "azimuth": self.azimuth,
            "timezone": "Europe/Berlin"
        }
        response = requests.get(url, params=params)

        data = response.json()

        try:
            df = pd.DataFrame({
                "time": data["hourly"]["time"],
                "temperature": data["hourly"]["temperature_2m"],
                "cloud": data["hourly"]["cloud_cover"],
                "radiation": data["hourly"]["shortwave_radiation"],
                "specific_radiation": data["hourly"]["global_tilted_irradiance"]
            })
        except Exception as e:
            raise ValueError(
            f"Fehler beim Fetchen der Wetterdaten: {e}, vollständige Antwort {df}"
        ) from e

        df["time"] = pd.to_datetime(df["time"])


        df.set_index("time", inplace=True)

        # Resample to 15-minute intervals and interpolate missing values
        df = df.resample("15min").interpolate()
        return TimeSeries(df).data
    
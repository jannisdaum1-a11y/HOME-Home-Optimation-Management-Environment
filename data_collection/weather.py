import pandas as pd 
import requests

url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
class Weather():
    def __init__(self, lat, lon, start_date=None, end_date=None, tilt=35, azimuth=0):
        self.lat = lat
        self.lon = lon
        self.tilt = tilt
        self.azimuth = azimuth
        self.start_date = start_date
        self.end_date = end_date
        self.radiation_data = None
        self.temperature_data = None
        self.windspeed = None
        self.cloud_cover = None

    def fetch_weather_data(self):
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hourly": [
                "temperature_2m",
                "cloud_cover",
                "shortwave_radiation",
                "global_tilted_irradiance"
                #"wind_speed_10m"
            ],
            "tilt": self.tilt,
            "azimuth": self.azimuth,
            "timezone": "Europe/Berlin"
        }
        response = requests.get(url, params=params)

        data = response.json()

        df = pd.DataFrame({
            "time": data["hourly"]["time"],
            "temperature": data["hourly"]["temperature_2m"],
            "cloud": data["hourly"]["cloud_cover"],
            "radiation": data["hourly"]["shortwave_radiation"],
            "global_tilted_irradiance": data["hourly"]["global_tilted_irradiance"]
        })

        df["time"] = pd.to_datetime(df["time"])


        df.set_index("time", inplace=True)

        # Resample to 15-minute intervals and interpolate missing values
        df = df.resample("15min").interpolate()
        return df
    
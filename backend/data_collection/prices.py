import pandas as pd
from abc import ABC, abstractmethod
from data_collection.config import get_config

base_unit = "€/kWh"
unit_conversion = {
    "€/MWh": 1e3,
    "€/kWh": 1,
    "ct/kWh": 1e2,
}

class Prices(ABC):
    def __init__(self, file_path, separator=',', decimal='.'):
        active_config = get_config()
        self.separator = separator
        self.decimal = decimal
        self.price_file = file_path
        self.start_date = active_config.start_date
        self.end_date = active_config.end_date
        self.n_timesteps = len(pd.date_range(start=self.start_date, end=self.end_date, freq=active_config.timestep))
        self.timestep_length = active_config.timestep
        self.prices_t = self._load_prices()

    
    def _load_prices(self):
        try:
            prices_df = pd.read_csv(self.price_file, sep=self.separator, decimal=self.decimal)
            return self._format_prices(prices_df)
        except FileNotFoundError:
            print(f"File not found: {self.price_file}")
            return None
        except pd.errors.EmptyDataError:
            print(f"No data: {self.price_file} is empty")
            return None
        except pd.errors.ParserError:
            print(f"Parsing error: {self.price_file} is malformed")
            return None

    def _convert_units(self, prices_df: pd.DataFrame, from_unit: str, to_unit: str) -> pd.DataFrame:
        if from_unit not in unit_conversion or to_unit not in unit_conversion:
            raise ValueError(f"Unsupported unit conversion from {from_unit} to {to_unit}")

        conversion_factor = unit_conversion[to_unit] / unit_conversion[from_unit]
        # Support both DataFrames and Series without modifying the input.
        return prices_df * conversion_factor

    @abstractmethod
    def _format_prices(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        """
        Abstract method to format the prices DataFrame.
        cols: from (pd.datetime), to (pd.datetime), price (float [€/kwh]"""
        return prices_df.loc[prices_df['from'] >= self.start_date].loc[prices_df['to'] <= self.end_date]


class SpotMarktPrices(Prices):
    def __init__(self, file_path):
        super().__init__(file_path, separator=';', decimal=',')

    def _format_prices(self, prices_df: pd.DataFrame) -> pd.DataFrame:

        prices_df.index = pd.to_datetime(
            prices_df["Datum"]+" "+prices_df["von"],
            format="%d.%m.%Y %H:%M",
            dayfirst=True
        )

        timestamps = pd.date_range(
                    start=self.start_date,
                    end=self.end_date- self.timestep_length,
                    freq=self.timestep_length
                )

        prices = prices_df["Spotmarktpreis in ct/kWh"][timestamps].rename("prices")
        prices = self._convert_units(prices, from_unit="ct/kWh", to_unit="€/kWh")

        return prices

class ConstPrice(Prices):
    def __init__(self, const_price):
        self.const_price = const_price
        super().__init__(file_path=None)
        

    def _load_prices(self):
        # Create a DataFrame with a single row for the constant price
        prices_t = pd.DataFrame(
            index=pd.date_range(start=self.start_date, end=self.end_date - self.timestep_length, freq=self.timestep_length),
            data= [self.const_price] * len(pd.date_range(start=self.start_date, end=self.end_date - self.timestep_length, freq=self.timestep_length))
            ).rename(columns={0: "prices"})
        return prices_t["prices"]

    def _format_prices(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        # For constant price, we don't need to format anything, just return the DataFrame as is
        return prices_df
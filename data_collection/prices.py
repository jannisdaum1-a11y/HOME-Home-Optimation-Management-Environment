import pandas as pd
from abc import ABC, abstractmethod

base_unit = "€/kWh"
unit_conversion = {
    "€/MWh": 1e3,
    "€/kWh": 1,
    "ct/kWh": 1e2
}

class Prices(ABC):
    def __init__(self, file_path, separator=',', decimal='.'):
        self.separator = separator
        self.decimal = decimal
        self.price_file = file_path
        self.prices_t = self._load_prices()
        self.start_date = self.prices_t['from'].min()
        self.end_date = self.prices_t['to'].max()
        self.n_timesteps = len(self.prices_t)
        self.timestep_length = (self.end_date - self.start_date) / self.n_timesteps

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
        # Support both DataFrame with a 'price' column and a Series of prices
        prices_df *= conversion_factor
        return prices_df

    @abstractmethod
    def _format_prices(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        """
        Abstract method to format the prices DataFrame.
        cols: from (pd.datetime), to (pd.datetime), price (float [€/kwh]"""
        return prices_df


class SpotMarktPrices(Prices):
    def __init__(self, file_path):
        super().__init__(file_path, separator=';', decimal=',')

    def _format_prices(self, prices_df: pd.DataFrame) -> pd.DataFrame:

        dates = pd.to_datetime(prices_df['Datum'], format='%d.%m.%Y')
        from_times = pd.to_datetime(prices_df['von'], format='%H:%M').dt.time
        to_times = pd.to_datetime(prices_df['bis'], format='%H:%M').dt.time
        prices = prices_df['Spotmarktpreis in ct/kWh'].values.astype(float)
        prices = self._convert_units(prices, from_unit="ct/kWh", to_unit=base_unit)
        prices_t = pd.DataFrame({
            'from': [pd.Timestamp.combine(date, from_time) for date, from_time in zip(dates, from_times)],
            'to': [pd.Timestamp.combine(date, to_time) for date, to_time in zip(dates, to_times)],
            'price': prices
        })
        return prices_t

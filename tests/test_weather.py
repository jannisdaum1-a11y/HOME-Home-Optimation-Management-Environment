import sys
import os
import pytest

from data_collection.weather import Weather

# Ensure the project root is on sys.path so imports resolve during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collection.prices import SpotMarktPrices

@pytest.mark.parametrize("start_date, end_date, lat, lon", [
    ("2025-06-01", "2026-08-06", 50.7753, 6.0839)  # Example coordinates for Cologne, Germany
])
def test_weather(start_date, end_date, lat, lon):
    weather = Weather(lat, lon, start_date, end_date)
    df = weather.fetch_weather_data()
    assert df is not None
    assert 'temperature' in df.columns
    assert 'cloud' in df.columns
    assert 'radiation' in df.columns
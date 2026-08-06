import pytest

from data_collection.prices import SpotMarktPrices


def test_spotmarktprices_conversion(tmp_path):
	csv = tmp_path / "prices.csv"
	csv.write_text("Datum,von,bis,Spotmarktpreis in ct/kWh\n01.01.2026,00:00,01:00,10\n")
	sm = SpotMarktPrices(str(csv))
	df = sm._load_prices()
	assert df is not None
	assert list(df.columns) == ['from', 'to', 'price']
	assert df.iloc[0]['price'] == pytest.approx(0.1)
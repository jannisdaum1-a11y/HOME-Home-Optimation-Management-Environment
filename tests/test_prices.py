import sys
import os
import pytest

# Ensure the project root is on sys.path so imports resolve during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collection.prices import SpotMarktPrices

@pytest.mark.parametrize("filepath", [
    "data/spotmarktpreise.csv"
])
def test_spotmarktprices_conversion(filepath):
    sm = SpotMarktPrices(filepath)
    assert sm.prices_t is not None
    assert list(sm.prices_t.columns) == ['from', 'to', 'price']

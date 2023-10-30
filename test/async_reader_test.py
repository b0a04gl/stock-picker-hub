import pytest
import csv
from datetime import datetime, timedelta
import redis
import pickle

from async_reader import read_symbols, download_stock_data, calculate_bollinger_bands, calculate_technical_indicators, \
    store_dataframe_in_redis, get_stock_data


@pytest.fixture
def example_symbols_file(tmp_path):
    symbols_file = tmp_path / "example_symbols.csv"
    with open(symbols_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["AAPL", "MSFT", "GOOGL"])
    return symbols_file


@pytest.fixture
def example_stock_data(example_symbols_file):
    symbols = read_symbols(example_symbols_file)
    stock_data = download_stock_data(symbols)
    return stock_data


@pytest.fixture
def example_stock_data_with_indicators(example_stock_data):
    calculate_bollinger_bands(example_stock_data)
    calculate_technical_indicators(example_stock_data)
    return example_stock_data


def test_read_symbols(example_symbols_file):
    symbols = read_symbols(example_symbols_file)
    assert symbols == ["AAPL", "MSFT", "GOOGL"]


def test_download_stock_data():
    symbols = ["AAPL", "MSFT"]
    stock_data = download_stock_data(symbols)
    assert not stock_data.empty


def test_calculate_bollinger_bands(example_stock_data):
    calculate_bollinger_bands(example_stock_data)
    assert 'bb_low' in example_stock_data.columns
    assert 'bb_mid' in example_stock_data.columns
    assert 'bb_high' in example_stock_data.columns




def test_store_dataframe_in_redis(example_stock_data):
    store_dataframe_in_redis(example_stock_data)
    r = redis.Redis(host='localhost', port=6379, db=0)
    data_serialized = r.get('past_week_stock_data')
    data = pickle.loads(data_serialized)
    assert data.equals(example_stock_data)



if __name__ == '__main__':
    pytest.main()

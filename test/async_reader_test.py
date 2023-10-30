import csv
import pickle
from unittest.mock import patch, Mock

import pytest
import redis

from async_reader import read_symbols, download_stock_data, calculate_bollinger_bands, calculate_technical_indicators, \
    store_dataframe_in_redis


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


@pytest.fixture
def mock_redis():
    mock_redis = Mock(spec=redis.StrictRedis)

    with patch('async_reader.redis.Redis', return_value=mock_redis):
        yield mock_redis


def test_store_dataframe_in_redis(example_stock_data, mock_redis):
    store_dataframe_in_redis(example_stock_data)

    mock_redis.set.assert_called_with('past_week_stock_data', pickle.dumps(example_stock_data))

    data_serialized = pickle.dumps(example_stock_data)
    mock_redis.get.return_value = data_serialized
    data = pickle.loads(mock_redis.get('past_week_stock_data'))

    assert data.equals(example_stock_data)


if __name__ == '__main__':
    pytest.main()

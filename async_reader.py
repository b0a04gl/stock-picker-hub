import csv
import pickle
from datetime import datetime, timedelta

import numpy as np
import pandas_ta
import redis
import yfinance as yf


def read_symbols(filename):
    symbols = []
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            symbols = [item for item in row]
    return symbols


def download_stock_data(symbols):
    current_date = datetime.now()
    start_date = current_date - timedelta(days=7)
    end_date = current_date

    df = yf.download(tickers=symbols, start=start_date, end=end_date).stack()
    df.index.names = ['date', 'ticker']
    df.columns = df.columns.str.lower()
    df['close'] = df['close'].fillna(method='ffill')
    return df


def calculate_bollinger_bands(df):
    df['bb_low'] = df.groupby(level=1)['adj close'].transform(
        (lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0] if pandas_ta.bbands(close=np.log1p(x),
                                                                                                 length=20) is not None else 0)
    )

    df['bb_mid'] = df.groupby(level=1)['adj close'].transform(
        (lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0] if pandas_ta.bbands(close=np.log1p(x),
                                                                                                 length=20) is not None else 0))

    df['bb_high'] = df.groupby(level=1)['adj close'].transform(
        (lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0] if pandas_ta.bbands(close=np.log1p(x),
                                                                                                 length=20) is not None else 0))


def calculate_technical_indicators(df):
    df.ta.ema(length=12, append=True)
    df.ta.ema(length=26, append=True)
    df['macd'] = df['EMA_12'] - df['EMA_26']
    df.ta.ema(length=9, append=True, col='macd_signal')
    df['dollar_volume'] = (df['adj close'] * df['volume']) / 1e6
    df.ta.ema(length=200, append=True)
    df['rsi'] = df.groupby(level=1)['adj close'].transform(lambda x: pandas_ta.rsi(x, length=20))
    print("calc rsi")
    print(df['rsi'])


def store_dataframe_in_redis(df):
    r = redis.Redis(host='localhost', port=6379, db=0)
    data_serialized = pickle.dumps(df)
    r.set('past_week_stock_data', data_serialized)


def get_stock_data():
    symbols = read_symbols("symbols.csv")
    stock_data = download_stock_data(symbols)
    # print("before bb")
    calculate_bollinger_bands(stock_data)
    # print("after bb")
    calculate_technical_indicators(stock_data)
    store_dataframe_in_redis(stock_data)
    return stock_data

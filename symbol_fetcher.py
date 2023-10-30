import csv
import pandas as pd


def write_symbols():
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

    sp500['Symbol'] = sp500['Symbol'].str.replace('.', '-')

    symbols_list = sp500['Symbol'].unique().tolist()

    with open('symbols.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(symbols_list)


if __name__ == '__main__':
    write_symbols()

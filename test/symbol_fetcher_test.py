import unittest
import os

import pytest

from symbol_fetcher import write_symbols


class TestWriteSymbols(unittest.TestCase):
    def setUp(self):
        self.filename = 'symbols.csv'

    def test_write_symbols(self):
        write_symbols()
        self.assertTrue(os.path.exists(self.filename))
        with open(self.filename, 'r') as file:
            symbols = file.read()
        self.assertTrue(len(symbols) > 0)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)


if __name__ == '__main__':
    pytest.main()

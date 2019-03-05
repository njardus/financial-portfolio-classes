from loguru import logger
from stock import OpenPosition, ClosedPosition, Stock


class StockList:

    def __init__(self):
        self.stocklist = []
        self.number_of_entries = 0

    def is_in_list(self, ticker):
        for pos in self.stocklist:
            if pos.ticker == ticker:
                return True
            else:
                return False

    def remove(self, ticker):
        if self.is_in_list(ticker):
            for pos in self.stocklist:
                if pos.ticker == ticker:
                    del pos
                    self.number_of_entries -= 1


class Watchlist(StockList):

    def __init__(self, ticker):
        StockList.__init__()

    def add(self, ticker):
        if not self.is_in_list(ticker):
            self.stocklist.append(Stock(ticker))
            self.number_of_entries += 1


class OpenList(StockList):

    def __init__(self):
        StockList.__init__()

    def add(self, ticker, number_of_shares, entry_date, entry_price):
        if not self.is_in_list(ticker):
            self.stocklist.append(OpenPosition(ticker, number_of_shares, entry_date, entry_price))
            self.number_of_entries += 1


class ClosedList(StockList):

    def __init__(self):
        self.closed_list = []

    def add(self, position, closing_date, closing_price):
        if not self.is_in_list(ticker):
            self.stocklist.append(ClosedPosition(position, closing_date, closing_price))
            self.number_of_entries += 1
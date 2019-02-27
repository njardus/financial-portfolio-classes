from datetime import datetime
from loguru import logger
from share import Share


class Stock(Share):

    def __init__(self, ticker):
        Share.__init__(self, ticker)

    def sma(self, period):
        # Todo: Implement
        # Note share.history.head():
        # 2000-01-04
        # 2000-01-05
        # 2000-01-06
        # 2000-01-07
        # 2000-01-10

        # Previous implimentation:
        # colname = "SMA" + str(period)
        # newcol = self.history['Close'].rolling(period).mean()
        # self.history[colname] = newcol

        # for index in self.history:
        #     print(row['4. Close'])
        pass


class OpenPosition(Stock):

    def __init__(self, ticker, number_of_shares, entry_date, entry_price):
        Stock.__init__(self, ticker)
        self.shares = number_of_shares
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.entry_value = self.entry_price * self.shares
        self.current_value = self.entry_value
        self.days_in_trade = self.get_days_in_trade()
        self.pct = self.get_pct()
        self.annualised_pct = self.get_annualised_pct()
        self.target_profit_price = self.get_target_profit_price()
        self.target_loss_price = self.get_target_loss_price()

    def get_current_value(self):
        self.update()
        self.current_value = self.current_price * self.shares
        return self.current_value

    def get_pct(self):
        self.pct = (self.current_price - self.entry_price) / self.entry_price
        return self.pct

    def get_days_in_trade(self):
        self.days_in_trade = (datetime.today() - self.entry_date).days
        return self.days_in_trade

    def get_annualised_pct(self):
        # [(1 + pct) ^ (365 / days_in_trade)] - 1
        pct = self.get_pct()
        days = self.get_days_in_trade()

        growth = 1 + pct
        days_ratio = 365 / days

        self.annualised_pct = (growth ** days_ratio) - 1
        return self.annualised_pct

    def get_target_profit_price(self):
        # ANN = (1+pct ** days_ratio) - 1
        # ANN + 1 = (1+pct ** days_ratio)
        # (ANN + 1) ** (1/days_ratio) = 1 + pct
        # [(ANN + 1) ** (1 / days_ratio)] - 1 = pct

        # Magic number!
        ann = 0.5 + 1
        days_ratio = self.get_days_in_trade() / 365
        pct = (ann ** days_ratio) - 1
        self.target_profit_price = self.entry_price * (1 + pct)

        return self.target_profit_price

    def get_target_loss_price(self):
        # Magic number!
        ann = -0.5 + 1
        days_ratio = self.get_days_in_trade() / 365
        pct = (ann ** days_ratio) - 1
        self.target_profit_price = self.entry_price * (1 + pct)

        return self.target_profit_price

    def get_change(self):
        return self.current_value - self.entry_value

    def get_summary(self):
        logger.info(f"+-------Open Position--------+")
        logger.info(f"|----------------------------|")
        logger.info(f"|  {self.ticker}                    |")
        logger.info(f"|  {self.shares:.4f} shares            |")
        logger.info(f"|----------------------------|")
        logger.info(f"| Purchased on {self.entry_date.date()}    |")
        logger.info(f"| at {self.entry_price}                    |")
        logger.info(f"| for R{self.entry_value/100:.2f}.              |")
        logger.info(f"|----------------------------|")
        logger.info(f"| That's a {100*self.pct:.2f}% change     |")
        logger.info(f"| over {self.days_in_trade} days               |")
        logger.info(f"| That's {100*self.annualised_pct:.2f}% annualised. |")
        logger.info(f"|----------------------------|")

        return [self.pct, self.days_in_trade, self.annualised_pct]


class ClosedPosition(OpenPosition):

    def __init__(self, open_position, close_date, close_price):
        self.ticker = open_position.ticker
        self.shares = open_position.shares

        self.entry_price = open_position.entry_price
        self.entry_date = open_position.entry_date

        # Set closing data
        self.close_date = close_date
        self.close_price = close_price

        self.entry_value = self.entry_price * self.shares
        self.close_value = self.close_price * self.shares

        self.pct = self.get_pct()
        self.days_in_trade = self.get_days_in_trade()
        self.annualised_pct = self.get_annualised_pct()

    def get_pct(self):
        self.pct = (self.close_price - self.entry_price) / self.entry_price
        return self.pct

    def get_days_in_trade(self):
        self.days_in_trade = (self.close_date - self.entry_date).days
        return self.days_in_trade

    def get_annualised_pct(self):
        # [(1 + pct) ^ (365 / days_in_trade)] - 1
        pct = self.get_pct()
        days = self.get_days_in_trade()

        growth = 1 + pct
        days_ratio = 365 / days

        self.annualised_pct = (growth ** days_ratio) - 1
        return self.annualised_pct

    def get_summary(self):
        logger.info(f"+------Closed Position-------+")
        logger.info(f"|----------------------------|")
        logger.info(f"|  {self.ticker}                    |")
        logger.info(f"|  {self.shares:.4f} shares            |")
        logger.info(f"|----------------------------|")
        logger.info(f"| Purchased on {self.entry_date.date()}    |")
        logger.info(f"| at {self.entry_price}                    |")
        logger.info(f"| for R{self.entry_value/100:.2f}.              |")
        logger.info(f"|----------------------------|")
        logger.info(f"| Purchased on {self.close_date.date()}    |")
        logger.info(f"| at {self.close_price}                    |")
        logger.info(f"| for R{self.close_value/100:.2f}.              |")
        logger.info(f"|----------------------------|")
        logger.info(f"| That's a {100*self.pct:.2f}% change     |")
        logger.info(f"| over {self.days_in_trade} days               |")
        logger.info(f"| That's {100*self.annualised_pct:.2f}% annualised. |")
        logger.info(f"|----------------------------|")

        return [self.pct, self.days_in_trade, self.annualised_pct]


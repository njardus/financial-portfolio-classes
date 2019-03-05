from datetime import datetime
from loguru import logger
from share import Share


class Stock(Share):

    def __init__(self, ticker):
        Share.__init__(self, ticker)

    def sma(self, period):
        colname = "SMA" + str(period)
        newcol = self.history['Close'].rolling(period).mean()
        self.history[colname] = newcol

        return self.history[colname].iloc[-1]


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

        if days == 0:
            return 0

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

    def get_sell_signal(self):
        # Todo: Flesh out market signals. Maybe throw it into a separate file? That'll help with getting portfolio
        # info in..

        sig = False

        if (self.get_annualised_pct() >= 0.5) and (self.get_days_in_trade() >= 7) and (self.get_pct() >= 0.104):
            sig = True

        if (self.get_annualised_pct() <= -0.5) and (self.get_days_in_trade() >= 62) and (self.current_value < 41067):
            sig = True

        return sig


class ClosedPosition(OpenPosition):

    def __init__(self, open_position, close_date, close_price):
        self.ticker = open_position.ticker
        self.shares = open_position.shares
        self.history = open_position.history
        self.last_updated = open_position.last_updated

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


class WatchStock(Stock):

    def __init__(self, ticker):
        super().__init__(ticker)

    def worth_a_look(self):
        # SMA 15 should be larger than SMA 50, indicating growth:
        # SMA 50 should be larger than SMA 200, indicating a support:
        # Current price should be above SMA 200, indicating a support:
        # Current price should be within a couple of % of SMA15:
        # 1 Year growth should be within range of the winning average:

        # Magic numbers!
        if (self.sma(15) > self.sma(50)) and (self.sma(50) > self.sma(200)) and (self.current_price > self.sma(200)):
            # TODO: implement 1 year growth
            # TODO: implement portfolio winning average
            logger.info(f"Look at buying {self.ticker} - the moving averages line up!")

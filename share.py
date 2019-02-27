from datetime import datetime
from loguru import logger
from alpha_vantage.timeseries import TimeSeries
import pickle
from os import path

# TODO: Set up magic numbers in settings file.
# Magic numbers:
max_retries = 15
update_interval = 60 * 60
key = KEY
error_margin = 0.7


class Share:

    def __init__(self, ticker):
        logger.info(f"Create share class: {ticker}.")
        self.ticker = ticker
        self.filename = ".\\data\\" + self.ticker + ".shr"
        self.last_updated = datetime(1970, 1, 1)
        self.history = []
        self.current_price = 0

        if path.isfile(self.filename):
            self.load_file()
        else:
            pass
        self.update()

    def save_file(self, data):
        outfile = open(self.filename, 'wb')
        pickle.dump(data, outfile)
        outfile.close()

    def load_file(self):
        infile = open(self.filename, 'rb')
        self.history = pickle.load(infile)
        infile.close()

    def update(self):
        logger.info(f"Grabbing history for {self.ticker}.")

        grabbed = False
        retries = 0
        data = None

        if self.time_since_last_update() > update_interval:
            while (grabbed is False) and (retries < max_retries):
                try:
                    ts = TimeSeries(key=key, output_format='pandas', indexing_type='date')
                    data, meta_data = ts.get_daily(self.ticker, outputsize='full')

                    data = self.clean_close_data(data)
                    data = self.fix_history(data)
                    self.save_file(data)

                    self.current_price = data.iloc[-1]['Close']

                    self.last_updated = datetime.now()
                    grabbed = True
                except KeyError:
                    retries += 1

        if data is None:
            self.load_file()
            return False
        else:
            self.history = data
            return True

    def time_since_last_update(self):
        now = datetime.now()
        then = self.last_updated

        return (now - then).total_seconds()

    @staticmethod
    def clean_close_data(data):
        """Function to clean closing from Alpha Vantage. The headers from Alpha Vantage are a bit odd, so this will just
        rename them to:
           |--Date--|--Open--|--High--|--Low--|--Close--|--Volume--|
        Input argument is the dataframe."""

        data.index.names = ['Date']
        try:
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        except ValueError:
            logger.error("ValueError in renaming the data columns. "
                         "Current data info is:"
                         ""
                         + data.info() +
                         ""
                         "Current data head is: " + data.head()
                         )

        return data

    def fix_history(self, data):
        """Step 1: Copy data to a new dataframe
        Step 2: Ensure the new data has an integer index
        Step 3: Step through the dataframe in reverse
        Step 3a: If the closing price is about 100 times smaller than the following day's (previous index's), multiply
                 the Open, High, Low, Close columns by 100.
        Step 4: Return the *new* dataframe."""

        # Step 1: Copy data to a new dataframe
        new_data = data.copy()
        # Step 2: Ensure the new data has an integer index.
        new_data = new_data.reset_index()

        loopindex = 0
        # Step 3: Step through the dataframe in reverse
        for idx in reversed(new_data.index):
            # logger.debug(f"idx in each iter: {idx}")

            # Step 3a: If the closing price is about 100 times smaller than the following day's (previous index's),
            #          multiply to Open, High, Low, Close columns by 100.
            if loopindex == 0:
                # Handle the special case
                loopindex += 1
            elif idx == 0:
                pass
            else:
                loopindex += 1
                today_close = new_data.loc[idx, 'Close']
                tomorrow_close = new_data.loc[idx - 1, 'Close']

                if tomorrow_close == 0:
                    new_data.loc[idx - 1, 'Open'] = new_data.loc[idx, 'Open']
                    new_data.loc[idx - 1, 'High'] = new_data.loc[idx, 'High']
                    new_data.loc[idx - 1, 'Low'] = new_data.loc[idx, 'Low']
                    new_data.loc[idx - 1, 'Close'] = new_data.loc[idx, 'Close']
                    tomorrow_close = new_data.loc[idx - 1, 'Close']

                if self.is_approximate_factor(today_close, tomorrow_close, 100, error_margin):
                    new_data.loc[idx, 'Open'] = data.loc[idx, 'Open'] * 100
                    new_data.loc[idx, 'High'] = data.loc[idx, 'High'] * 100
                    new_data.loc[idx, 'Low'] = data.loc[idx, 'Low'] * 100
                    new_data.loc[idx, 'Close'] = data.loc[idx, 'Close'] * 100
                elif today_close == 0:
                    # Special case: today_close == 0
                    new_data.loc[idx, 'Open'] = new_data.loc[idx + 1, 'Open']
                    new_data.loc[idx, 'High'] = new_data.loc[idx + 1, 'High']
                    new_data.loc[idx, 'Low'] = new_data.loc[idx + 1, 'Low']
                    new_data.loc[idx, 'Close'] = new_data.loc[idx + 1, 'Close']

        return new_data

    @staticmethod
    def is_approximate_factor(num1, num2, factor, margin):
        """is_approximate_factor tests if num1*factor is close to num2, within an error margin.
        This is useful in cleaning up financial data where data was saved as the major currency denominator
        (eg. dollars) at some point, and then suddenly as the minor denominator (eg. cents), or vice versa.
        Input arguments:
        num1: The smaller number.
        num2: The larger number.
        factor: The multiplication factor that should be tested.
        margin: The allowed margin of error, in percent of (num1 * factor).
        Example:
            If we want to see if the number 1 is approximately 100 times smaller than the number 99.8, the function
            would be called as:
            result = is_approximate_factor(1, 99.8, 100, 0.5)
            and would return true.
            result = is_approximate_factor(1, 99.4, 100, 0.5)
            would return false, as  (1 * 100) * (100-0.5) > 99.4
        """
        compare_num = num1 * factor

        pct_diff = abs((compare_num - num2) / num2)

        if pct_diff < margin:
            return True
        else:
            return False

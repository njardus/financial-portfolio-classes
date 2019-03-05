from datetime import datetime
from pandas import DataFrame as df
from loguru import logger

from portfolio import Watchlist
from stock import Stock, OpenPosition, ClosedPosition
from positionhistory import *
import comms

# Test NPN for purchase:
# npn = Watchlist("NPN.JO")
# npn.worth_a_look()




# Todo: Implement email with summary
comms.mail_summary(list_of_open_positions)
# comms.mail_summary(list_of_closed_positions)

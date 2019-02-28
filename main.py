from datetime import datetime
from pandas import DataFrame as df
from loguru import logger

from stock import OpenPosition
from stock import ClosedPosition
import comms

list_of_positions = []
list_of_positions.append(OpenPosition('TBS.JO', 1.2634, datetime(2018, 4, 18), 39329))
list_of_positions.append(OpenPosition('DSY.JO', 5.0898, datetime(2018, 9, 20), 17423))
list_of_positions.append(OpenPosition('CLS.JO', 4.7944, datetime(2018, 9, 20), 18444))
list_of_positions.append(OpenPosition('AVI.JO', 11.7908, datetime(2018, 10, 1), 10589))
list_of_positions.append(OpenPosition('CLS.JO', 0.0005, datetime(2018, 10, 1), 18214))
list_of_positions.append(OpenPosition('AFX.JO', 45.7421, datetime(2018, 11, 5), 2905))
list_of_positions.append(OpenPosition('SNT.JO', 4.5562, datetime(2018, 11, 16), 30381))
list_of_positions.append(OpenPosition('FSR.JO', 12.3695, datetime(2018, 11, 19), 6947))
list_of_positions.append(OpenPosition('MNK.JO', 11.3997, datetime(2018, 11, 26), 8773))
list_of_positions.append(OpenPosition('CLS.JO', 1.6072, datetime(2019, 1, 14), 19390))
list_of_positions.append(OpenPosition('SPP.JO', 7.8525, datetime(2019, 1, 16), 20896))
list_of_positions.append(OpenPosition('PSG.JO', 6.5549, datetime(2019, 1, 30), 24494))
list_of_positions.append(OpenPosition('EXX.JO', 12.9008, datetime(2019, 2, 1), 15451))
list_of_positions.append(OpenPosition('MTH.JO', 11.3255, datetime(2019, 2, 1), 8800))
list_of_positions.append(OpenPosition('PSG.JO', 2.056, datetime(2019, 2, 13), 25019))
list_of_positions.append(OpenPosition('SNT.JO', 2.6054, datetime(2019, 2, 13), 30128))
list_of_positions.append(OpenPosition('TKG.JO', 39.9735, datetime(2019, 2, 21), 6794))

# Todo: Implement email with summary
comms.mail_summary(list_of_positions)
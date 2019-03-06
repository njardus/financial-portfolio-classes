from positionhistory import *
import comms

# Todo: Up the rate of update to once every 10 minutes, and implement better filtering logic in the comms package so that we only mail an update once an hour or if action is required.

# Todo: Implement email with summary
comms.send_summary(list_of_open_positions)
# comms.send_summary(list_of_closed_positions)

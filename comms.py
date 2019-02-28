from datetime import datetime
from loguru import logger


def mail_summary(positions):
    total_value = 0
    index = 0

    today = datetime.today().strftime("%Y-%m-%d")

    subject = "Portfolio summary - " + today
    message_start = "\nPortfolio summary on " + today + ". \n" \
                      "------------------------------------\n"
    message_sell_sig = ""

    message_total_value = "Total portfolio value: R"

    for pos in positions:
        if pos.get_sell_signal():
            message_sell_sig += f"Look at selling: {pos.ticker}.\n" \
                                f"  Annualised pct: {100*pos.annualised_pct:.2f}%\n" \
                                f"  Pct:            {100*pos.pct:.2f}%\n" \
                                f"  Days open:      {pos.days_in_trade}\n" \
                                 "------------------------------------\n"

            logger.critical("\n" + message_sell_sig)

        total_value += pos.get_current_value() / 100

        index += 1

    message_total_value += f"{total_value:.2f}."

    logger.info(message_total_value)

    message = message_start + message_sell_sig + message_total_value

    logger.debug(message)
    # gmailmessage(address, subject, message)

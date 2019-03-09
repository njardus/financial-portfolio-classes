import config
import settings

from datetime import datetime
from loguru import logger
from twilio.rest import Client


def send_summary(positions):
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

    total_value += 44788/100 # TEMP to add the MCG that is not being pulled from Alpha Vantage right now

    message_total_value += f"{total_value:.2f}."

    message = message_start + message_sell_sig + message_total_value

    if config.errorlevel >= 0:
        message += "\n\n Please note that an error occurred while processing the portfolio."

    logger.debug(message)

    if settings.send_whatsapp():
        send_whatsapp(message)

    # TODO:
    # if settings.send_email():
    #     send_email(message)


def send_whatsapp(message):
    logger.debug("Attempting Whatsapp")

    tonumber = 'whatsapp:' + settings.whatsapp_number()
    logger.debug(tonumber)

    client = Client(settings.whatsapp_account_sid(), settings.whatsapp_auth_token())

    message = client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',
        to=tonumber
    )

    logger.info(f"Whatsapp sent: {message.sid} to {tonumber}.")
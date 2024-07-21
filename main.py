import json
import random
import time
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable

from waveshare_epd import epd2in13b_V4
epd = epd2in13b_V4.EPD()

import signal

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

data_sink = Observable()

def get_dummy_data():
    logger.info('Generating dummy data')


def fetch_prices():
    logger.info('Fetching prices')
    timeslot_end = datetime.now(timezone.utc)
    end_date = timeslot_end.strftime(DATETIME_FORMAT)
    start_data = (timeslot_end - timedelta(days=DATA_SLICE_DAYS)).strftime(DATETIME_FORMAT)
    url = f'https://api.exchange.coinbase.com/products/{config.currency}/candles?granularity=900&start={urllib.parse.quote_plus(start_data)}&end={urllib.parse.quote_plus(end_date)}'
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    external_data = json.loads(response.text)
    prices = [entry[1:5] for entry in external_data[::-1]]
    return prices


def exit_gracefully():
        logger.info('Exit')
        data_sink.close()
        logger.info("Clear...")
        epd.init()
        epd.clear()
        logger.info("Goto Sleep...")
        epd.sleep()
        exit()


def handler_stop_signals(signum, frame):
    exit_gracefully()


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


def main():
    logger.info('Initialize')

    builder = Builder(config)
    builder.bind(data_sink)

    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices)
                time.sleep(config.refresh_interval)
            except (HTTPError, URLError) as e:
                logger.error(str(e))
                time.sleep(5)
    except IOError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        exit_gracefully()


if __name__ == "__main__":
    main()

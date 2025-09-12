import logging
import time
#
from prometheus_client import start_http_server
#
from config import LOG_LEVEL, METRICS_PORT, METRICS_UPDATE_FREQUENCY, NUMERAI_PUBLIC_ID, NUMERAI_SECRET
from lib.metrics.general import GeneralMetrics
from lib.metrics.signals import SignalsMetrics
from lib.signal_handling import setup_signal_handling

logging.basicConfig(level=LOG_LEVEL)
setup_signal_handling()


def main():
    logging.info('Starting Numerai exporter...')
    start_http_server(METRICS_PORT)

    general_metrics = GeneralMetrics(NUMERAI_PUBLIC_ID, NUMERAI_SECRET)
    signals_metrics = SignalsMetrics(NUMERAI_PUBLIC_ID, NUMERAI_SECRET)

    while True:
        try:
            general_metrics.set_metrics()
            signals_metrics.set_metrics()
        except Exception as e:
            logging.exception(e)

        time.sleep(METRICS_UPDATE_FREQUENCY)


if __name__ == '__main__':
    main()

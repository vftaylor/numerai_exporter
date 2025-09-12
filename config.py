import logging
import os


LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
METRICS_PORT = int(os.getenv('METRICS_PORT', 8000))
METRICS_UPDATE_FREQUENCY = int(os.getenv('METRICS_UPDATE_FREQUENCY', 60))
NUMERAI_PUBLIC_ID = os.getenv('NUMERAI_PUBLIC_ID')
NUMERAI_SECRET = os.getenv('NUMERAI_SECRET')
RELEVANT_PERIODS = [1, 2, 3, 4, 5, 10, 20, 40, 60, 120, 250, -1]  # in days. -1 means all

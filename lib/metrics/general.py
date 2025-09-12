import logging
#
from prometheus_client import Gauge
#
from lib.classes.base import MetricsBaseClass
from lib.classes.general import GeneralAPI


class GeneralMetrics(MetricsBaseClass):
    tournament = 'general'
    metrics_prefix = f'numerai_{tournament}'

    def __init__(self, numerai_public_id: str, numerai_secret: str, *args, **kwargs) -> None:
        self.numerai_api = GeneralAPI(numerai_public_id, numerai_secret)
        super().__init__(*args, **kwargs)

    def _setup_metrics(self) -> None:
        self.nmr_price_gauge = Gauge('numerai_nmr_price', 'Current value of NMR', ['currency'])

    def set_metrics(self) -> None:
        logging.info(f'Setting {self.tournament} metrics...')

        nmr_price = self.numerai_api.get_nmr_price_usd()
        self.nmr_price_gauge.labels(currency='usd').set(float(nmr_price))

        logging.info(f'Done setting {self.tournament} general metrics...')

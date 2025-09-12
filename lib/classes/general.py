from decimal import Decimal
#
from numerapi import base_api
from numerapi.base_api import Api as NumeraiApi


class Api(base_api.Api):
    def get_nmr_price_usd(self) -> Decimal:
        query = """
            query {
              latestNmrPrice {
                lastUpdated
                priceUsd
              }
            }
        """
        raw = self.raw_query(query, authorization=True)
        return Decimal(raw['data']['latestNmrPrice']['priceUsd'])


class GeneralAPI(Api, NumeraiApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

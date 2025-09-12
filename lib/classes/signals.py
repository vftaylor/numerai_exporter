from numerapi import base_api
from numerapi import SignalsAPI as NumeraiSignalsApi


class Api(base_api.Api):
    def get_round_performance_mapping(self, model_id: str) -> dict:
        query = """
            query($tournament: Int!, $modelId: String) {
              v2RoundModelPerformances(tournament: $tournament, modelId: $modelId) {
                atRisk
                churnThreshold
                corrMultiplier
                mmcMultiplier
                prevWeekChurnMax
                prevWeekTurnoverMax
                roundResolved
                roundNumber
                roundPayoutFactor
                submissionId
                tickersAcceptedCount
                tickersSubmittedCount
                turnoverThreshold

                submissionScores {
                  displayName
                  percentile
                  payoutPending
                  payoutSettled
                  value
                }
              }
            }
        """
        raw = self.raw_query(query, {'tournament': self.tournament_id, 'modelId': model_id}, authorization=True)
        data = raw['data']['v2RoundModelPerformances']
        data = {d['roundNumber']: d for d in data}
        sorted_data = {k: data[k] for k in sorted(data.keys(), reverse=True)}  # ensure data in reverse chrono order
        return sorted_data

    def list_models(self) -> dict:
        query = """
            query {
              account {
                models {
                  id
                  name
                }
              }
            }
        """
        raw = self.raw_query(query, authorization=True)
        data = raw['data']['account']['models']
        return {d['name']: d for d in data}

    def get_latest_round(self) -> int:
        query = """
            query($tournament: Int!, $limit: Int!) {
              rounds(tournament: $tournament, limit: $limit) {
                number
              }
            }
        """
        raw = self.raw_query(query, {'tournament': self.tournament_id, 'limit': 1}, authorization=True)
        return raw['data']['rounds'][0]['number']


class SignalsAPI(Api, NumeraiSignalsApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

from collections import defaultdict
from decimal import Decimal
from statistics import mean
from typing import List, Tuple
#
from lib.enums import RoundState


def get_submission_scores(submission_scores: List) -> dict:
    output = dict()

    for submission_score in submission_scores:
        if submission_score['value'] and submission_score['percentile']:
            d = Decimal(submission_score['value']), round(Decimal(submission_score['percentile'] * 100), 1)
        else:
            d = None

        output[submission_score['displayName']] = d
    return output


def generate_data_mean_maps(data) -> Tuple[dict, dict, dict, dict, dict]:
    values_map = {
        RoundState.RESOLVED: defaultdict(list),
        RoundState.UNRESOLVED: defaultdict(list)
    }
    percentiles_map = {
        RoundState.RESOLVED: defaultdict(list),
        RoundState.UNRESOLVED: defaultdict(list)
    }
    payout_factor_map = {
        RoundState.RESOLVED: list(),
        RoundState.UNRESOLVED: list()
    }
    at_risk_map = {
        RoundState.RESOLVED: list(),
        RoundState.UNRESOLVED: list()
    }
    turnover_map = {
        RoundState.RESOLVED: list(),
        RoundState.UNRESOLVED: list()
    }

    for k, v in data.items():
        scores = get_submission_scores(v['submissionScores'])
        status = RoundState.RESOLVED if v['roundResolved'] else RoundState.UNRESOLVED

        for metric, data in scores.items():
            if data:
                value, percentile = data
                values_map[status][metric].append(value)
                percentiles_map[status][metric].append(percentile)

        if v.get('roundPayoutFactor'):
            payout_factor_map[status].append(Decimal(v['roundPayoutFactor']))

        if v.get('atRisk'):
            at_risk_map[status].append(Decimal(v['atRisk']))

        if v.get('prevWeekTurnoverMax'):
            turnover_map[status].append(Decimal(v['prevWeekTurnoverMax']))

    return values_map, percentiles_map, payout_factor_map, at_risk_map, turnover_map


def mean_for_period(values: list, period: int, round_dp: int) -> Decimal | None:
    period_values = values[:period] if period != -1 else values

    if period_values:
        return round(mean(period_values), round_dp)
    else:
        return None

from decimal import Decimal
import logging
#
from prometheus_client import Gauge
#
from config import RELEVANT_PERIODS
from lib.classes.base import MetricsBaseClass
from lib.classes.signals import SignalsAPI
from lib.enums import RoundingDP, RoundState
from lib.helpers import generate_data_mean_maps, get_submission_scores, mean_for_period


def calculate_payout_ratio_ex_pf(alpha: Decimal, mpc: Decimal) -> Decimal:
    return Decimal('0.3') * alpha + Decimal('0.8') * mpc


class SignalsMetrics(MetricsBaseClass):
    tournament = 'signals'
    metrics_prefix = f'numerai_{tournament}'

    def __init__(self, numerai_public_id: str, numerai_secret: str, *args, **kwargs) -> None:
        self.numerai_api = SignalsAPI(numerai_public_id, numerai_secret)
        super().__init__(*args, **kwargs)

    def _setup_metrics(self) -> None:
        self.latest_round_gauge = Gauge(f'{self.metrics_prefix}_latest_round', 'Latest round')

        # metrics for individual rounds
        self.percentiles_gauge = Gauge(
            f'{self.metrics_prefix}_score_percentile', 'Percentiles for a score',
            ['model', 'round', 'score_name', 'status']
        )
        self.values_gauge = Gauge(
            f'{self.metrics_prefix}_score_value', 'Values for a score', ['model', 'round', 'score_name', 'status']
        )
        self.payout_ratio_ex_pf_gauge = Gauge(
            f'{self.metrics_prefix}_payout_ratio_ex_pf', 'Payout ratio excluding payout factor',
            ['model', 'round', 'status']
        )
        self.payout_ratio_gauge = Gauge(
            f'{self.metrics_prefix}_payout_ratio', 'Payout ratio', ['model', 'round', 'status']
        )
        self.payout_pending_gauge = Gauge(
            f'{self.metrics_prefix}_payout_pending', 'Payout pending', ['model', 'round', 'status']
        )
        self.payout_settled_gauge = Gauge(
            f'{self.metrics_prefix}_payout_settled', 'Payout settled', ['model', 'round', 'status']
        )
        self.payout_factor_gauge = Gauge(
            f'{self.metrics_prefix}_payout_factor', 'Payout factor', ['model', 'round', 'status']
        )
        self.at_risk_gauge = Gauge(
            f'{self.metrics_prefix}_at_risk', 'At-risk capital', ['model', 'round', 'status']
        )
        self.turnover_gauge = Gauge(
            f'{self.metrics_prefix}_turnover', 'Turnover', ['model', 'round', 'status']
        )

        # mean metrics of rounds
        self.percentiles_mean_gauge = Gauge(
            f'{self.metrics_prefix}_score_percentile_mean', 'Mean of the percentiles for a score',
            ['model', 'score_name', 'period', 'status']
        )
        self.values_mean_gauge = Gauge(
            f'{self.metrics_prefix}_score_value_mean', 'Mean of the values for a score',
            ['model', 'score_name', 'period', 'status']
        )
        self.payout_ratio_ex_pf_mean_gauge = Gauge(
            f'{self.metrics_prefix}_payout_ratio_ex_pf_mean', 'Mean of payout ratio excluding payout factor',
            ['model', 'period', 'status']
        )
        self.payout_ratio_mean_gauge = Gauge(
            f'{self.metrics_prefix}_payout_ratio_mean', 'Mean of payout ratio', ['model', 'period', 'status']
        )
        self.payout_factor_mean_gauge = Gauge(
            f'{self.metrics_prefix}_payout_factor_mean', 'Mean of payout factor', ['model', 'period', 'status']
        )
        self.at_risk_mean_gauge = Gauge(
            f'{self.metrics_prefix}_at_risk_mean', 'Mean of at-risk capital', ['model', 'period', 'status']
        )
        self.turnover_mean_gauge = Gauge(
            f'{self.metrics_prefix}_turnover_mean', 'Mean of turnover', ['model', 'period', 'status']
        )

    def _calculate_round_metrics(self, model_name: str, round_data: dict) -> None:
        submission_scores = round_data['submissionScores']
        scores = get_submission_scores(submission_scores)

        alpha_data = scores['alpha']
        mpc_data = scores['mpc']
        payout_factor = round_data['roundPayoutFactor']
        round_number = round_data['roundNumber']
        at_risk = round_data['atRisk']
        status = RoundState.RESOLVED if round_data['roundResolved'] else RoundState.UNRESOLVED
        payout_pending = submission_scores[0]['payoutPending']  # this is duplicated for all metrics so take first one
        payout_settled = submission_scores[0]['payoutSettled']  # this is duplicated for all metrics so take first one
        turnover = round_data['prevWeekTurnoverMax']

        for score, value in scores.items():
            if value is not None:
                score_value, score_percentile = value
                self.percentiles_gauge.labels(
                    model=model_name, round=round_number, score_name=score, status=status
                ).set(float(score_percentile))
                self.values_gauge.labels(
                    model=model_name, round=round_number, score_name=score, status=status
                ).set(float(score_value))

        if alpha_data is not None and mpc_data is not None and payout_factor is not None:
            alpha_value, alpha_percentile = alpha_data
            mpc_value, mpc_percentile = mpc_data
            payout_ratio_ex_pf = calculate_payout_ratio_ex_pf(alpha_value, mpc_value)
            payout_ratio = Decimal(payout_factor) * payout_ratio_ex_pf

            self.payout_ratio_ex_pf_gauge.labels(model=model_name, round=round_number, status=status).set(
                float(payout_ratio_ex_pf)
            )
            self.payout_ratio_gauge.labels(model=model_name, round=round_number, status=status).set(float(payout_ratio))

        if at_risk is not None:
            self.at_risk_gauge.labels(
                model=model_name, round=round_number, status=status
            ).set(float(at_risk))

        if payout_pending:
            self.payout_pending_gauge.labels(
                model=model_name, round=round_number, status=status
            ).set(float(payout_pending))

        if payout_settled:
            self.payout_settled_gauge.labels(
                model=model_name, round=round_number, status=status
            ).set(float(payout_pending))

        if payout_factor:
            self.payout_factor_gauge.labels(
                model=model_name, round=round_number, status=status
            ).set(float(payout_factor))

        if turnover:
            self.turnover_gauge.labels(
                model=model_name, round=round_number, status=status
            ).set(float(turnover))

    def _calculate_round_mean_metrics(self, round_performance_mapping: dict, model_name: str, status: str, period: int)\
            -> None:
        period_name = f'{period}d' if period != -1 else 'all'
        values_map, percentiles_map, payout_factor_map, at_risk_map, turnover_map = (
            generate_data_mean_maps(round_performance_mapping)
        )

        for score, values in percentiles_map[status].items():
            mean_calc = mean_for_period(values, period, RoundingDP.ONE)
            if mean_calc is not None:
                self.percentiles_mean_gauge.labels(
                    model=model_name, score_name=score, period=period_name, status=status
                ).set(float(mean_calc))

        for score, values in values_map[status].items():
            mean_calc = mean_for_period(values, period, RoundingDP.FOUR)
            if mean_calc is not None:
                self.values_mean_gauge.labels(
                    model=model_name, score_name=score, period=period_name, status=status
                ).set(float(mean_calc))

        alpha_mean = mean_for_period(values_map[status]['alpha'], period, RoundingDP.FOUR)
        mpc_mean = mean_for_period(values_map[status]['mpc'], period, RoundingDP.FOUR)
        payout_factor_mean = mean_for_period(payout_factor_map[status], period, RoundingDP.FOUR)
        at_risk_mean = mean_for_period(at_risk_map[status], period, RoundingDP.FOUR)
        turnover_mean = mean_for_period(turnover_map[status], period, RoundingDP.FOUR)

        if alpha_mean is not None and mpc_mean is not None and payout_factor_mean is not None:
            payout_ratio_ex_pf = calculate_payout_ratio_ex_pf(alpha_mean, mpc_mean)
            payout_ratio = payout_factor_mean * payout_ratio_ex_pf

            self.payout_ratio_ex_pf_mean_gauge.labels(model=model_name, period=period_name, status=status).set(
                float(payout_ratio_ex_pf)
            )
            self.payout_ratio_mean_gauge.labels(model=model_name, period=period_name, status=status).set(
                float(payout_ratio)
            )

        if at_risk_mean is not None:
            self.at_risk_mean_gauge.labels(model=model_name, period=period_name, status=status).set(float(at_risk_mean))

        if payout_factor_mean is not None:
            self.payout_factor_mean_gauge.labels(model=model_name, period=period_name, status=status).set(float(
                payout_factor_mean))

        if turnover_mean is not None:
            self.turnover_mean_gauge.labels(model=model_name, period=period_name, status=status).set(float(
                turnover_mean))

    def set_metrics(self) -> None:
        latest_round = self.numerai_api.get_latest_round()
        self.latest_round_gauge.set(int(latest_round))

        models = self.numerai_api.list_models()
        logging.info(f'Generating {self.tournament} metrics for {len(models.keys())} models.')

        for model_name, data in models.items():
            logging.info(f'Setting {self.tournament} metrics for {model_name}.')
            round_performance_mapping = self.numerai_api.get_round_performance_mapping(model_id=data['id'])

            # CALCULATE INDIVIDUAL ROUND METRICS
            for round_number, round_data in round_performance_mapping.items():
                self._calculate_round_metrics(model_name, round_data)

            # CALCULATE MEAN OF ROUNDS METRICS
            for state in RoundState:
                for period in RELEVANT_PERIODS:
                    self._calculate_round_mean_metrics(round_performance_mapping, model_name, state, period)

        logging.info(f'Done generating {self.tournament} metrics.')

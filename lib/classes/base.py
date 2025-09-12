class MetricsBaseClass:
    def __init__(self, *args, **kwargs):
        self._setup_metrics()

    def _setup_metrics(self) -> None:
        raise NotImplementedError

    def set_metrics(self) -> None:
        raise NotImplementedError

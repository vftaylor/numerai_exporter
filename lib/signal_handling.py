import logging
import signal
import sys


def _handle_exit_signal(_signum, _frame) -> None:
    logging.info('Caught Ctrl+C. Exiting.')
    sys.exit(0)


def setup_signal_handling() -> None:
    signal.signal(signal.SIGTERM, _handle_exit_signal)
    signal.signal(signal.SIGINT, _handle_exit_signal)

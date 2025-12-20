import logging
from app.utils_legacy.constants import Constants


class LoggingConfig:
    @staticmethod
    def setup_logging(debug: bool = False):
        level = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(
            level=level,
            format=Constants.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
            ],
        )

        if not debug:
            LoggingConfig._suppress_third_party_logs()

    @staticmethod
    def _suppress_third_party_logs():
        for logger_name in Constants.SUPPRESSED_LOGGERS:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


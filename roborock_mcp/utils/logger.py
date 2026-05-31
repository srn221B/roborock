import logging

_formatter = '%(asctime)s - (%(filename)s) - [%(levelname)s] - %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=_formatter)
_logger = logging.getLogger(__name__)


class Log:
    @staticmethod
    def info(msg: str) -> None:
        return _logger.info(msg)

    @staticmethod
    def error(msg: str) -> None:
        return _logger.error(msg)

    @staticmethod
    def debug(msg: str) -> None:
        return _logger.debug(msg)

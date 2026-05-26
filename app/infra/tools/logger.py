import logging

from core.interfaces.infra.tools.i_logger import ILogger
from infra.config.settings import settings


class Logger(ILogger):
    def __init__(self):
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger("area_verde")

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def success(self, message: str) -> None:
        self.logger.info(f"SUCCESS: {message}")

    def warn(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

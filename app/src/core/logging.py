import logging
import sys

from src.core.config import Settings


def configure_basic_logging(settings: Settings) -> None:
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=settings.log_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,
    )

    if settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def setup_logging(settings: Settings) -> None:
    configure_basic_logging(settings)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured: level=%s, environment=%s",
        logging.getLevelName(settings.log_level),
        settings.environment.value,
    )

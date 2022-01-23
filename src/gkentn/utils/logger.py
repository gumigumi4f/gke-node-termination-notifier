import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S %z")
    )
    logger.addHandler(handler)
    return logger

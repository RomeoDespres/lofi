import functools
import logging


@functools.lru_cache
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

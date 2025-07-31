"""Logging utilities"""

import logging


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper()))
    return logger

import logging
import logging.config

logger = logging.getLogger(__name__)


def get_config() -> dict:
    """Generate the current log configuration as a dictionary."""
    sqelched_loggers = {
        name: {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        }
        for name in [
            "azure.core.pipeline.policies.http_logging_policy",
        ]
    }
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
            },
        },
        "loggers": {**sqelched_loggers},
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    }


def configure():
    logging.config.dictConfig(get_config())

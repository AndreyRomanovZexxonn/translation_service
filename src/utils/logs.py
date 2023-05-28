from typing import TYPE_CHECKING, Optional

import coloredlogs

if TYPE_CHECKING:
    from src.utils.configs.app_config import EnvConfig


def init_logging(
    cfg: Optional['EnvConfig'] = None,
    fmt: Optional[str] = None,
    error_loggers: Optional[list] = None,
    warning_loggers: Optional[list] = None
):
    fmt = (
        fmt or "%(asctime)s %(name)s[%(process)d] %(levelname)s %(" "message)s"
    )
    loglvl = (cfg and cfg.log_level) or 'DEBUG'
    coloredlogs.install(
        level=loglvl, isatty=True, fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S.%f"
    )

    import logging

    for logger_name in (warning_loggers or []):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    for logger_name in (error_loggers or []):
        logging.getLogger(logger_name).setLevel(logging.ERROR)

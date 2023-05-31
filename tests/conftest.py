import logging
import os
import time

import coloredlogs
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    if log_level := os.getenv("TESTS_LOG_LEVEL"):
        coloredlogs.install(level=log_level)
    else:
        return

    for logger_name in []:
        # in test env we do not have DataDog, skip this logs, it won't affect the tests
        logging.getLogger(logger_name).setLevel("CRITICAL")

    logger = logging.getLogger(__name__)
    logger.debug("")
    logger.debug("Logging is set up")


@pytest.fixture(scope="session", autouse=True)
def set_utc_timezone():
    os.environ['TZ'] = 'UTC'
    time.tzset()


@pytest.fixture(scope="session")
def monkeysession(request):
    """ As monkeypatch but for `session` scoped fixtures """
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="module")
def monkeymodule(request):
    """ As monkeypatch but for `module` scoped fixtures """
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()

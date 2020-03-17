import logging

from auto_deprecator import deprecate

LOGGER = logging.getLogger(__name__)


@deprecate(
    expiry="2.1.0",
    current="2.0.0",
    relocate="other_func",
    warn_handler=lambda msg: LOGGER.warning(msg),
)
def warn_handler_replaced():
    pass


@deprecate(
    expiry="2.1.0",
    current="2.2.0",
    relocate="other_func",
    error_handler=lambda msg: LOGGER.warning(msg),
)
def error_handler_replaced():
    pass


def test_deprecated_warn_handler_replaced(caplog):
    with caplog.at_level(logging.WARNING, logger=__name__):
        warn_handler_replaced()

    assert (
        'Function "warn_handler_replaced" will be deprecated '
        'on version 2.1.0. Please use function / method "other_func"'
    ) in caplog.text


def test_deprecated_error_handler_replaced(caplog):
    with caplog.at_level(logging.WARNING, logger=__name__):
        error_handler_replaced()

    assert (
        'Function "error_handler_replaced" is deprecated since '
        'version 2.1.0. Please use function / method "other_func"'
    ) in caplog.text

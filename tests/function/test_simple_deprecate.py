import pytest

from auto_deprecator import deprecate


@deprecate()
def simple_deprecate():
    pass


def test_no_error_simple_deprecate():
    with pytest.warns(DeprecationWarning) as warning:
        simple_deprecate()

    assert (
        'Function "simple_deprecate" will '
        "be deprecated soon"
    ) in warning[0].message.args[0]



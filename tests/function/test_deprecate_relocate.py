import pytest

from auto_deprecator import deprecate


@deprecate(expiry='2.1.0', current='2.0.0', relocate='other_func')
def simple_deprecate():
    pass


def test_no_error_simple_deprecate():
    with pytest.warns(DeprecationWarning) as warning:
        simple_deprecate()

    assert (
        'Function "simple_deprecate" will be deprecated on version '
        '2.1.0. Please use function / method "other_func"'
    ) in warning[0].message.args[0]


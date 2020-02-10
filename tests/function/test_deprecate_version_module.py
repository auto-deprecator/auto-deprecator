import pytest

from auto_deprecator import deprecate


__version__ = "2.0.0"


@deprecate(
    expiry="2.1.0",
    version_module="tests.function.test_deprecate_version_module",
)
def simple_deprecate():
    pass


@deprecate(
    expiry="2.1.0", version_module="tests.function.conftest",
)
def failed_to_locate_version():
    pass


@deprecate(
    expiry="2.1.0", version_module="tests.function.not_existing_module",
)
def not_existing_module():
    pass


def test_no_error_simple_deprecate():
    with pytest.warns(DeprecationWarning) as warning:
        simple_deprecate()

    assert (
        'Function "simple_deprecate" will be deprecated on version 2.1.0'
    ) in warning[0].message.args[0]


def test_failed_to_locate_version():
    with pytest.raises(RuntimeError) as error:
        failed_to_locate_version()

    assert (
        "Cannot find version (__version__) from the version module "
        '"tests.function.conftest"'
    ) in str(error.value)


def test_not_existing_module():
    with pytest.raises(RuntimeError) as error:
        not_existing_module()

    assert (
        'Cannot locate version module "tests.function.not_existing_module"'
    ) in str(error.value)

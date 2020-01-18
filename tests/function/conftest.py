import importlib.util
from tempfile import NamedTemporaryFile

import pytest


IMPORT_STATEMENT = """from auto_deprecator import deprecate"""


NORMAL_FUNCTION = """


def normal_function():
    pass"""


DEPRECATE_FUNCTION_2_0_0 = """


@deprecate(expiry="2.0.0", current="2.1.0")
def deprecate_version_2_0_0():
    pass"""


DEPRECATE_FUNCTION_2_1_0 = """


@deprecate(expiry="2.1.0", current="2.1.0")
def deprecate_version_2_1_0():
    pass"""


DEPRECATE_FUNCTION_2_2_0 = """


@deprecate(expiry="2.2.0", current="2.1.0")
def deprecate_version_2_2_0():
    pass"""


@pytest.fixture(scope="session")
def function_file_str():
    return (
        IMPORT_STATEMENT
        + NORMAL_FUNCTION
        + DEPRECATE_FUNCTION_2_0_0
        + DEPRECATE_FUNCTION_2_1_0
        + DEPRECATE_FUNCTION_2_2_0
    )


@pytest.fixture
def function_file(function_file_str):
    with NamedTemporaryFile(mode="a+", suffix=".py") as tmpfile:
        tmpfile.write(function_file_str)
        tmpfile.flush()
        yield tmpfile.name


@pytest.fixture
def function_module(function_file):
    spec = importlib.util.spec_from_file_location("function", function_file)
    function_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(function_module)
    return function_module

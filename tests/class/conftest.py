import importlib.util
from tempfile import NamedTemporaryFile

import pytest


IMPORT_STATEMENT = r"""from auto_deprecator import deprecate


"""

CLASS_DELARATION = r"""class DummyClass:"""

INIT_METHOD = r"""

    def __init__(self):
        pass"""

DEPRECATE_2_0_0 = r"""

    @deprecate(expiry="2.0.0", current="2.1.0")
    def deprecate_version_2_0_0(self):
        pass"""

DEPRECATE_2_1_0 = r"""

    @deprecate(expiry="2.1.0", current="2.1.0")
    def deprecate_version_2_1_0(self):
        pass"""

DEPRECATE_2_2_0 = r"""

    @deprecate(expiry="2.2.0", current="2.1.0")
    def deprecate_version_2_2_0(self):
        pass"""

INNER_CLASS = r"""

    class DummyClass2:
        @deprecate(expiry="2.3.0", current="2.1.0")
        def deprecate_version_2_3_0(self):
            pass"""


@pytest.fixture(scope="session")
def dummy_class():
    return (
        IMPORT_STATEMENT
        + CLASS_DELARATION
        + INIT_METHOD
        + DEPRECATE_2_0_0
        + DEPRECATE_2_1_0
        + DEPRECATE_2_2_0
        + INNER_CLASS
    )


@pytest.fixture
def dummy_class_file(dummy_class):
    with NamedTemporaryFile(mode="a+", suffix=".py") as tmpfile:
        tmpfile.write(dummy_class)
        tmpfile.flush()
        yield tmpfile.name


@pytest.fixture(name="DummyClass")
def dummy_class_fixture(dummy_class_file):
    spec = importlib.util.spec_from_file_location(
        "dummy_class", dummy_class_file
    )
    dummy_class = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dummy_class)
    return dummy_class.DummyClass

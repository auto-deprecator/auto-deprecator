from os.path import join
import pkg_resources
import shutil
from tempfile import NamedTemporaryFile

import pytest

from auto_deprecator.cli.auto_deprecate import deprecate_single_file


IMPORT_STATEMENT = r"""from auto_deprecator import deprecate


"""

CLASS_DELARATION = r"""class DummyClass:"""

INIT_METHOD = (r"""

    def __init__(self):
        pass""")

DEPRECATE_2_0_0 = (r"""

    @deprecate("2.0.0")
    def deprecate_version_2_0_0(self):
        pass""")

DEPRECATE_2_1_0 = (r"""

    @deprecate("2.1.0")
    def deprecate_version_2_1_0(self):
        pass""")

DEPRECATE_2_2_0 = (r"""

    @deprecate("2.2.0")
    def deprecate_version_2_2_0(self):
        pass""")

INNER_CLASS = (r"""

    class DummyClass2:
        @deprecate("2.3.0")
        def deprecate_version_2_3_0(self):
            pass""")


@pytest.fixture(scope="session")
def dummy_class():
    return (
        IMPORT_STATEMENT +
        CLASS_DELARATION +
        INIT_METHOD +
        DEPRECATE_2_0_0 +
        DEPRECATE_2_1_0 +
        DEPRECATE_2_2_0 +
        INNER_CLASS
    )


@pytest.fixture
def dummy_class_file(dummy_class):
    with NamedTemporaryFile(mode='a+') as tmpfile:
        tmpfile.write(dummy_class)
        tmpfile.flush()
        yield tmpfile.name


def test_auto_deprecate_single_file_2_1_0(dummy_class_file):
    deprecate_single_file(
        filename=dummy_class_file, current="2.1.0"
    )

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT +
        CLASS_DELARATION +
        INIT_METHOD +
        DEPRECATE_2_2_0 +
        INNER_CLASS)


def test_auto_deprecate_single_file_2_2_0(dummy_class_file):
    deprecate_single_file(
        filename=dummy_class_file, current="2.2.0"
    )

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT +
        CLASS_DELARATION +
        INIT_METHOD +
        INNER_CLASS)


def test_auto_deprecate_single_file_2_3_0(dummy_class_file):
    deprecate_single_file(
        filename=dummy_class_file, current="2.3.0"
    )

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        CLASS_DELARATION +
        INIT_METHOD)

import pytest

from auto_deprecator import SingleFileAutoDeprecator

from .conftest import NORMAL_FUNCTION

SHEBANG = "#!/bin/python"

DEPRECATE_FUNCTION_2_0_0_COMMENT = """


def deprecate_version_2_0_0_comment():
    \"\"\"Deprecate version 2.0.0.
    \"\"\"
    # auto-deprecate: expiry=2.0.0
    pass"""

DEPRECATE_INNER_FUNCTION_2_1_0_COMMENT = """


def deprecate_version_2_1_0_only_inner():
    print('hello world')

    def deprecate_version_2_1_0_comment():
        #  auto-deprecate: expiry=2.1.0
        pass

    print('bye bye')"""

@pytest.fixture
def function_file_str():
    return (
        SHEBANG
        + NORMAL_FUNCTION
        + DEPRECATE_FUNCTION_2_0_0_COMMENT
        + DEPRECATE_INNER_FUNCTION_2_1_0_COMMENT
    )


def test_auto_deprecate_single_file_2_1_0(function_file):
    SingleFileAutoDeprecator(
        filename=function_file,
        current="2.1.0"
    ).run()

    filestream = open(function_file, "r").read()
    assert filestream == (
        SHEBANG
        + NORMAL_FUNCTION
        + DEPRECATE_INNER_FUNCTION_2_1_0_COMMENT
    )


def test_auto_deprecate_single_file_2_2_0(function_file):
    SingleFileAutoDeprecator(
        filename=function_file,
        current="2.2.0"
    ).run()

    filestream = open(function_file, "r").read()
    assert filestream == (
        SHEBANG + NORMAL_FUNCTION + """


def deprecate_version_2_1_0_only_inner():
    print('hello world')

    print('bye bye')""")

import pytest

from auto_deprecator import SingleFileAutoDeprecator

from .conftest import (
    NORMAL_FUNCTION, DEPRECATE_FUNCTION_2_0_0_COMMENT
)

SHEBANG = "#!/bin/python"


@pytest.fixture
def function_file_str():
    return (
        SHEBANG
        + NORMAL_FUNCTION
        + DEPRECATE_FUNCTION_2_0_0_COMMENT
    )


def test_auto_deprecate_single_file_2_1_0(function_file):
    SingleFileAutoDeprecator(
        filename=function_file,
        current="2.1.0"
    ).run()

    filestream = open(function_file, "r").read()
    assert filestream == (
        SHEBANG + NORMAL_FUNCTION
    )

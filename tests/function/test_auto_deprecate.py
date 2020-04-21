from auto_deprecator import SingleFileAutoDeprecator

from .conftest import (
    IMPORT_STATEMENT,
    NORMAL_FUNCTION,
    DEPRECATE_FUNCTION_2_2_0,
)


def test_auto_deprecate_single_file_2_1_0(function_file):
    SingleFileAutoDeprecator(
        filename=function_file,
        current="2.1.0"
    ).run()

    filestream = open(function_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT + NORMAL_FUNCTION + DEPRECATE_FUNCTION_2_2_0
    )


def test_auto_deprecate_single_file_2_2_0(function_file):
    SingleFileAutoDeprecator(
        filename=function_file,
        current="2.2.0"
    ).run()

    filestream = open(function_file, "r").read()
    assert filestream == (NORMAL_FUNCTION).lstrip("\n")

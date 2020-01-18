from auto_deprecator.cli.auto_deprecate import deprecate_single_file

from .conftest import (
    IMPORT_STATEMENT,
    CLASS_DELARATION,
    INIT_METHOD,
    DEPRECATE_2_2_0,
    INNER_CLASS,
)


def test_auto_deprecate_single_file_2_1_0(dummy_class_file):
    deprecate_single_file(filename=dummy_class_file, current="2.1.0")

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT
        + CLASS_DELARATION
        + INIT_METHOD
        + DEPRECATE_2_2_0
        + INNER_CLASS
    )


def test_auto_deprecate_single_file_2_2_0(dummy_class_file):
    deprecate_single_file(filename=dummy_class_file, current="2.2.0")

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT + CLASS_DELARATION + INIT_METHOD + INNER_CLASS
    )


def test_auto_deprecate_single_file_2_3_0(dummy_class_file):
    deprecate_single_file(filename=dummy_class_file, current="2.3.0")

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (CLASS_DELARATION + INIT_METHOD)

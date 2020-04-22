from auto_deprecator import SingleFileAutoDeprecator

from .conftest import (
    IMPORT_STATEMENT,
    CLASS_DELARATION,
    INIT_METHOD,
    DEPRECATE_2_2_0,
    DEPRECATE_2_2_0_PROPERTY,
    INNER_CLASS,
)


def test_auto_deprecate_single_file_2_2_0(dummy_class_file):
    SingleFileAutoDeprecator(
        filename=dummy_class_file,
        current="2.2.0"
    ).run()

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT
        + CLASS_DELARATION
        + INIT_METHOD
        + DEPRECATE_2_2_0
        + DEPRECATE_2_2_0_PROPERTY
        + INNER_CLASS
    )


def test_auto_deprecate_single_file_2_3_0(dummy_class_file):
    SingleFileAutoDeprecator(
        filename=dummy_class_file,
        current="2.3.0"
    ).run()

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (
        IMPORT_STATEMENT + CLASS_DELARATION + INIT_METHOD + INNER_CLASS
    )


def test_auto_deprecate_single_file_2_4_0(dummy_class_file):
    SingleFileAutoDeprecator(
        filename=dummy_class_file,
        current="2.4.0"
    ).run()

    filestream = open(dummy_class_file, "r").read()
    assert filestream == (CLASS_DELARATION + INIT_METHOD)

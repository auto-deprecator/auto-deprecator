import pytest

from auto_deprecator.cli.auto_deprecate import deprecate_single_file


@pytest.fixture
def function_file_str():
    return """#!/bin/python
def normal_func():
    pass


def deprecate_version_2_0_0():
    \"\"\"Deprecate version 2.0.0.
    \"\"\"
    # auto-deprecate: expiry=2.0.0
    pass"""


def test_auto_deprecate_single_file_2_1_0(function_file):
    deprecate_single_file(filename=function_file, current="2.1.0")

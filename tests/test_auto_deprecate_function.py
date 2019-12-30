from os.path import join
import pkg_resources
import shutil
from tempfile import TemporaryDirectory

import pytest

from auto_deprecator.cli.auto_deprecate import (
    deprecate_single_file
)


def test_auto_deprecate_single_file_2_1_0():
    with TemporaryDirectory() as tmpdir:
        test_function_path = pkg_resources.resource_filename(
            'tests.test_project', 'function.py')
        shutil.copyfile(test_function_path, join(tmpdir, 'function.py'))

        deprecate_single_file(
            filename=join(tmpdir, 'function.py'),
            curr_version='2.1.0')

        filestream = open(join(tmpdir, 'function.py'), 'r').read()
        assert filestream == (
"""from auto_deprecator import deprecate


def normal_function():
    pass


@deprecate(version='2.2.0')
def deprecate_version_2_2_0():
    pass""")


def test_auto_deprecate_single_file_2_2_0():
    with TemporaryDirectory() as tmpdir:
        test_function_path = pkg_resources.resource_filename(
            'tests.test_project', 'function.py')
        shutil.copyfile(test_function_path, join(tmpdir, 'function.py'))

        deprecate_single_file(
            filename=join(tmpdir, 'function.py'),
            curr_version='2.2.0')

        filestream = open(join(tmpdir, 'function.py'), 'r').read()
        assert filestream == (
"""def normal_function():
    pass""")

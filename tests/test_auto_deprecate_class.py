from os.path import join
import pkg_resources
import shutil
from tempfile import TemporaryDirectory

from auto_deprecator.cli.auto_deprecate import deprecate_single_file


def test_auto_deprecate_single_file_2_1_0():
    with TemporaryDirectory() as tmpdir:
        test_function_path = pkg_resources.resource_filename(
            "tests.test_project", "dummy_class.py"
        )
        shutil.copyfile(test_function_path, join(tmpdir, "dummy_class.py"))

        deprecate_single_file(
            filename=join(tmpdir, "dummy_class.py"), curr_version="2.1.0"
        )

        filestream = open(join(tmpdir, "dummy_class.py"), "r").read()
        assert filestream == (
            """from auto_deprecator import deprecate


class DummyClass:

    def __init__(self):
        pass

    @deprecate(version='2.2.0')
    def deprecate_version_2_2_0(self):
        pass

    class DummyClass2:
        @deprecate(version='2.3.0')
        def deprecate_version_2_3_0(self):
            pass"""
        )


def test_auto_deprecate_single_file_2_2_0():
    with TemporaryDirectory() as tmpdir:
        test_function_path = pkg_resources.resource_filename(
            "tests.test_project", "dummy_class.py"
        )
        shutil.copyfile(test_function_path, join(tmpdir, "dummy_class.py"))

        deprecate_single_file(
            filename=join(tmpdir, "dummy_class.py"), curr_version="2.2.0"
        )

        filestream = open(join(tmpdir, "dummy_class.py"), "r").read()
        assert filestream == (
            """from auto_deprecator import deprecate


class DummyClass:

    def __init__(self):
        pass

    class DummyClass2:
        @deprecate(version='2.3.0')
        def deprecate_version_2_3_0(self):
            pass"""
        )


def test_auto_deprecate_single_file_2_3_0():
    with TemporaryDirectory() as tmpdir:
        test_function_path = pkg_resources.resource_filename(
            "tests.test_project", "dummy_class.py"
        )
        shutil.copyfile(test_function_path, join(tmpdir, "dummy_class.py"))

        deprecate_single_file(
            filename=join(tmpdir, "dummy_class.py"), curr_version="2.3.0"
        )

        filestream = open(join(tmpdir, "dummy_class.py"), "r").read()
        assert filestream == (
            """class DummyClass:

    def __init__(self):
        pass"""
        )

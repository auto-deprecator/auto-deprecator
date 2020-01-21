from os import environ

import pytest


def test_deprecate_version_2_0_0_with_1_9_0(function_module):
    environ['DEPRECATE_VERSION'] = '1.9.0'

    with pytest.warns(DeprecationWarning) as warning:
        function_module.deprecate_version_2_0_0()

    environ['DEPRECATE_VERSION'] = ''

    assert (
        'Function "deprecate_version_2_0_0" will '
        "be deprecated on version 2.0.0"
    ) in warning[0].message.args[0]


def test_deprecate_version_2_0_0_with_2_1_0(function_module):
    environ['DEPRECATE_VERSION'] = '2.1.0'

    with pytest.raises(RuntimeError) as err:
        function_module.deprecate_version_2_0_0()

    environ['DEPRECATE_VERSION'] = ''

    assert (
        'Function "deprecate_version_2_0_0" is '
        "deprecated since version 2.0.0"
    ) in str(err)


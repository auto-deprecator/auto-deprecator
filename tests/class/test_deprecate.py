import pytest


def test_deprecate_version_2_0_0(DummyClass):
    with pytest.raises(RuntimeError) as err:
        obj = DummyClass()
        obj.deprecate_version_2_0_0()

    assert (
        'Function "deprecate_version_2_0_0" is '
        "deprecated since version 2.0.0"
    ) in str(err)


def test_deprecate_version_2_1_0(DummyClass):
    with pytest.raises(RuntimeError) as err:
        obj = DummyClass()
        obj.deprecate_version_2_1_0()

    assert (
        'Function "deprecate_version_2_1_0" is '
        "deprecated since version 2.1.0"
    ) in str(err)


def test_deprecate_version_2_2_0(DummyClass):
    with pytest.warns(DeprecationWarning) as warning:
        obj = DummyClass()
        obj.deprecate_version_2_2_0()

    assert (
        'Function "deprecate_version_2_2_0" will '
        "be deprecated on version 2.2.0"
    ) in warning[0].message.args[0]

    with pytest.warns(DeprecationWarning) as warning:
        obj = DummyClass()
        obj.deprecate_property_2_2_0()

    assert (
        'Function "deprecate_property_2_2_0" will '
        "be deprecated on version 2.2.0"
    ) in warning[0].message.args[0]

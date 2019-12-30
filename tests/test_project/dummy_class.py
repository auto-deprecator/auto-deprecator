from auto_deprecator import deprecate


class DummyClass:

    def __init__(self):
        pass

    @deprecate(version='2.0.0')
    def deprecate_version_2_0_0(self):
        pass

    @deprecate(version='2.1.0')
    def deprecate_version_2_1_0(self):
        pass

    @deprecate(version='2.2.0')
    def deprecate_version_2_2_0(self):
        pass

    class DummyClass2:
        @deprecate(version='2.3.0')
        def deprecate_version_2_3_0(self):
            pass

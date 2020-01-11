from auto_deprecator import deprecate


def normal_function():
    pass


@deprecate("2.0.0")
def deprecate_version_2_0_0():
    pass


@deprecate("2.1.0")
def deprecate_version_2_1_0():
    pass


@deprecate("2.2.0")
def deprecate_version_2_2_0():
    pass

"""Main module."""
from os import environ
from importlib import import_module
from warnings import warn


def deprecate(version=None, curr_version=None):
    def _deprecate(func):
        def wrapper(*args, **kwargs):
            # Check whether the function is deprecated
            is_deprecated = check_deprecation(
                func=func, version=version, curr_version=curr_version,
            )

            # Throw exception if deprecation
            if is_deprecated:
                handle_deprecation(func=func, version=version)

            # Run the function
            result = func(*args, **kwargs)

            # Alert the user that the function will be
            # deprecated
            alert_future_deprecation(func=func, version=version)

            return result

        return wrapper

    return _deprecate


def get_curr_version(func, curr_version):
    if "DEPRECATE_VERSION" in environ:
        return environ["DEPRECATE_VERSION"]

    if curr_version:
        return curr_version

    module = ""
    imported_module = func.__module__

    while imported_module:
        tmp_module, _, imported_module = imported_module.partition(".")
        module = module + "." + tmp_module if module else tmp_module
        m = import_module(module, "__version__")
        try:
            return getattr(m, "__version__")
        except AttributeError:
            continue

    raise RuntimeError(
        (
            'No version can be found in function "{func}" from all the '
            'parent modules "{module}"'
        ).format(func=func.__name__, module=func.__module__)
    )


def check_deprecation(func=None, version=None, curr_version=None):
    if version is not None:
        curr_version = get_curr_version(func, curr_version)

        if curr_version >= version:
            return True

    return False


def handle_deprecation(func, version=None):
    err_msg = 'Function "{func}" is deprecated since '.format(
        func=func.__name__
    )

    if version is not None:
        err_msg += "version {version}".format(version=version)

    raise RuntimeError(err_msg)


def alert_future_deprecation(func, version=None):
    warning_msg = 'Function "{func}" will be deprecated on '.format(
        func=func.__name__
    )

    if version is not None:
        warning_msg += "version {version}".format(version=version)

    warn(warning_msg, DeprecationWarning)

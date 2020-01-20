"""Main module."""
from os import environ
from importlib import import_module
from warnings import warn


def deprecate(expiry=None, current=None):
    def _deprecate(func):
        def wrapper(*args, **kwargs):
            # Check whether the function is deprecated
            is_deprecated = check_deprecation(
                func=func, expiry=expiry, current=current,
            )

            # Throw exception if deprecation
            if is_deprecated:
                handle_deprecation(func=func, expiry=expiry)

            # Run the function
            result = func(*args, **kwargs)

            # Alert the user that the function will be
            # deprecated
            alert_future_deprecation(func=func, expiry=expiry)

            return result

        return wrapper

    return _deprecate


def get_curr_version(func, current):
    if "DEPRECATE_VERSION" in environ:
        return environ["DEPRECATE_VERSION"]

    if current:
        return current

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


def check_deprecation(func=None, expiry=None, current=None):
    if expiry is not None:
        current = get_curr_version(func, current)

        if current >= expiry:
            return True

    return False


def handle_deprecation(func, expiry=None):
    if expiry is None:
        return

    raise RuntimeError(
        'Function "{func}" is deprecated since version {version}'.format(
            func=func.__name__, version=expiry
        )
    )


def alert_future_deprecation(func, expiry=None):
    if expiry is None:
        version_msg = 'soon'
    else:
        version_msg = 'on version {version}'.format(version=expiry)

    warn(
        'Function "{func}" will be deprecated {version_msg}'.format(
            func=func.__name__, version_msg=version_msg
        ),
        DeprecationWarning,
    )

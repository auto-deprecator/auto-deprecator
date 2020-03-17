"""Main module."""
from os import environ
from importlib import import_module
from warnings import warn


def deprecate(
    expiry=None,
    current=None,
    relocate=None,
    version_module=None,
    error_handler=None,
    warn_handler=None,
):
    """Deprecate

    This is a function decorator which

      1. If the current version is before the expiry version, by deafult,
         a deprecation warning is raised.

      2. If the current version is same as or after the expiry version, by
         default, an exception is raised.

    :param expiry: `str` The expiry version, e.g. 2.1.0.
    :param current: `str` The current version. e.g. 2.0.0.
    :param relocate: `str` The relocated method or function name, which will
        be hinted if warning or exception is raised.
    :param version_module: `str` The module name which includes the current
        version (__version__).
    :param error_handler: `Callable[msg]` The error handler with message
        as the parameter. The default handler is to raise the runtime error.
    :param warn_handler: `Callable[msg]` The warning handler with message
        as the parameter. The default handler is to raise the deprecation
        warning.
    """

    def _deprecate(func):
        def wrapper(*args, **kwargs):
            # Check whether the function is deprecated
            is_deprecated = check_deprecation(
                expiry=expiry, current=current, version_module=version_module
            )

            # Throw exception if deprecation
            if is_deprecated:
                handle_deprecation(
                    handler=error_handler,
                    func=func,
                    expiry=expiry,
                    relocate=relocate,
                )

            # Run the function
            result = func(*args, **kwargs)

            # Alert the user that the function will be
            # deprecated
            if not is_deprecated:
                alert_future_deprecation(
                    handler=warn_handler,
                    func=func,
                    expiry=expiry,
                    relocate=relocate,
                )

            return result

        return wrapper

    return _deprecate


def get_curr_version(current, version_module):
    if "DEPRECATE_VERSION" in environ:
        return environ["DEPRECATE_VERSION"]

    assert (current is not None) or (version_module is not None), (
        "Only the current version (%s) or the version module (%s) "
        "should be specified"
    ) % (current, version_module)

    if current:
        return current

    try:
        module = import_module(version_module, "__version__")
    except ModuleNotFoundError:
        raise RuntimeError(
            'Cannot locate version module "%s"' % version_module
        )

    try:
        return getattr(module, "__version__")
    except AttributeError:
        raise RuntimeError(
            "Cannot find version (__version__) from the version module "
            '"%s"' % version_module
        )


def check_deprecation(expiry=None, current=None, version_module=None):
    if expiry is not None:
        current = get_curr_version(
            current=current, version_module=version_module
        )

        if current >= expiry:
            return True

    return False


def handle_deprecation(handler, func, expiry=None, relocate=None):
    if expiry is None:
        return

    if relocate:
        hints = ' Please use function / method "{relocate}"'.format(
            relocate=relocate
        )
    else:
        hints = ""

    msg = (
        'Function "{func}" is deprecated since version {version}.' "{hints}"
    ).format(func=func.__name__, version=expiry, hints=hints)

    handler = handler or _default_deprecation_error_handler
    handler(msg)


def alert_future_deprecation(handler, func, expiry=None, relocate=None):
    if expiry is None:
        version_msg = "soon"
    else:
        version_msg = "on version {version}".format(version=expiry)

    if relocate:
        hints = ' Please use function / method "{relocate}"'.format(
            relocate=relocate
        )
    else:
        hints = ""

    msg = 'Function "{func}" will be deprecated {version_msg}.{hints}'.format(
        func=func.__name__, version_msg=version_msg, hints=hints
    )

    handler = handler or _default_deprecation_warn_handler
    handler(msg)


def _default_deprecation_error_handler(msg):
    raise RuntimeError(msg)


def _default_deprecation_warn_handler(msg):
    warn(msg, DeprecationWarning)

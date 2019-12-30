"""Main module."""
from datetime import datetime
from importlib import import_module
from warnings import warn


def deprecate(version=None, date=None):
    assert not ((version is not None) and (date is not None)), (
        'Only version "{version}" and date "{date}" should be '
        'provided').format(version=version, date=date)

    def _deprecate(func):
        def wrapper(*args, **kwargs):
            # Check whether the function is deprecated
            is_deprecated = check_deprecation(
                func=func,
                version=version,
                date=date)

            # Throw exception if deprecation
            if is_deprecated:
                handle_deprecation(
                    func=func,
                    version=version,
                    date=date)

            # Run the function
            result = func(*args, **kwargs)

            # Alert the user that the function will be
            # deprecated
            alert_future_deprecation(
                func=func,
                version=version,
                date=date)

            return result

        return wrapper
    return _deprecate


def get_curr_version(func):
    module = ''
    imported_module = func.__module__

    while imported_module:
        tmp_module, _, imported_module = imported_module.partition('.')
        module = module + '.' + tmp_module if module else tmp_module
        m = import_module(module, '__version__')
        try:
            return getattr(m, '__version__')
        except AttributeError:
            continue

    raise RuntimeError((
        'No version can be found in function "{func}" from all the '
        'parent modules "{module}"').format(
            func=func.__name__,
            module=func.__module__))


def get_curr_date():
    return datetime.now()


def check_deprecation(func=None, version=None, date=None, curr_version=None):
    if version is not None:
        curr_version = curr_version or get_curr_version(func)

        if curr_version >= version:
            return True

    if date is not None:
        curr_date = get_curr_date()

        if curr_date >= datetime.strptime(date, '%Y-%m-%d'):
            return True

    return False


def handle_deprecation(func, version=None, date=None):
    err_msg = 'Function "{func}" is deprecated since '.format(
        func=func.__name__)

    if version is not None:
        err_msg += 'version {version}'.format(version=version)

    if date is not None:
        err_msg += 'date {date}'.format(date=date)

    raise RuntimeError(err_msg)


def alert_future_deprecation(func, version=None, date=None):
    warning_msg = 'Function "{func}" will be deprecated on '.format(
        func=func.__name__)

    if version is not None:
        warning_msg += 'version {version}'.format(version=version)

    if date is not None:
        warning_msg += 'date {date}'.format(date=date)

    warn(warning_msg, DeprecationWarning)

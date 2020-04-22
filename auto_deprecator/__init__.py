"""Top-level package for Auto deprecator."""
import argparse
import ast
from io import BytesIO
from importlib import import_module
import logging
from os import environ, walk
from os.path import isfile, join
from tokenize import tokenize, COMMENT
from warnings import warn

LOGGER = logging.getLogger(__name__)


class FunctionStage:
    """Function stage."""

    WARNING = 0
    EXPIRED = 1
    CLEANING = 2


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
            stage = check_stage(
                expiry=expiry, current=current, version_module=version_module
            )

            # Throw exception if deprecation
            if stage != FunctionStage.WARNING:
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
            if stage == FunctionStage.WARNING:
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
        module = import_module(version_module, "")
    except Exception:
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


def check_stage(expiry=None, current=None, version_module=None):
    if expiry is not None:
        current = get_curr_version(
            current=current, version_module=version_module
        )

        if current > expiry:
            return FunctionStage.CLEANING
        elif current == expiry:
            return FunctionStage.EXPIRED
        else:
            return FunctionStage.WARNING

    return FunctionStage.WARNING


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


class SingleFileAutoDeprecator:
    """Auto deprecator.
    """

    def __init__(self, filename, current):
        """Constructor.

        :param filename: `str` File path.
        :param current: `str` Current version.
        """
        self._filename = filename
        self._current = current
        self._deprecate_tokens = []

    @staticmethod
    def is_nestable(body):
        return isinstance(body, (ast.FunctionDef, ast.ClassDef))

    @classmethod
    def check_import_deprecator_exists(cls, tree, last_lineno):
        import_deprecator_lines = []

        for index, body in enumerate(tree.body):
            if (
                isinstance(body, (ast.ImportFrom, ast.Import))
                and hasattr(body, "module")
                and "auto_deprecator" in body.module
            ):
                start_lineno = body.lineno

                if index != len(tree.body) - 1:
                    end_lineno = tree.body[index + 1].lineno
                else:
                    end_lineno = last_lineno

                import_deprecator_lines.append((start_lineno, end_lineno))

        return import_deprecator_lines

    @classmethod
    def check_tree_deprecator_exists(cls, tree):
        for body in tree.body:
            if cls.is_nestable(body):
                if cls.check_tree_deprecator_exists(body):
                    return True

            if cls.get_body_deprecate_deprecator(body):
                return True

        return False

    @classmethod
    def get_body_deprecate_deprecator(cls, body):
        if not hasattr(body, "decorator_list"):
            return None

        deprecate_list = [
            d for d in body.decorator_list
            if hasattr(d, 'func') and d.func.id == "deprecate"
        ]

        if len(deprecate_list) == 0:
            return None

        assert len(deprecate_list) == 1, (
            "More than one deprecate decorator is found "
            'in the function "{func}"'.format(func=body.func.name)
        )

        return deprecate_list[0]

    @classmethod
    def get_function_lineno(cls, body):
        if hasattr(body, "decorator_list") and len(body.decorator_list) > 0:
            return body.decorator_list[0].lineno
        else:
            return body.lineno

    @classmethod
    def get_deprecate_tokens(cls, file_content):
        """Get deprecate tokens.

        :returns: `List[(int, int, str)]` List of tuples of which
            the first and second is the start and end of the line
            number, and the third is the expiry version.
        """
        source_tokens = list(
            tokenize(BytesIO(file_content.encode('utf-8')).readline)
        )

        deprecate_tokens = []

        for (t_type, t_string,
                 (srow, _), (erow, _), _) in source_tokens:
            if t_type != COMMENT:
                continue

            t_string = t_string.lstrip('# ')
            if not t_string.startswith('auto-deprecate:'):
                continue

            expiry = t_string.replace('auto-deprecate:', '').strip(' ')
            assert 'expiry=' in expiry, (
                "Invalid auto-deprecate option (%s)" % expiry
            )

            expiry = expiry.replace('expiry=', '').strip(' ')

            deprecate_tokens.append((srow, erow, expiry))

        return deprecate_tokens

    def get_deprecate_expiry_from_comment(
            self, body, start_lineno, end_lineno):
        """Get deprecate expiry from comment.

        The comment should be like

            # auto-deprecate: expiry=2.0.0

        and located in the function in the first place, after
        the docstring.

        For example,

            def abc():
                \"\"\"Abc.\"\"\"
                # auto-deprecate: expiry=2.0.0
                pass

        is valid, but not

            def abc()
                \"\"\"Abc.\"\"\"
                print('hello world')
                # auto-deprecate: expiry=2.0.0
                pass

        """
        if hasattr(body, 'body'):
            for inner_body in body.body:
                end_lineno = self.get_function_lineno(inner_body)
                if self.is_nestable(inner_body):
                    break

        check_expiry = [
            expiry
            for (srow, erow, expiry) in self._deprecate_tokens
            if srow >= start_lineno and erow < end_lineno
        ]

        if check_expiry:
            return check_expiry[0]

        return None

    def get_body_deprecate_expiry(
            self, body, start_lineno, end_lineno):
        """Get the expiry version of the body.

        :returns: `str` Expiry version.
        """
        if not isinstance(body, (ast.ClassDef, ast.FunctionDef)):
            return None

        deprecate_decorator = self.get_body_deprecate_deprecator(body)

        if deprecate_decorator is not None:
            keywords = {
                k.arg: getattr(k.value, 's', None)
                for k in deprecate_decorator.keywords
            }

            expiry = (
                deprecate_decorator.args[0].value
                if deprecate_decorator.args
                else keywords["expiry"]
            )

            assert expiry is not None, "Expiry cannot be None"

            return expiry

        expiry = self.get_deprecate_expiry_from_comment(
            body, start_lineno, end_lineno
        )

        return expiry

    def find_deprecated_lines(
            self, tree, current, begin_lineno, last_lineno):
        deprecated_lines = []
        deprecated_body = []

        for index, body in enumerate(tree.body):
            # Python 3.8 lineno is on the function rather than the decorator
            start_lineno = self.get_function_lineno(body)

            if index != len(tree.body) - 1:
                end_lineno = self.get_function_lineno(
                    tree.body[index + 1]
                )
            else:
                end_lineno = last_lineno

            expiry = self.get_body_deprecate_expiry(
                body, start_lineno, end_lineno
            )

            assert current is not None, "Current version must be provided"

            stage = check_stage(expiry=expiry, current=current)

            # Loop into the body only if it can contain inner
            # function / inner class
            if self.is_nestable(body):
                deprecated_lines += self.find_deprecated_lines(
                    body, current, start_lineno, last_lineno
                )

                if len(body.body) == 0:
                    deprecated_body.append(body)

            if stage != FunctionStage.CLEANING:
                continue

            deprecated_lines.append((start_lineno, end_lineno))
            deprecated_body.append(body)

        # Remove the deprecated body from the tree
        for body in deprecated_body:
            tree.body.remove(body)

        # If no element is found in the body, remove the whole tree
        if len(tree.body) == 0:
            deprecated_lines = [(begin_lineno, last_lineno)]

        return deprecated_lines

    def run(self):
        LOGGER.info('Deprecating the file %s', self._filename)

        # Read file stream
        filestream = open(self._filename, "r").readlines()
        file_content = "".join(filestream)
        tree = ast.parse(file_content)

        # Get the deprecate tokens
        self._deprecate_tokens = self.get_deprecate_tokens(
            file_content
        )

        # Check whether deprecate is included
        deprecator_import_lines = self.check_import_deprecator_exists(
            tree, len(filestream) + 1
        )

        # Store the deprecated funcion line numbers. The tuple
        # is combined by the start and end line index
        deprecated_lines = self.find_deprecated_lines(
            tree, self._current, 1, len(filestream) + 1
        )

        if not deprecated_lines:
            return False

        # Remove the import of the auto_deprecator if no more
        # deprecate decorator is found
        if not self.check_tree_deprecator_exists(tree):
            deprecated_lines += deprecator_import_lines

        # Remove the deprecated functions from backward
        deprecated_lines = sorted(
            deprecated_lines, key=lambda x: x[0], reverse=True
        )

        for start_lineno, end_lineno in deprecated_lines:
            filestream = (
                filestream[: start_lineno - 1] + filestream[end_lineno - 1 :]
            )

        # Remove the redundant newline
        filestream = "".join(filestream).rstrip()

        # Write back the file
        open(self._filename, "w+").write(filestream)

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Automatical removal of deprecated source code."
    )
    parser.add_argument(
        "path", type=str, help="The source code path.")
    parser.add_argument(
        "--version", dest="current", type=str, help="Current package version."
    )
    parser.add_argument(
        "--debug", dest="debug", help='Debug mode', action='store_true',
    )
    args = parser.parse_args()

    # Set up logger
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)-15s %(message)s')

    # Get the argument values
    path = args.path
    current = args.current
    assert current, "Current version is not provided"

    if isfile(path):
        SingleFileAutoDeprecator(filename=path, current=current).run()
    else:
        for root, subdirs, files in walk(path):
            LOGGER.debug('Walk through root %s with files %s', root, files)
            for python_file in files:
                if python_file[-3:] != '.py':
                    continue

                python_file = join(root, python_file)
                SingleFileAutoDeprecator(
                    filename=python_file,
                    current=current
                ).run()


if __name__ == '__main__':
    main()

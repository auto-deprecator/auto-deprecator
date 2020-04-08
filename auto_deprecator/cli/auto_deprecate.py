import argparse
import ast
import logging
from os import walk
from os.path import isfile

try:
    from auto_deprecator.deprecate import check_deprecation
except ImportError:
    from os.path import dirname, join
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location(
        'deprecate', join(dirname(__file__), '..', 'deprecate.py')
    )
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    check_deprecation = module.check_deprecation

LOGGER = logging.getLogger(__name__)


def check_import_deprecator_exists(tree, last_lineno):
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


def check_body_deprecator_exists(body):
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


def check_tree_deprecator_exists(tree):
    for body in tree.body:
        if isinstance(body, ast.ClassDef):
            if check_tree_deprecator_exists(body):
                return True

        if check_body_deprecator_exists(body):
            return True

    return False


def find_deprecated_lines(tree, current, begin_lineno, last_lineno):
    def get_function_lineno(body):
        if hasattr(body, "decorator_list") and len(body.decorator_list) > 0:
            return body.decorator_list[0].lineno
        else:
            return body.lineno

    deprecated_lines = []
    deprecated_body = []

    for index, body in enumerate(tree.body):
        # Python 3.8 lineno is on the function rather than the decorator
        start_lineno = get_function_lineno(body)

        if index != len(tree.body) - 1:
            end_lineno = get_function_lineno(tree.body[index + 1])
        else:
            end_lineno = last_lineno

        if isinstance(body, ast.ClassDef):
            deprecated_lines += find_deprecated_lines(
                body, current, start_lineno, last_lineno
            )

            if len(body.body) == 0:
                deprecated_body.append(body)

        deprecate_decorator = check_body_deprecator_exists(body)

        if deprecate_decorator is None:
            continue

        keywords = {
            k.arg: getattr(k.value, 's', None)
            for k in deprecate_decorator.keywords
        }

        expiry = (
            deprecate_decorator.args[0].value
            if deprecate_decorator.args
            else keywords["expiry"]
        )

        if current is None:
            current = (
                deprecate_decorator.args[1].value
                if len(deprecate_decorator.args) > 1
                else keywords["current"]
            )

        is_deprecated = check_deprecation(expiry=expiry, current=current)

        if not is_deprecated:
            continue

        # Readjust the start lineno from the decorator
        start_lineno = body.decorator_list[0].lineno

        deprecated_lines.append((start_lineno, end_lineno))
        deprecated_body.append(body)

    # Remove the deprecated body from the tree
    for body in deprecated_body:
        tree.body.remove(body)

    # If no element is found in the body, remove the whole tree
    if len(tree.body) == 0:
        deprecated_lines = [(begin_lineno, last_lineno)]

    return deprecated_lines


def deprecate_single_file(filename, current=None):
    LOGGER.info('Deprecating the file %s', filename)

    # Read file stream
    filestream = open(filename, "r").readlines()
    tree = ast.parse("".join(filestream))

    # Check whether deprecate is included
    deprecator_import_lines = check_import_deprecator_exists(
        tree, len(filestream) + 1
    )

    if not deprecator_import_lines:
        return False

    # Store the deprecated funcion line numbers. The tuple
    # is combined by the start and end line index
    deprecated_lines = find_deprecated_lines(
        tree, current, 1, len(filestream) + 1
    )

    if not deprecated_lines:
        return False

    # Remove the import of the auto_deprecator if no more
    # deprecate decorator is found
    if not check_tree_deprecator_exists(tree):
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
    open(filename, "w+").write(filestream)

    return True


def deprecate_directory(path, current):
    for root, subdirs, files in walk(path):
        LOGGER.debug('Walk through root %s with files %s', root, files)
        for python_file in files:
            if python_file[-3:] != '.py':
                continue

            python_file = join(root, python_file)
            deprecate_single_file(python_file, current)


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
        deprecate_single_file(path, current)
    else:
        deprecate_directory(path, current)


if __name__ == '__main__':
    main()

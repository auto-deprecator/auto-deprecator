import ast

import click

from auto_deprecator.deprecate import check_deprecation


def check_deprecator_exists(tree):
    for body in tree.body:
        if (isinstance(body, (ast.ImportFrom, ast.Import)) and
                body.module == 'auto_deprecator'):
            return True

    return False

def deprecate_single_file(filename, curr_version=None):
    tree = ast.parse(open(filename, 'r').read())

    # Check whether deprecate is included
    deprecator_exists = check_deprecator_exists(tree)

    if not deprecator_exists:
        return False

    # Store the deprecated funcion line numbers. The tuple
    # is combined by the start and end line index
    deprecated_lines = []

    # Read file stream only when if deprecated function
    # is needed to be removed.
    filestream = None

    # Find the decorator deprecate and locate the line
    for index, body in enumerate(tree.body):
        if not hasattr(body, 'decorator_list'):
            continue

        deprecate_list = [d for d in body.decorator_list
                          if d.func.id == 'deprecate']

        if len(deprecate_list) == 0:
            continue

        func_name = body.name

        assert len(deprecate_list) == 1, (
            'More than one deprecate decorator is found '
            'in the function "{func}"'.format(
                func=func_name))

        deprecate_args = {
            kw.arg: kw.value.s
            for kw in deprecate_list[0].keywords
        }

        is_deprecated = check_deprecation(
            curr_version=curr_version,
            **deprecate_args)

        if not is_deprecated:
            continue

        if filestream is None:
            filestream = open(filename, 'r').readlines()

        start_lineno = body.lineno

        if index != len(tree.body) - 1:
            end_lineno = tree.body[index + 1].lineno
        else:
            end_lineno = len(filestream) + 1

        deprecated_lines.append((start_lineno, end_lineno))

    # Remove the deprecated functions from backward
    deprecated_lines = deprecated_lines[::-1]

    for start_lineno, end_lineno in deprecated_lines:
        filestream = filestream[:start_lineno-1] + filestream[end_lineno-1:]

    # Remove the redundant newline
    filestream = ''.join(filestream).rstrip()

    # Write back the file
    open(filename, 'w+').write(filestream)


@click.command()
@click.option(
    '--filename',
    default=None,
    help='Python file name which includes the deprecated functions')
@click.option(
    '--curr-version',
    default=None,
    help='Current file or package version. If not provided, the '
         'current versions is derived from the package.')
def main(filename, curr_version):
    if filename is not None:
        deprecate_single_file(filename, curr_version)

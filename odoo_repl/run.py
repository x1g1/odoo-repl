# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import shlex
import os
import sys

import odoo_repl

from odoo_repl.imports import t


def main(argv=sys.argv[1:]):
    # type: (t.Sequence[str]) -> int
    # TODO: flags for disabling features
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--database", type=str, default=None, help="Database name"
    )
    parser.add_argument(
        "-c", "--command", type=str, default=None, help="Initial command to execute"
    )
    parser.add_argument(
        "--ipython",
        action="store_true",
        default=False,
        help="Use IPython instead of the default REPL",
    )
    parser.add_argument(
        "--interpreter",
        type=str,
        default=None,
        help="Specify a different interpreter to use",
    )
    parser.add_argument(
        "-a",
        "--args",
        type=str,
        default=None,
        help="Extra flags to pass to the interpreter",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    parser.add_argument(
        "--bg-editor",
        action="store_true",
        help="Allow editors to run in the background",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Immediately quit odoo-repl after starting",
    )
    parser.add_argument(
        "directory", type=str, default=".", nargs="?", help="Buildout directory to use"
    )
    parser.add_argument(
        "extra_args", nargs="*", help="Extra configuration arguments you'd pass to odoo"
    )
    args = parser.parse_args(argv)

    if args.ipython and args.interpreter:
        print("--ipython and --interpreter can't be used together")
        return 1

    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        print("Directory {!r} does not exist".format(directory))
        return 1

    executable = os.path.join(directory, "bin/python_odoo")

    if not os.path.isfile(executable):
        print("{!r} is not a buildout directory".format(directory))
        return 1

    with open(executable) as f:
        line = f.readline().strip()
        assert line.startswith("#!")
        interp = line[2:].strip()
        py2 = "python2" in interp

    if args.interpreter:
        interp = args.interpreter

    if os.environ.get("PYTHONSTARTUP"):
        # $PYTHONSTARTUP isn't read when executing a file, but if you have one
        # then you probably want to use it when running this script, so load
        # it manually
        if py2:
            cmd = """with open({!r}) as f:
    exec f.read()
""".format(
                os.environ["PYTHONSTARTUP"]
            )
        else:
            cmd = """with open({!r}) as f:
    exec(f.read(), globals(), locals())
""".format(
                os.environ["PYTHONSTARTUP"]
            )
    else:
        cmd = ""

    cmd += """import sys
sys.path.append({odoo_repl_path!r})
import odoo_repl
sys.path.pop()
odoo_repl.parse_config(['-c', session.openerp_config_file] + {extra_args!r})
session.open(db={database!r})
odoo_repl.enable(session.env, __name__, with_color={color!r}, bg_editor={bg_editor!r})
""".format(
        database=args.database,
        odoo_repl_path=os.path.dirname(
            os.path.dirname(odoo_repl.__file__)
        ),  # Might be fragile
        color=not (args.no_color or os.environ.get("NO_COLOR")),
        bg_editor=args.bg_editor,
        extra_args=args.extra_args,
    )

    if args.command is not None:
        cmd += args.command

    # python_odoo has a -i flag for an interactive mode, but that's not great
    # It doesn't enable Python 3's readline enhancements, for example
    # So use Python's own -i flag instead
    if args.ipython:
        original_interp = interp
        interp = "ipython" if py2 else "ipython3"
        # Detect IPython if it's installed in the same virtualenv as Odoo
        maybe_interp = os.path.join(os.path.dirname(original_interp), interp)
        if os.path.isfile(maybe_interp):
            interp = maybe_interp
        argv = [interp, "--no-banner"]
    else:
        argv = [interp]
    if not args.no_interactive:
        argv.append("-i")
    if args.args:
        argv.extend(shlex.split(args.args))
    argv.extend(["--", executable, "-c", cmd])
    os.execvp(interp, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

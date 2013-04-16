#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
usage: oyakata [--version] [-f procfile|--procfile procfile] [-r root|--root root] <command> [<args>...]

Options:

    -h --help                           show this help
    --version                           show version
    -f procfile, --procfile procfile    Procfile
    -r root, --root, root               Application Root

"""

import sys
from . import __version__
from oyakata.commands import get_commands
from docopt import docopt


class OyakataCli(object):
    def __init__(self, argv=None):

        self.commands = get_commands()
        version_str = "oyakata version %s" % __version__
        doc_str = "%s%s" % (__doc__, self._commands_help())
        self.args = docopt(doc_str, argv=argv, version=version_str, options_first=True)

    def run(self):
        cmdname = self.args['<command>']
        if cmdname.lower() == "help":
            self.display_help()
        elif cmdname not in self.commands:
            print "Unknown command: %r" % cmdname
            sys.exit(1)
        cmd = self.commands[cmdname]
        cmd_argv = [cmdname] + self.args['<args>']
        cmd_args = docopt(cmd.__doc__, argv=cmd_argv)

        try:
            cmd.run(cmd_args)
        except RuntimeError, e:
            sys.stderr.write('%s\n' % str(e))
            sys.exit(1)
        except Exception, e:
            import traceback
            print traceback.format_exc()
            sys.stderr.write('%s\n' % str(e))
            sys.exit(1)
        sys.exit(0)

    def display_help(self):
        u"""
        ヘルプ表示
        """
        return

    def _commands_help(self):
        u"""
        コマンドのヘルプを拾い上げて結合する。
        """
        commands = [name for name in self.commands] + ["help"]
        max_len = len(max(commands, key=len))
        output = ["Commands:",
                  " "]
        for name in commands:
            if name == "help":
                desc = "Get help on a command"
                output.append("    %-*s\t%s" % (max_len, name, desc))
            else:
                cmd = self.commands[name]
                output.append("    %-*s\t%s" % (max_len, name, cmd.short_descr))
        output.append("    ")
        return "\n".join(output)


def main():
    cli = OyakataCli()
    cli.run()


if __name__ == '__main__':
    main()

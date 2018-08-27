from sys import argv, stdin
import argparse

from MiniTemple import render_file, render_text

def isint(i):
    try:
        int(i)
        return True
    except ValueError:
        return False

def isfloat(f):
    try:
        float(f)
        return True
    except ValueError:
        return False

parser = argparse.ArgumentParser(
        description='Use the MiniTemple templating engine'
)

parser.add_argument('filename', metavar='FILENAME')

parser.add_argument('--tags', '-t', action='store', nargs=2, default=None)

parser.add_argument('--output', '-o', action='store', default='-')

parser.add_argument('--scope', '-s', action='append', nargs=2)
parser.add_argument('--debug', '-d', action='store_true', default=False)


options = parser.parse_args(argv[1:])
outfilename = options.output

filename = options.filename

scope = {}

if options.scope:
    for key, value in options.scope:
        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif value == 'None':
            value = None
        elif isint(value):
            value = int(value)
        elif isfloat(value):
            value = float(value)
        scope[key] = value


opt_d = {}
if options.tags:
    opt_d = options.tags

if options.debug:
    opt_d['debug'] = True

if outfilename == '-':
    if filename == '-':
        print(render_text(stdin.read(), scope, **opt_d), end='')
    else:
        print(render_file(filename, scope, **opt_d), end='')
else:
    with open(outfilename, 'w') as fout:
        if filename == '-':
            print(render_text(stdin.read(), scope, **opt_d), end='', file=fout)
        else:
            print(render_file(filename, scope, **opt_d), end='', file=fout)

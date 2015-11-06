import sys

def debug(*args):
    for arg in args:
        sys.stdout.write(str(arg))
    if len(args) > 0:
        sys.stdout.write('\n')

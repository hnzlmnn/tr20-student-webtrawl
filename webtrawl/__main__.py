import argparse
import os
import sys

from webtrawl import application

parser = argparse.ArgumentParser(prog="python -m webtral", description='WebTrawl')
parser.add_argument('-l', '--liberal', type=bool, default=False, nargs="?", const=True,
                    help='Liberally parse requests (non-strict) default: strict')
args = parser.parse_args()


application(os.environ, sys.stdin.buffer, sys.stdout.buffer, strict=not args.liberal)

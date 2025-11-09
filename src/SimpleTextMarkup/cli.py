import sys
from .converter import *

from argparse import ArgumentParser

def gen_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('input', type=str, nargs='?', default=None, help='Input file - if not given, reads from stdin')
    parser.add_argument('output', type=str, nargs='?', default=None, help='Output file - if not given, writes to stdout')
    return parser

def main():
    args = gen_arg_parser().parse_args()
    input = args.input
    output = args.output
    if input is None or input == '-':
        input = sys.stdin
    if output is None or output == '-':
        output = sys.stdout

    stm_convert_to_file(input, output)

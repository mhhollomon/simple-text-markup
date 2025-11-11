import sys
from .converter import *

from argparse import ArgumentParser

def gen_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('input', type=str, nargs='?', default=None,
                        help='Input file. If not given, or is \'-\', reads from stdin')
    parser.add_argument('output', type=str, nargs='?', default=None,
                        help='Output file . If not given, or is \'-\', writes to stdout')

    # Group fr classes
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--use-classes', action='store_true', dest='use_classes',
                       help='Include a class name in each generated tag')
    group.add_argument('--no-use-classes', action='store_false', dest='use_classes',
                       help='Do not include a class name in each generated tag')
    return parser

def main():
    args = gen_arg_parser().parse_args()
    input = args.input
    output = args.output
    if input is None or input == '-':
        input = sys.stdin
    if output is None or output == '-':
        output = sys.stdout

    options = {}
    if args.use_classes:
        options['use_classes'] = args.use_classes

    stm_convert_to_file(input, output, options)

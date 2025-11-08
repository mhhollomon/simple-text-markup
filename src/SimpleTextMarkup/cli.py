import sys
from .converter import *

from argparse import ArgumentParser

def gen_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('input', type=str, help='Input file')
    parser.add_argument('output', type=str, help='Output file')
    return parser

def main():
    args = gen_arg_parser().parse_args()
    input = args.input
    output = args.output
    if not args.input :
        input = sys.stdin
    if not args.output :
        output = sys.stdout

    stm_convert_to_file(input, output)

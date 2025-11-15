from typing import Dict
from .impl_ import *
import regex as re


def default_options() -> Dict[str, Option]:
    return {
        'use_classes' : BooleanOption('use_classes', False, OptionSource.DEFAULT),
    }

######################################################################
# STMConverter
######################################################################
class STMConverter(ParserProxy):
    def __init__(self, src : LineSrc,  options : dict[str, str] | None = None):
        self.stack : list[Context] = []
        self.output = ''
        self.src = src

        self.options = default_options()
        if options is not None:
            for k, v in options.items():
                if k not in self.options:
                    raise Exception(f"Unknown option: {k}")
                self.options[k].set_value(v, OptionSource.CONFIG)

        print(f"--- STMConverter: Options: {self.options}")


    #### ParserProxy overrides
    def get_class_name(self, tag : str) -> str:
        if not self.options['use_classes'].get_value():
            return ''
        if tag == 'span':
            return ''
        return f'stm-{tag}'

    def _inner_context(self) -> Context:
        return self.stack[-1]

    def _in_context(self) -> bool:
        return len(self.stack) > 0

    def _push_context(self, data : FormatterBase | Context, opener : str | None = None) -> Context:
        if isinstance(data, FormatterBase):
            if opener is None:
                raise Exception("Context created from Formatter must have an opener")
            ctx = Context.from_formatter(data, opener)
        else :
            ctx = data
        self.stack.append(ctx)
        return ctx

    def _pop_context(self) -> Context:
        return self.stack.pop()

    def _add_output(self, line : str):
        if self._in_context():
            self._inner_context().add_to_buffer(line)
        else:
            self.output += line

    def _skip_blanks_lines(self) -> bool:
        while True :
            line = self.src.get_next()
            if line is None:
                return False
            if line.strip() == '':
                continue
            self.src.push_back(line)
            return True

    def parseConfigs(self) -> bool:

        if not self._skip_blanks_lines() :
            return False

        line : str = self.src.get_next() # type: ignore

        if not line.startswith('%config '):
            self.src.push_back(line)
            return False

        line = line[len('%config '):].strip()

        for opt in re.findall(r'(\w+)=(.*)', line):
            if opt[0] not in self.options:
                raise Exception(f"Unknown option: {opt[0]}")
            self.options[opt[0]].set_value(opt[1], OptionSource.FILE)

        return True

    def parseBlock(self) -> bool:
        if not self._skip_blanks_lines() :
            return False

        line : str = self.src.get_next() # type: ignore

        return False


    def convert(self) -> str:

        if self.src is None:
            raise Exception("No input")

        while not self.src.is_at_end():
            while self.parseConfigs() :
                pass

            self.parseBlock()

        return self.output

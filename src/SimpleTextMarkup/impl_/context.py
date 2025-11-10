
from enum import Enum, auto
from dataclasses import dataclass

from .formatter import FormatterBase, FormatterType


@dataclass
class Context:
    name : str
    buffer : str
    ftype : FormatterType
    fmt : FormatterBase
    opener : str

    def add_to_buffer(self, line):
        self.buffer += line

    @staticmethod
    def from_formatter(formatter : FormatterBase, opener : str) -> 'Context':
        return Context(
            fmt=formatter,
            name=formatter.name,
            ftype=formatter.ftype,
            buffer='',
            opener=opener
        )



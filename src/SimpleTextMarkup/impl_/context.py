
from enum import Enum, auto
from dataclasses import dataclass

from .formatter import Formatter

class context_type(Enum) :
    FORMATTER = auto()
    DIRECTIVE = auto()


@dataclass
class Context:
    name : str
    buffer : str
    ctype : context_type
    fmt : Formatter
    opener : str

    def add_to_buffer(self, line):
        self.buffer += line

    @staticmethod
    def from_formatter(formatter : Formatter, opener : str) -> 'Context':
        return Context(name=formatter.name, buffer='',
                        ctype=context_type.FORMATTER, 
                        fmt=formatter, opener=opener
                        )
    


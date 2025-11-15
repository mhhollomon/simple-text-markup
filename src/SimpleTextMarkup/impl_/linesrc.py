from pathlib import Path
from typing import Any, List, TextIO


class LineSrc:
    def __init__(self, input : str | Path | TextIO | List[str]):
        self.pushback : List[str] = []
        self.data : List[str] = []

        self.index = 0
        self.io : Any = None
        self.at_end = False

        if isinstance(input, str):
            self.data = input.splitlines()
        elif isinstance(input, Path):
            self.data = input.read_text().splitlines()
        elif isinstance(input, list):
            self.data = input
        else :
            self.io = input

    def get_next(self) -> str | None:
        if self.at_end:
            return None

        if len(self.pushback) > 0:
            return self.pushback.pop()

        if self.io is not None:
            line = self.io.readline()
            if line == '':
                self.at_end = True
                return None
            elif line[-1] == '\n':
                return line[:-1] + ' '
            else :
                return line + ' '

        if self.index >= len(self.data):
            self.at_end = True
            return None
        self.index += 1
        return self.data[self.index - 1] + ' '

    def push_back(self, line : str):
        self.at_end = False
        self.pushback.append(line)

    def peek(self) -> str | None:

        line = self.get_next()
        if line is not None:
            self.push_back(line)
        return line


    def is_blank(self) -> bool:
        l = self.peek()
        return l is None or l.strip() == ''

    def is_at_end(self) -> bool:
        return self.at_end

from pathlib import Path
from typing import Any, List, TextIO


class LineSrc:
    def __init__(self, input : str | Path | TextIO | List[str]):
        print(f"--- LineSrc:Input type: {type(input)}")
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
            print("--- LineSrc: get_next() : End of input")
            return None

        if len(self.pushback) > 0:
            print("--- LineSrc: get_next() : Returning pushed back line")
            return self.pushback.pop(0)

        if self.io is not None:
            line = self.io.readline()
            if line == '':
                self.at_end = True
                print("--- LineSrc: get_next() : IO returned EOF")
                return None
            elif line[-1] == '\n':
                print("--- LineSrc: get_next() : IO returning chomped line")
                return line[:-1] + ' '
            else :
                print("--- LineSrc: get_next() : IO returning line")
                return line + ' '

        if self.index >= len(self.data):
            print("--- LineSrc: Index - End of input")
            self.at_end = True
            return None
        self.index += 1
        print(f"--- LineSrc: get_next() : Returning line '{self.data[self.index - 1]}'")
        return self.data[self.index - 1] + ' '

    def push_back(self, line : str):
        print("--- LineSrc: push_back()")
        self.at_end = False
        self.pushback.append(line)

    def peek(self) -> str | None:
        if self.at_end:
            return None

        if len(self.pushback) > 0:
            return self.pushback[0]

        if self.index >= len(self.data):
            return None

        return self.data[self.index] + ' '

    def is_blank(self) -> bool:
        if self.at_end:
            return True

        l = self.peek()
        return l is None or l.strip() == ''

    def is_at_end(self) -> bool:
        return self.at_end

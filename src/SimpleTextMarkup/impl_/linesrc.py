from pathlib import Path
from typing import List, TextIO


class LineSrc:
    def __init__(self, input : str | Path | TextIO | List[str]):
        print(f"--- LineSrc:Input type: {type(input)}")
        self.pushback : List[str] = []

        self.index = 0
        if isinstance(input, str):
            self.data = input.splitlines()
        elif isinstance(input, Path):
            self.data = input.read_text().splitlines()
        elif isinstance(input, list):
            self.data = input
        else :
            self.data = [x[:-1] if x[-1] == '\n' else x for x in input.readlines()]

    def get_next(self) -> str | None:
        if len(self.pushback) > 0:
            return self.pushback.pop(0)

        if self.index >= len(self.data):
            print("--- LineSrc:End of input")
            return None
        self.index += 1
        print(f"--- LineSrc: {self.data[self.index - 1]}")
        return self.data[self.index - 1] + ' '

    def push_back(self, line : str):
        self.pushback.append(line)

    def peek(self) -> str | None:
        if len(self.pushback) > 0:
            return self.pushback[0]
        if self.index >= len(self.data):
            return None
        return self.data[self.index] + ' '

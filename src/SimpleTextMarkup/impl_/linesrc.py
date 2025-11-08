from pathlib import Path
from typing import List, TextIO


class LineSrc:
    def __init__(self, input : str | Path | TextIO | List[str]):
        print(f"--- LineSrc:Input type: {type(input)}")
        self.index = 0
        if isinstance(input, str):
            self.data = input.splitlines()
        elif isinstance(input, Path):
            self.data = input.read_text().splitlines()
        elif isinstance(input, list):
            self.data = input
        else :
            self.data = [x[:-1] if x[-1] == '\n' else x for x in input.readlines()]

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        self.index += 1
        return self.data[self.index - 1] + ' '

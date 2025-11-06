from pathlib import Path


class LineSrc:
    def __init__(self, input : str | Path):
        self.index = 0
        if isinstance(input, str):
            self.data = input.splitlines()
        elif isinstance(input, Path):
            self.data = input.read_text().splitlines()

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        self.index += 1
        return self.data[self.index - 1] + ' '

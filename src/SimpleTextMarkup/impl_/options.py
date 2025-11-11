from abc import ABC, abstractmethod
import regex as re
from enum import Enum
from typing import Any


class OptionSource(Enum):
    DEFAULT = 1
    FILE    = 2
    CONFIG  = 3

class Option(ABC) :
    def __init__(self, name : str, value :str, source : OptionSource = OptionSource.DEFAULT):
        self.name = name
        self.value = value
        self.source = source

    @abstractmethod
    def get_value(self) -> Any:
        pass

    def set_value(self, value : Any, source : OptionSource = OptionSource.DEFAULT):
        print(f"-- Option.set_value({self.name}, {value}, {source})")
        if source.value  >= self.source.value:
            print(f"-- Option.set_value({self.name}, {value}, {source}) : Setting")
            self.value = str(value)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name}={self.value}, source={self.source})"

    def __repr__(self) -> str:
        return self.__str__()

class BooleanOption(Option):
    def __init__(self, name : str, value : bool, source : OptionSource = OptionSource.DEFAULT):
        super().__init__(name, "TRUE" if value else "FALSE", source)

    def get_value(self) -> bool:
        return self.value == "TRUE"

    def set_value(self, value : bool | str, source : OptionSource = OptionSource.DEFAULT):
        if isinstance(value, str):
            if (re.match(r"^(TRUE|ON|YES)$", value, re.IGNORECASE)):
                value = True
            else:
                value = False
        super().set_value("TRUE" if value else "FALSE", source)

class StringOption(Option):
    def __init__(self, name : str, value : str, source : OptionSource = OptionSource.DEFAULT):
        super().__init__(name, value, source)

    def get_value(self) -> str:
        return self.value

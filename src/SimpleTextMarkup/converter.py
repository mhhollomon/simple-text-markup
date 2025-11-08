from pathlib import Path
from .convert import STMConverter
from .impl_ import LineSrc

from typing import List, TextIO

def stm_convert(input : str | Path | TextIO | List[str]) -> str:
    src = LineSrc(input)
    return STMConverter(src).convert()

def stm_convert_to_file(input : str | Path | TextIO | List[str], output : str | Path | TextIO) :

    x = stm_convert(input)
    if isinstance(output, str) or isinstance(output, Path):
        with open(output, 'w') as f:
            f.write(x)
    else :
        output.write(x)

from pathlib import Path
from .convert import STMConverter

from typing import List, TextIO

def stm_convert(input : str | Path | TextIO | List[str]) -> str:
    return STMConverter().convert(input)

def stm_convert_to_file(input : str | Path | TextIO | List[str], output : str | Path | TextIO) :

    x = stm_convert(input)
    if isinstance(output, str) or isinstance(output, Path):
        with open(output, 'w') as f:
            f.write(x)
    else :
        output.write(x)
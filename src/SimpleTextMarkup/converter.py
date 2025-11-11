from pathlib import Path
from .convert import STMConverter
from .impl_ import LineSrc

from typing import List, TextIO

def stm_convert(input : str | Path | TextIO | List[str], options : dict[str, str] | None = None) -> str:
    src = LineSrc(input)
    return STMConverter(src, options=options).convert()

def stm_convert_to_file(input : str | Path | TextIO | List[str], output : str | Path | TextIO, options : dict[str, str] | None = None):

    x = stm_convert(input, options=options)
    if isinstance(output, str) or isinstance(output, Path):
        with open(output, 'w') as f:
            f.write(x)
    else :
        output.write(x)

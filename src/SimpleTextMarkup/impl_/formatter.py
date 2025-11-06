from dataclasses import dataclass
from typing import Callable
import regex as re


@dataclass
class Formatter:
    name : str
    group : str
    tag : str
    starter : str 
    needs_space : bool = False
    allows_nesting : bool = True
    terminator : str = ''
    tbel : bool = True
    handler : Callable[[str, str],str] | None = None
    one_shot : bool = False

    def start_re(self) -> str :
        retval = re.escape(self.starter)
        if self.needs_space:
            retval = r'(?<=\s|^)' + retval
        else :
            # make sure there isn't a blackslash preceeding the starter
            retval = r'(?<!\\)' + retval
        return retval
    
    def end_re(self) -> str :
        retval = re.escape(self.terminator)
        if self.needs_space:
            retval = r'(?=\s|$)' + retval
        else :
            # make sure there isn't a blackslash preceeding the terminator
            retval = r'(?<!\\)' + retval
        return retval
    
    def build_output(self, input : str, opener : str ) -> str:
        if self.handler is not None:
            return self.handler(input, opener)
        else:
            return f"<{self.tag}>{input}</{self.tag}>"

class ClassNameFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = self._handler
        self.terminator = '>'

    def _handler(self, input : str, opener : str) -> str:
        class_string = ''
        equal = opener.find('=')
        if equal != -1:
            class_name = opener[equal+1 : -1].strip()
            if class_name != '':
                class_string = f' class=\"{class_name}\"'

        class_name = opener[opener.find('=')+1 : -1]
        return f"<{self.tag}{class_string}>{input}</{self.tag}>"
    
    def start_re(self) -> str:
        """Need the special characters to be special"""

        return f"\\$<{self.starter}(=[^:]*)?:"
    
class LinkFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = self._handler
        self.one_shot = True


    def _handler(self, _ : str, opener : str) -> str:
        title_index = opener.find(']')
        if title_index != -1:
            title = opener[1:title_index]
        else :
            title = opener[1:-1]
        href = opener[title_index+2:-1]
        return f"<a href=\"{href}\">{title}</a>"
    
    def start_re(self) -> str:
        return r"\[[^\]]+\]\([^)]+\)"

Formatters : list[Formatter] = [
    Formatter(
        name='bold',
        group = 'bold',
        tag = 'strong',
        allows_nesting = True,
        starter = '**',
        terminator = '**'
    ),
    ClassNameFormatter(
        name='bold_class',
        group = 'bold',
        tag = 'strong',
        allows_nesting = True,
        starter = 'b',
    ),
    Formatter(
        name='italic',
        group = 'italic',
        tag = 'em',
        allows_nesting = True,
        starter = '~~',
        terminator = '~~'
    ),
    ClassNameFormatter(
        name='italic_class',
        group = 'italic',
        tag = 'em',
        allows_nesting = True,
        starter = 'i',
    ),
    Formatter(
        name='code',
        group = 'code',
        tag = 'code',
        allows_nesting = False,
        starter = '``',
        terminator = '``'
    ),
    ClassNameFormatter(
        name='code_class',
        group = 'code',
        tag = 'code',
        allows_nesting = True,
        starter = 'code',
    ),
    ClassNameFormatter(
        name='span_class',
        group = 'span',
        tag = 'span',
        allows_nesting = True,
        starter = 'span',
    ),
    LinkFormatter(
        name='link',
        group = 'link',
        tag = 'a',
        allows_nesting = False,
        starter = '[',
    )
]

def __null_handler(x, y):
    raise Exception(f"Null formatter: {x}, {y}")

NULLFORMATTER = Formatter(
    name='null',
    group = 'null',
    tag = 'null',
    handler = __null_handler,
    allows_nesting = False,
    starter = ''
)

PARA_FORMATTER = Formatter(
    name='paragraph',
    group = 'para',
    tag = 'p',
    allows_nesting = True,
    starter = ''
)


from dataclasses import dataclass
from enum import Enum, auto
import regex as re


class FormatterType(Enum):
    UNKNOWN  = auto()
    EMBEDDED = auto()
    ONELINE  = auto()
    BLOCK    = auto()

class FormatterBase:
    def __init__(self, name : str, group : str, ftype : FormatterType) -> None:
        self.name = name
        self.group = group
        self.ftype = ftype

    def start_re(self) -> str:
        raise NotImplementedError

    def end_re(self) -> str:
        raise NotImplementedError

    def build_output(self, input : str, opener : str) -> str:
        raise NotImplementedError

    def nestable(self) -> bool:
        raise NotImplementedError

    def self_closing(self) -> bool:
        raise NotImplementedError

@dataclass
class EmbedFormatter(FormatterBase):
    def __init__(self,
                 name : str, group : str, tag : str, starter : str,
                 terminator : str = '', allows_nesting : bool = True,
                 one_shot : bool = False):
        super().__init__(name, group, FormatterType.EMBEDDED)
        self.tag = tag
        self.starter = starter
        self.terminator = terminator
        self.allows_nesting = allows_nesting
        self.one_shot = one_shot


    def nestable(self) -> bool:
        return self.allows_nesting

    def self_closing(self) -> bool:
        return self.one_shot

    def start_re(self) -> str :
        retval = re.escape(self.starter)
        # make sure there isn't a blackslash preceeding the starter
        retval = r'(?<!\\)' + retval
        return retval

    def end_re(self) -> str :
        retval = re.escape(self.terminator)
        # make sure there isn't a blackslash preceeding the terminator
        retval = r'(?<!\\)' + retval
        return retval

    def build_output(self, input : str, opener : str ) -> str:
        return f"<{self.tag}>{input}</{self.tag}>"

class ClassNameFormatter(EmbedFormatter):
    def __init__(self,
                 name : str, group : str, tag : str,
                 starter : str, allows_nesting : bool = True,
                 one_shot : bool = False):
        super().__init__(name, group, tag, starter, '>', allows_nesting, one_shot)

    def build_output(self, input : str, opener : str) -> str:
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

class LinkFormatter(EmbedFormatter):
    def __init__(self, *args, **kwargs):
        kwargs['one_shot'] = True
        super().__init__(*args, **kwargs)


    def build_output(self, _ : str, opener : str) -> str:
        title_index = opener.find(']')
        if title_index != -1:
            title = opener[1:title_index]
        else :
            title = opener[1:-1]
        href = opener[title_index+2:-1]
        return f"<a href=\"{href}\">{title}</a>"

    def start_re(self) -> str:
        return r"\[[^\]]+\]\([^)]+\)"

def get_formatters() -> list[FormatterBase]:
    return [
        EmbedFormatter(
            name='bold',
            group = 'bold',
            tag = 'strong',
            starter = '**',
            terminator = '**'
        ),
        ClassNameFormatter(
            name='bold_class',
            group = 'bold',
            tag = 'strong',
            starter = 'b',
        ),
        EmbedFormatter(
            name='italic',
            group = 'italic',
            tag = 'em',
            starter = '~~',
            terminator = '~~'
        ),
        ClassNameFormatter(
            name='italic_class',
            group = 'italic',
            tag = 'em',
            starter = 'i',
        ),
        EmbedFormatter(
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
            allows_nesting = False,
            starter = 'code',
        ),
        ClassNameFormatter(
            name='span_class',
            group = 'span',
            tag = 'span',
            starter = 'span',
        ),
        LinkFormatter(
            name='link',
            group = 'link',
            tag = 'a',
            allows_nesting = False,
            starter = '[',
        ),
        HorizontalRuleFormatterClass(),
        HorizontalRuleFormatterClass(name = 'hr_class', directive=True),
        HeaderFormatterClass(),
        HeaderFormatterClass(name = 'header_class', directive=True),
    ]


class BlockFormatter(FormatterBase):
    def __init__(self, name : str, group : str, tag : str):
        super().__init__(name, group, FormatterType.BLOCK)
        self.tag = tag

    def build_output(self, input : str, opener : str) -> str:
        return f"<{self.tag}>{input}</{self.tag}>"

NULLFORMATTER = BlockFormatter(
    name='null',
    group = 'null',
    tag = 'null'
)

PARA_FORMATTER = BlockFormatter(
    name ='paragraph',
    group = 'para',
    tag = 'p'
)

NOOP_FORMATTER = BlockFormatter(
    name ='noop',
    group = 'noop',
    tag = 'noop'
)

##### Line Formatters

class OneLineFormatter(FormatterBase):
    def __init__(self, name : str, group : str):
        super().__init__(name=name, group=group, ftype=FormatterType.ONELINE)

class HorizontalRuleFormatterClass(OneLineFormatter):
    def __init__(self, name : str = 'hr', directive : bool = False):
        super().__init__(
            name = name,
            group = 'hr'
        )
        self.directive = directive

    def start_re(self) -> str:
        if self.directive:
            return r'^\:hr(=[^\s]*)?(?:\s|$)'
        else :
            return r'^-{3,}(?:\s|$)'

    def build_output(self, input: str, opener: str) -> str:
        index = opener.find('=')
        if index != -1:
            class_name = f' class="{opener[index+1 : -1]}"'
        else :
            class_name = ''
        if self.directive:
            return f'<hr{class_name}>'
        return '<hr>'

class HeaderFormatterClass(OneLineFormatter):
    def __init__(self, name : str = 'header', directive : bool = False):
        super().__init__(
            name = name,
            group = 'header'
        )
        self.directive = directive

    def start_re(self) -> str:
        if self.directive:
            return r'^\:h[123456](=[^\s]*)?(?:\s|$)'
        else :
            return r'^#{1,6}(?:\s)'

    def build_output(self, input: str, opener: str) -> str:
        input = input.strip()
        if self.directive:
            level = opener[2]
            index = opener.find('=')
            if index != -1:
                class_name = f' class="{opener[index+1 : -1]}"'
            else :
                class_name = ''
            return f'<h{level}{class_name}>{input}</h{level}>'
        else :
            level = opener.count('#')
            return f'<h{level}>{input}</h{level}>'


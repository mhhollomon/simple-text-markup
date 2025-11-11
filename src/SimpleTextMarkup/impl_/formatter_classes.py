from abc import ABC, abstractmethod
from enum import Enum, auto
import regex as re


class ParserProxy(ABC):
    @abstractmethod
    def get_class_name(self, tag : str) -> str:
        pass

class FormatterType(Enum):
    EMBEDDED = auto()
    ONELINE  = auto()
    BLOCK    = auto()

#############################################################
# FormatterBase
#############################################################
class FormatterBase:
    def __init__(self, name : str, group : str, ftype : FormatterType, parser : ParserProxy) -> None:
        self.name = name
        self.group = group
        self.ftype = ftype
        self.parser = parser

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

    def get_class_name(self, tag : str, override : str | None = None) -> str:
        if override is not None and override != '':
            return override
        else:
            return self.parser.get_class_name(tag)

    def get_class_string(self, tag : str, override : str | None = None) -> str:
        class_name = self.get_class_name(tag, override)
        if class_name != '':
            return f' class="{class_name}"'
        else:
            return ''

    def get_class_from_opener(self, opener : str, ignore_last_char : bool = True) -> str:
        index = opener.find('=')
        default_class = ''

        if index != -1:
            if ignore_last_char:
                default_class = opener[index+1 : -1].strip()
            else :
                default_class = opener[index+1 :].strip()
        print(f'-- Default class: "{opener}" -> "{default_class}"')
        return default_class

    def get_class_string_from_opener(self, tag : str, opener : str, ignore_last_char : bool = True) -> str:
        return self.get_class_string(tag, override=self.get_class_from_opener(opener, ignore_last_char))

#############################################################
# EmbedFormatter
#############################################################
class EmbedFormatter(FormatterBase):
    def __init__(self,
                 name : str, group : str, tag : str, starter : str,
                 parser : ParserProxy,
                 terminator : str = '', allows_nesting : bool = True,
                 one_shot : bool = False):
        super().__init__(name=name, group=group, ftype=FormatterType.EMBEDDED, parser=parser)
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
        class_string = self.get_class_string(self.tag)
        return f"<{self.tag}{class_string}>{input}</{self.tag}>"

#############################################################
# ClassNameFormatter
#############################################################
class ClassNameFormatter(EmbedFormatter):
    def __init__(self,
                 name : str, group : str, tag : str,
                 starter : str,
                 parser : ParserProxy,
                 allows_nesting : bool = True,
                 one_shot : bool = False):
        super().__init__(name=name, group=group, tag=tag, parser=parser,
                         starter=starter, terminator='>',
                         allows_nesting=allows_nesting, one_shot=one_shot
                        )

    def build_output(self, input : str, opener : str) -> str:
        class_string = self.get_class_string_from_opener(self.tag, opener)
        return f"<{self.tag}{class_string}>{input}</{self.tag}>"

    def start_re(self) -> str:
        """Need the special characters to be special"""

        return f"\\$<{self.starter}(=[^:]*)?:"

#############################################################
# LinkFormatter
#############################################################
class LinkFormatter(EmbedFormatter):
    def __init__(self, *args, **kwargs):
        kwargs['one_shot'] = True
        kwargs['tag'] = 'a'
        super().__init__(*args, **kwargs)


    def build_output(self, _ : str, opener : str) -> str:
        title_index = opener.find(']')
        if title_index != -1:
            title = opener[1:title_index]
        else :
            title = opener[1:-1]
        href = opener[title_index+2:-1]
        class_string= self.get_class_string(self.tag)
        return f"<{self.tag}{class_string} href=\"{href}\">{title}</a>"

    def start_re(self) -> str:
        return r"\[[^\]]+\]\([^)]+\)"


#############################################################
# BlockFormatter
#############################################################
class BlockFormatter(FormatterBase):
    def __init__(self, name : str, group : str, tag : str, parser : ParserProxy):
        super().__init__(name, group, FormatterType.BLOCK, parser=parser)
        self.tag = tag

    def build_output(self, input : str, opener : str) -> str:
        class_string = self.get_class_string(self.tag)
        return f"<{self.tag}{class_string}>{input}</{self.tag}>"


#############################################################
# OneLineFormatter
#############################################################
class OneLineFormatter(FormatterBase):
    def __init__(self, name : str, group : str, parser : ParserProxy):
        super().__init__(name=name, group=group, ftype=FormatterType.ONELINE, parser=parser)

#############################################################
# HorizontalRuleFormatterClass
#############################################################
class HorizontalRuleFormatterClass(OneLineFormatter):
    def __init__(self, parser : ParserProxy, name : str = 'hr', directive : bool = False):
        super().__init__(
            name = name,
            group = 'hr',
            parser = parser
        )
        self.directive = directive

    def start_re(self) -> str:
        if self.directive:
            return r'^\:hr(=[^\s]*)?(?:\s|$)'
        else :
            return r'^-{3,}(?:\s|$)'

    def build_output(self, input: str, opener: str) -> str:
        if self.directive:
            class_string = self.get_class_string_from_opener('hr', opener, False)
        else :
            class_string = self.get_class_string('hr')

        return f'<hr{class_string}>'

#############################################################
# HeaderFormatterClass
#############################################################
class HeaderFormatterClass(OneLineFormatter):
    def __init__(self, parser : ParserProxy, name : str = 'header', directive : bool = False):
        super().__init__(
            name = name,
            group = 'header',
            parser = parser
        )
        self.directive = directive

    def start_re(self) -> str:
        if self.directive:
            return r'^\:h[123456](=[^\s]*)?(?:\s|$)'
        else :
            return r'^={1,6}(?:\s)'

    def build_output(self, input: str, opener: str) -> str:
        input = input.strip()

        class_name = None
        if self.directive:
            level = opener[2]
            tag = 'h' + str(level)
            class_string = self.get_class_string_from_opener(tag, opener, False)
        else :
            level = opener.count('=')
            tag = 'h' + str(level)
            class_string = self.get_class_string(tag)

        return f'<{tag}{class_string}>{input}</h{level}>'


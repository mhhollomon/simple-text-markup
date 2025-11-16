from typing import Dict

from .renderer import Renderer
from .impl_ import *
import regex as re


def default_options() -> Dict[str, Option]:
    return {
        'use_classes' : BooleanOption('use_classes', False, OptionSource.DEFAULT),
    }

######################################################################
# STMConverter
######################################################################
class STMConverter(ParserProxy):
    def __init__(self, src : LineSrc,  options : dict[str, str] | None = None, renderer : Renderer | None = None):
        self.stack : list[Context] = []
        self.output = ''
        self.src = src

        if renderer is not None:
            self.renderer = renderer
        else :
            from .renderer.html_render import render
            self.renderer = render

        self.doc = Document()

        self.options = default_options()
        if options is not None:
            for k, v in options.items():
                if k not in self.options:
                    raise Exception(f"Unknown option: {k}")
                self.options[k].set_value(v, OptionSource.CONFIG)

        print(f"--- STMConverter: Options: {self.options}")


    #### ParserProxy overrides
    def get_class_name(self, tag : str) -> str:
        if not self.options['use_classes'].get_value():
            return ''
        if tag == 'span':
            return ''
        return f'stm-{tag}'

    def _inner_context(self) -> Context:
        return self.stack[-1]

    def _in_context(self) -> bool:
        return len(self.stack) > 0

    def _push_context(self, data : FormatterBase | Context, opener : str | None = None) -> Context:
        if isinstance(data, FormatterBase):
            if opener is None:
                raise Exception("Context created from Formatter must have an opener")
            ctx = Context.from_formatter(data, opener)
        else :
            ctx = data
        self.stack.append(ctx)
        return ctx

    def _pop_context(self) -> Context:
        return self.stack.pop()

    def _add_output(self, line : str):
        if self._in_context():
            self._inner_context().add_to_buffer(line)
        else:
            self.output += line

    def _skip_blanks_lines(self) -> bool:
        while True :
            line = self.src.get_next()
            if line is None:
                return False
            if line.strip() == '':
                continue
            self.src.push_back(line)
            return True

    def parseConfigs(self) -> bool:

        if not self._skip_blanks_lines() :
            return False

        line : str = self.src.get_next() # type: ignore

        if not line.startswith('%config '):
            self.src.push_back(line)
            return False

        line = line[len('%config '):].strip()

        for opt in re.findall(r'(\w+)=(.*)', line):
            if opt[0] not in self.options:
                raise Exception(f"Unknown option: {opt[0]}")
            self.options[opt[0]].set_value(opt[1], OptionSource.FILE)

        return True

    def parseLineSpans(self, parent : Block, line : str) :
        parent.append(Span(line))


    def parseSpans(self, parent : Block, first_line : str, explicit : bool) :
        line : str | None = first_line

        while True :
            if line is None :
                return
            if explicit and line.startswith('.}') :
                # throw away the line and return
                return
            if not explicit and line.strip() == '' :
                # throw away the line and return
                return

            self.parseLineSpans(parent, line)
            line = self.src.get_next()

    def parseList(self, parent : Block, first_line : str, level : int) :

        list_item_block = Block(tag='li')
        self.parseLineSpans(list_item_block, first_line)
        parent.append(list_item_block)

        while True :

            line = self.src.get_next()
            if line is None or line.strip() == '' :
                return

            m = re.match(r'(\s*)(-|\#) ', line)
            if m :
                if len(m.group(1)) % 4 != 0:
                    raise Exception("List indentation must be a multiple of 4 spaces")
            else :
                self.src.push_back(line)
                return

            tag = 'ul' if m.group(2) == '-' else 'ol'

            new_level = len(m.group(1)) // 4
            if new_level > level :
                new_list = Block(tag=tag)
                list_item_block.append(new_list)
                self.parseList(new_list, line[len(m.group(0)) :], new_level)
            elif new_level < level :
                self.src.push_back(line)
                return
            else :
                list_item_block = Block(tag='li')
                self.parseLineSpans(list_item_block, line[len(m.group(0)) :])
                parent.append(list_item_block)



    def tryList(self, line : str) -> bool:

        m = re.match(r'(\s*)(-|\#) ', line)
        if m :
            if len(m.group(1)) % 4 != 0:
                raise Exception("List indentation must be a multiple of 4 spaces")
        else :
            return False

        level = len(m.group(1)) // 4

        tag = 'ul' if m.group(2) == '-' else 'ol'

        block = Block(tag=tag)
        self.parseList(block, line[len(m.group(0)) :], level)
        self.doc.append(block)
        return True

    def tryTable(self, line : str) -> bool:
        return False


    def tryParagraph(self, line : str) -> bool:
        m = re.match(r'.p?{ ', line)
        if m :
            line = line[len(m.group(0)) : ]
            line = line.lstrip()
            if line.strip() == '':
                line = self.src.get_next() # type: ignore
            explicit = True
        else :
            line = line.lstrip()
            explicit = False

        block = Block(tag='p')
        self.parseSpans(block, line, explicit=explicit)
        self.doc.append(block)
        return True

    def parseBlock(self) -> bool:
        if not self._skip_blanks_lines() :
            return False

        line : str = self.src.get_next() # type: ignore

        if self.tryList(line) :
            return True

        if self.tryTable(line) :
            return True

        # Paragraph must come last since it is the default
        # if nothing else matches.
        if self.tryParagraph(line) :
            return True

        return False




    def parse(self) -> Document:

        if self.src is None:
            raise Exception("No input")

        while not self.src.is_at_end():
            while self.parseConfigs() :
                pass

            self.parseBlock()

        import json
        print('--- START ----')
        print(json.dumps(self.doc.json(), indent=2))
        print('--- END ------')

        return self.doc

    def convert(self) -> str:
        self.parse()
        return self.renderer(self.doc)

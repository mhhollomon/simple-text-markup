from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass
import regex as re
from typing import Callable

class _context_type(Enum) :
    FORMATTER = auto()
    DIRECTIVE = auto()

@dataclass
class _context:
    name : str
    buffer : str
    tbel : bool
    ctype : _context_type
    terminate : str
    handler : Callable[[str],str] | None

    def add_to_buffer(self, line):
        #if self.buffer:
        #    self.buffer += ' '
        self.buffer += line

@dataclass
class Formatter:
    name : str
    handler : Callable[[str],str]
    needs_space : bool
    starter : str
    terminator : str

Formatters : list[Formatter] = [
    Formatter(
        name='bold',
        handler = lambda x: f'<strong>{x}</strong>',
        needs_space = True,
        starter = '**',
        terminator = '**'
    ),
    Formatter(
        name='italic',
        handler = lambda x: f'<em>{x}</em>',
        needs_space = True,
        starter = '~~',
        terminator = '~~'
    ),
    Formatter(
        name='code',
        handler = lambda x: f'<code>{x}</code>',
        needs_space = True,
        starter = '``',
        terminator = '``'
    )
]

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

class STMConverter:
    def __init__(self):
        self.new_para = True
        self.stack : list[_context] = []
        self.output = ''

    def _inner_context(self) -> _context:
        return self.stack[-1]

    def handleFormatters(self, line) :

        print(f"-- Input: {line}")

        while(len(line) > 0):
            in_progress = [c.name for c in self.stack if c.ctype == _context_type.FORMATTER]
            terminated = {c.terminate : [f for f in Formatters if f.name == c.name][0] for c in self.stack if c.ctype == _context_type.FORMATTER}
            possible = {f.starter : f for f in Formatters if f.name not in in_progress}

            regexes = []
            for starter, formatter in possible.items():
                r = re.escape(starter)
                if formatter.needs_space:
                    r = r'(?<=\s|^)' + r
                regexes.append(f"(?:{r})")

            for ender, formatter in terminated.items():
                r = re.escape(ender)
                if formatter.needs_space:
                    r += r'(?=\s|$)'
                regexes.append(f"({r})")

            regex_string = '|'.join(regexes)
            print(f"-- Regex: {regex_string}")
            
            final_regex = re.compile(regex_string)

            m = final_regex.search(line)
            if m:
                retval = True
                print(f"-- Match: {m.group(0)}")
                preamble = line[:m.start()]
                line = line[m.end():]
                self._inner_context().add_to_buffer(preamble)

                if m.group(0) in possible:
                    self.stack.append(self._format_context(possible[m.group(0)]))
                elif m.group(0) in terminated:
                    while True :
                        if self._inner_context().ctype != _context_type.FORMATTER:
                            break
                        context = self.stack.pop()
                        if context.name != terminated[m.group(0)].name:
                            self._inner_context().add_to_buffer(context.buffer)
                        else:
                            self._close(context)
                            break

                continue

            print(f"-- No match: {line}")
            self._inner_context().add_to_buffer(line)
            # short circuit - no need to continue looking
            return
        
        return
    
    def handleDirectives(self, line) -> bool:
        return False
    
    def _close(self, context : _context):
        """Assumes _context has already been popped from the stack"""

        handler = context.handler if context.handler else lambda x: x
        output = handler(context.buffer.rstrip())
        if self.stack:
            self._inner_context().add_to_buffer(output)
        else:
            self.output += output

    def _blankline(self):
        while self.stack:
            if self.stack[-1].tbel:
               self._close( self.stack.pop())
            else:
                break

    def _in_context(self) -> bool:
        return len(self.stack) > 0
    
    def _para_context(self) -> _context:
        return _context(name='para', buffer='', tbel=True, 
                        ctype=_context_type.DIRECTIVE, 
                        terminate='', handler=lambda x: f"<p>{x}</p>")
    
    def _format_context(self, formatter : Formatter) -> _context:
        return _context(name=formatter.name, buffer='', tbel=True, 
                        ctype=_context_type.FORMATTER, 
                        terminate=formatter.terminator, handler=formatter.handler)

    def convert(self, input : str | Path):

        src = LineSrc(input)

        for line in src:
            if (line.strip() == ''):
                self._blankline()
                continue
            else :

                if not self._in_context():
                    if self.handleDirectives(line) :
                        continue
                    else :
                        self.stack.append(self._para_context())

                self.handleFormatters(line)
                
        while self.stack:
            self._close(self.stack.pop())
        return self.output
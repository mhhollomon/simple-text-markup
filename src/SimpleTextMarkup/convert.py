from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass
import regex as re
from typing import Callable

class _context_type(Enum) :
    FORMATTER = auto()
    DIRECTIVE = auto()


@dataclass
class Formatter:
    name : str
    handler : Callable[[str],str]
    needs_space : bool
    allows_nesting : bool
    starter : str 
    terminator : str 
    tbel : bool = True

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

Formatters : list[Formatter] = [
    Formatter(
        name='bold',
        handler = lambda x: f'<strong>{x}</strong>',
        needs_space = False,
        allows_nesting = True,
        starter = '**',
        terminator = '**'
    ),
    Formatter(
        name='italic',
        handler = lambda x: f'<em>{x}</em>',
        needs_space = False,
        allows_nesting = True,
        starter = '~~',
        terminator = '~~'
    ),
    Formatter(
        name='code',
        handler = lambda x: f'<code>{x}</code>',
        needs_space = False,
        allows_nesting = False,
        starter = '``',
        terminator = '``'
    )
]

def __null_handler(x):
    raise Exception(f"Null formatter: {x}")

NULLFORMATTER = Formatter(
    name='null',
    handler = __null_handler,
    needs_space = False,
    allows_nesting = False,
    starter = '',
    terminator = ''
)

PARA_FORMATTER = Formatter(
    name='paragraph',
    handler = lambda x: f'<p>{x}</p>',
    needs_space = False,
    allows_nesting = True,
    starter = '',
    terminator = ''
)

@dataclass
class _context:
    name : str
    buffer : str
    ctype : _context_type
    fmt : Formatter

    def add_to_buffer(self, line):
        self.buffer += line
    


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

######################################################################
# STMCOnverter
######################################################################
class STMConverter:
    def __init__(self):
        self.stack : list[_context] = []
        self.output = ''

    def _inner_context(self) -> _context:
        return self.stack[-1]

    def handleFormatters(self, line) :

        print(f"-- Input: {line}")
        count = 0

        while(len(line) > 0):
            count += 1
            #print(f"-- Count: {count} stack: {len(self.stack)}")
            if count > 100 :
                raise Exception("Infinite loop")
            
            in_progress = [c.name for c in self.stack if c.ctype == _context_type.FORMATTER]
            terminated = {c.fmt.terminator : c.fmt for c in self.stack if c.ctype == _context_type.FORMATTER}
            possible = {f.starter : f for f in Formatters if f.name not in in_progress}

            #print(f"-- In progress: {in_progress}")
            #print(f"-- Possible: {possible}")
            #print(f"-- Terminated: {terminated}")

            regexes = []
            
            ctx = self._inner_context()
            #print(f"-- Context: {ctx}")
            if ctx.ctype == _context_type.DIRECTIVE or ctx.fmt.allows_nesting:
                #print(" -- Nesting is allowed")
                for starter, formatter in possible.items():
                    r = formatter.start_re()
                    regexes.append(f"(?:{r})")

            for ender, formatter in terminated.items():
                r = formatter.end_re()
                regexes.append(f"({r})")

            regex_string = '|'.join(regexes)
            #print(f"-- Regex: {regex_string}")
            
            final_regex = re.compile(regex_string)

            m = final_regex.search(line)
            if m:
                print(f"-- Match: {m.group(0)}")
                preamble = line[:m.start()]
                line = line[m.end():]
                self._inner_context().add_to_buffer(preamble)

                if m.group(0) in possible:
                    self.stack.append(self._format_context(possible[m.group(0)]))
                elif m.group(0) in terminated:
                    while True :
                        if not self._in_context() or self._inner_context().ctype != _context_type.FORMATTER:
                            break
                        context = self.stack.pop()
                        if context.name != terminated[m.group(0)].name:
                            self._inner_context().add_to_buffer(context.fmt.terminator + context.buffer)
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

        handler = context.fmt.handler
        output = handler(context.buffer.rstrip())
        if self.stack:
            self._inner_context().add_to_buffer(output)
        else:
            self.output += output

    def _blankline(self):
        while self.stack:
            if self._inner_context().fmt.tbel:
               self._close(self.stack.pop())
            else:
                break

    def _in_context(self) -> bool:
        return len(self.stack) > 0
    
    def _para_context(self) -> _context:
        return _context(name='para', buffer='', 
                        ctype=_context_type.DIRECTIVE, 
                        fmt=PARA_FORMATTER, 
                        )
    
    def _format_context(self, formatter : Formatter) -> _context:
        return _context(name=formatter.name, buffer='',
                        ctype=_context_type.FORMATTER, fmt=formatter,
                        )

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
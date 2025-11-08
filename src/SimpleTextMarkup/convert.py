from pathlib import Path
from typing import List, TextIO
import regex as re

from .impl_ import *


######################################################################
# STMCOnverter
######################################################################
class STMConverter:
    def __init__(self):
        self.stack : list[Context] = []
        self.output = ''

    def _inner_context(self) -> Context:
        return self.stack[-1]

    def _in_context(self) -> bool:
        return len(self.stack) > 0

    def _push_context(self, data : Formatter | Context, opener : str | None = None) -> Context:
        if isinstance(data, Formatter):
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

    def handleFormatters(self, line) :

        print(f"-- Input: {line}")
        count = 0

        while(len(line) > 0):
            count += 1
            print(f"-- Count: {count} stack: {len(self.stack)}")
            if count > 100 :
                raise Exception("Infinite loop")
            
            # Nesting is controlled by the group name.
            # Only one formatter of a group can be active.
            in_progress = [c.fmt.group for c in self.stack if c.ctype == context_type.FORMATTER]
            # Reversed to make sure the inner most contexts are first in the list
            terminated = {c.name : c.fmt for c in reversed(self.stack) if c.ctype == context_type.FORMATTER}
            possible = {f.name : f for f in Formatters if f.group not in in_progress}

            print(f"-- In progress: {in_progress}")
            #print(f"-- Possible: {possible}")
            print(f"-- Terminated: {terminated}")

            regexes = []
            
            ctx = self._inner_context()
            #print(f"-- Context: {ctx}")
            if ctx.ctype == context_type.DIRECTIVE or ctx.fmt.allows_nesting:
                #print(" -- Nesting is allowed")
                for starter, formatter in possible.items():
                    r = formatter.start_re()
                    regexes.append(f"(?P<{formatter.name}>{r})")

            for ender, formatter in terminated.items():
                r = formatter.end_re()
                regexes.append(f"(?P<{formatter.name}>{r})")

            regex_string = '|'.join(regexes)
            print(f"-- Regex: {regex_string}")
            
            final_regex = re.compile(regex_string)

            m = final_regex.search(line)
            if m:
                # gotta be a better way
                opener = m.group(0)
                matching_formatter = [ i[0] for i in m.groupdict().items() if i[1] == opener ][0]
                print(f"-- Matching formatter: {matching_formatter}")
                print(f"-- Match: {opener}")
                preamble = line[:m.start()]
                print(f"-- Preamble: {preamble}")
                line = line[m.end():]
                self._inner_context().add_to_buffer(preamble)

                if matching_formatter in possible :
                    fm = possible[matching_formatter]
                    if fm.one_shot:
                        self._inner_context().add_to_buffer(fm.build_output(opener, opener))
                    else :
                        self._push_context(fm, opener)

                elif matching_formatter in terminated:
                    while True :
                        if not self._in_context() or self._inner_context().ctype != context_type.FORMATTER:
                            break
                        context = self._pop_context()
                        if context.name != matching_formatter:
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
    
    def _close(self, ctx : Context):
        """Assumes ctx has already been popped from the stack"""

        output = ctx.fmt.build_output(ctx.buffer.rstrip(), ctx.opener)
        self._add_output(output)

    def _blankline(self):
        while self._in_context():
            if self._inner_context().fmt.tbel:
               self._close(self._pop_context())
            else:
                break

    def _para_context(self) -> Context:
        return Context(name='para', buffer='', 
                        ctype=context_type.DIRECTIVE, 
                        fmt=PARA_FORMATTER, opener=''
                        )
        
    def convert(self, input : str | Path | TextIO | List[str]) -> str:

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
                        self._push_context(self._para_context())

                self.handleFormatters(line)
                
        while self._in_context():
            self._close(self._pop_context())

        return self.output
from .impl_ import *
import regex as re


######################################################################
# STMCOnverter
######################################################################
class STMConverter:
    def __init__(self, src : LineSrc):
        self.stack : list[Context] = []
        self.output = ''
        self.src = src

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

    def parseInlineFormatters(self) -> bool:
        line = self.src.get_next()
        if line is None:
            return False

        print(f"-- Input: {line}")
        count = 0

        while(len(line) > 0):
            count += 1
            print(f"-- Count: {count} stack: {len(self.stack)}")
            if count > 100 :
                raise Exception("Infinite loop")

            # Nesting is controlled by the group name.
            # Only one formatter of a group can be active.
            in_progress = [c.fmt.group for c in self.stack if c.ftype == FormatterType.EMBEDDED]
            # Reversed to make sure the inner most contexts are first in the list
            terminated = {c.name : c.fmt for c in reversed(self.stack) if c.ftype == FormatterType.EMBEDDED}
            possible = {f.name : f for f in Formatters if f.group not in in_progress}

            print(f"-- In progress: {in_progress}")
            #print(f"-- Possible: {possible}")
            print(f"-- Terminated: {terminated}")

            regexes = []

            ctx = self._inner_context()
            #print(f"-- Context: {ctx}")
            if ctx.ftype == FormatterType.BLOCK or ctx.fmt.allows_nesting:
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
                        if not self._in_context() or self._inner_context().ftype != FormatterType.EMBEDDED:
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
            return True

        return True

    def parseConfigs(self) -> bool:
        line = self.src.get_next()
        while (line is not None and line.strip() == ''):
            line = self.src.get_next()
        if line is None:
            return False

        # for now, just ignore configs
        self.src.push_back(line)
        return False

    def parseBlock(self) -> bool:
        line = self.src.get_next()
        while (line is not None and line.strip() == ''):
            line = self.src.get_next()
        if line is None:
            return False

        self.src.push_back(line)
        self._push_context(self._para_context())

        while not self.src.is_blank():
            self.parseInlineFormatters()

        return True

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
        return Context(
            fmt=PARA_FORMATTER,
            name=PARA_FORMATTER.name,
            ftype=PARA_FORMATTER.ftype,
            buffer='',
            opener=''
        )

    def convert(self) -> str:

        if self.src is None:
            raise Exception("No input")


        while (not self.src.is_at_end()):
            while self.parseConfigs() :
                pass

            if self.parseBlock():
                self._blankline()
                continue


        while self._in_context():
            self._close(self._pop_context())

        return self.output

from .impl_ import *
import regex as re


######################################################################
# STMCOnverter
######################################################################
class STMConverter:
    def __init__(self, src : LineSrc, formatters : list[EmbedFormatter] | None = None):
        self.stack : list[Context] = []
        self.output = ''
        self.src = src

        if formatters is not None:
            self.formatters = formatters
        else:
            self.formatters = get_formatters()

        self.embeds = [f for f in self.formatters if f.ftype == FormatterType.EMBEDDED]
        self.oneliners = [f for f in self.formatters if f.ftype == FormatterType.ONELINE]
        self.blocks = [f for f in self.formatters if f.ftype == FormatterType.BLOCK]

    def _inner_context(self) -> Context:
        return self.stack[-1]

    def _in_context(self) -> bool:
        return len(self.stack) > 0

    def _push_context(self, data : EmbedFormatter | Context, opener : str | None = None) -> Context:
        if isinstance(data, EmbedFormatter):
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

    def parseEmbeddedFormatters(self) -> bool:
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
            possible = {f.name : f for f in self.embeds if f.group not in in_progress}

            print(f"-- In progress: {in_progress}")
            #print(f"-- Possible: {possible}")
            print(f"-- Terminated: {terminated}")

            regexes = []

            ctx = self._inner_context()
            #print(f"-- Context: {ctx}")
            if ctx.ftype == FormatterType.BLOCK or ctx.fmt.nestable():
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
                    if fm.self_closing():
                        self._inner_context().add_to_buffer(fm.build_output(opener, opener))
                    else :
                        self._push_context(fm, opener)

                elif matching_formatter in terminated:
                    while True :
                        if not self._in_context() or self._inner_context().ftype != FormatterType.EMBEDDED:
                            break
                        context = self._pop_context()
                        if context.name != matching_formatter:
                            self._inner_context().add_to_buffer(context.opener + context.buffer)
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

    def _build_oneliner_regex(self) -> re.Pattern:
        regexes = []
        for f in self.oneliners:
            r = f.start_re()
            regexes.append(f"(?P<{f.name}>{r})")
        return re.compile('|'.join(regexes))

    def parseOneLiners(self) -> bool:
        line = self.src.get_next()
        while (line is not None and line.strip() == ''):
            line = self.src.get_next()
        if line is None:
            return False

        regex = self._build_oneliner_regex()
        print("-- One liner Regex: " + regex.pattern)
        print("-- One liner line: " + line)
        m = regex.search(line)
        if m:
            opener = m.group(0)
            matching_formatter = [ i[0] for i in m.groupdict().items() if i[1] == opener ][0]
            formatter = [ f for f in self.oneliners if f.name == matching_formatter ][0]
            postlude = line[m.end():]
            self._add_output(formatter.build_output(postlude, opener))

            return True

        self.src.push_back(line)
        return False

    def parseBlock(self) -> bool:
        line = self.src.get_next()
        while (line is not None and line.strip() == ''):
            line = self.src.get_next()
        if line is None:
            return False

        self.src.push_back(line)

        ctx = self._para_context()
        self._push_context(ctx)

        while not self.src.is_blank():
            self.parseEmbeddedFormatters()

        while self._in_context() and self._inner_context() != ctx:
            self._close(self._pop_context())

        self._close(self._pop_context())

        return True

    def _close(self, ctx : Context):
        """Assumes ctx has already been popped from the stack"""

        output = ctx.fmt.build_output(ctx.buffer.rstrip(), ctx.opener)
        self._add_output(output)

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

            while self.parseOneLiners() :
                pass

            self.parseBlock()


        while self._in_context():
            self._close(self._pop_context())

        return self.output

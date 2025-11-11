from .formatter_classes import *


def get_formatters(parser : ParserProxy) -> list[FormatterBase]:
    """Generate list of formatters"""
    return [
        EmbedFormatter(
            name='bold',
            group = 'bold',
            tag = 'strong',
            starter = '**',
            terminator = '**',
            parser=parser,
        ),
        ClassNameFormatter(
            name='bold_class',
            group = 'bold',
            tag = 'strong',
            starter = 'b',
            parser=parser,
        ),
        EmbedFormatter(
            name='italic',
            group = 'italic',
            tag = 'em',
            starter = '~~',
            terminator = '~~',
            parser=parser,
        ),
        ClassNameFormatter(
            name='italic_class',
            group = 'italic',
            tag = 'em',
            starter = 'i',
            parser=parser,
        ),
        EmbedFormatter(
            name='code',
            group = 'code',
            tag = 'code',
            allows_nesting = False,
            starter = '``',
            terminator = '``',
            parser=parser,
        ),
        ClassNameFormatter(
            name='code_class',
            group = 'code',
            tag = 'code',
            allows_nesting = False,
            starter = 'code',
            parser=parser,
        ),
        ClassNameFormatter(
            name='span_class',
            group = 'span',
            tag = 'span',
            starter = 'span',
            parser=parser,
        ),
        LinkFormatter(
            name='link',
            group = 'link',
            tag = 'a',
            allows_nesting = False,
            starter = '[',
            parser=parser,
        ),
        HorizontalRuleFormatterClass(parser=parser),
        HorizontalRuleFormatterClass(name = 'hr_class', parser=parser, directive=True),
        HeaderFormatterClass(parser=parser),
        HeaderFormatterClass(name = 'header_class', parser=parser, directive=True),

        ###### BLOCK FORMATTERS
        BlockFormatter(
            name='null',
            group = 'null',
            tag = 'null',
            parser=parser
        ),

        BlockFormatter(
            name ='paragraph',
            group = 'para',
            tag = 'p',
            parser=parser
        ),

        BlockFormatter(
            name ='noop',
            group = 'noop',
            tag = 'noop',
            parser=parser
        )
    ]


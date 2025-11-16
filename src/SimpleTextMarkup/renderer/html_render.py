from .type import Renderer
from SimpleTextMarkup.impl_.ast import Document, Block

def renderBlock(block : Block) :
    output = ''
    first = True
    for c in block.children:
        if c.ntype in HELPERS:
            if not first and c.ntype == 'span':
                output += ' '
            first = False
            output += HELPERS[c.ntype](c)
        else :
            raise Exception(f"Unknown node type: {c.ntype}")

    if block.tag != '':
        output = f'<{block.tag}>{output}</{block.tag}>'

    return output

HELPERS = {
    'block' : renderBlock,
    'span' : lambda span : span.text
}

def render(doc : Document) -> str:
    output = ''

    for c in doc.children:
        if c.ntype in HELPERS:
            output += HELPERS[c.ntype](c)
        else :
            raise Exception(f"Unknown node type: {c.ntype}")

    return output


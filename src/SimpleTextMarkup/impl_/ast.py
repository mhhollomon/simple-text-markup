
from typing import Dict, List

class Node :
    ntype : str = 'Node'

    def __init__(self, tag : str = '') -> None:
        self.tag = tag


    def json(self) -> Dict[str, str] :
        return { 'ntype' : self.ntype, 'tag' : self.tag }

    def __str__(self) -> str:
        return f"Block({self.ntype}, '{self.tag}')"

class Span(Node) :
    ntype = 'span'
    def __init__(self, text : str, tag : str = '') -> None:
        super().__init__(tag=tag)
        self.text = text

    def json(self) :
        return { **(super().json()), 'text' : self.text}

class Container(Node) :
    ntype = 'container'

    def __init__(self) -> None:
        super().__init__(tag='')
        self.children : List[Node] = []

    def append(self, child : Node) :
        self.children.append(child)

    def json(self) :
        return { **(super().json()),
                'children' : [ c.json() for c in self.children]}


class Block(Container) :
    ntype = 'block'

    def __init__(self, tag : str = '') -> None:
        super().__init__()
        self.tag = tag


class Paragraph(Block) :

    def __init__(self, use_wrapper : bool) -> None:
        self.use_wrapper = use_wrapper
        tag = 'p' if use_wrapper else ''
        super().__init__(tag=tag)

    def json(self) :
        return {  **(super().json()),
                'use_wrapper' : self.use_wrapper,
                }

class Document(Container) :
    ntype = 'document'

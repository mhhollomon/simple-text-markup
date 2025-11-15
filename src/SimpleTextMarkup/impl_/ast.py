
from typing import Dict, List

class Node :
    ntype : str = 'Node'

    def json(self) -> Dict[str, str] :
        return { 'ntype' : self.ntype }

class Span(Node) :
    ntype = 'span'
    def __init__(self, text : str) -> None:
        self.text = text

    def json(self) :
        return { **(super().json()), 'text' : self.text}

class Container(Node) :
    ntype = 'container'

    def __init__(self) -> None:
        self.children : List[Node] = []

    def append(self, child : Node) :
        self.children.append(child)

    def json(self) :
        return { **(super().json()),
                'children' : [ c.json() for c in self.children]}


class Block(Container) :
    ntype = 'block'

    def __init__(self, tag : str) -> None:
        super().__init__()
        self.tag = tag

    def json(self) :
        return {  **(super().json()),
                'tag' : self.tag,
                }

class Document(Container) :
    ntype = 'document'

    def __init__(self):
        self.children : List[Block] = []

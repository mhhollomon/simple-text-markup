
from typing import List

class Span :
    def __init__(self, text : str) -> None:
        self.text = text

    def json(self) :
        return { 'ntype' : 'span', 'text' : self.text}

class Block :
    def __init__(self):
        self.children : List['Span | Block'] = []

    def append(self, child : 'Span | Block') :
        self.children.append(child)

    def json(self) :
        return { 'ntype' : 'block',
                'children' : [ c.json() for c in self.children]}

class Document :
    def __init__(self):
        self.children : List[Block] = []

    def append(self, child : Block) :
        self.children.append(child)

    def json(self) :
        return { 'ntype' : 'document',
                'children' : [ c.json() for c in self.children]}



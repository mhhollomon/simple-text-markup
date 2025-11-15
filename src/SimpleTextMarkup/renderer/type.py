from typing import Callable

from SimpleTextMarkup.impl_.ast import Document


type Renderer = Callable[[Document], str]

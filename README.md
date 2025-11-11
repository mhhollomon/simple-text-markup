# simple-text-formatter

Not sure it is really simple.

Based largely on Markdown, but with some "rationalizations".

# Command Line

The package includes a command-line tool `stm`

```
usage: stm [-h] [--use-classes | --no-use-classes] [input] [output]

positional arguments:
  input             Input file. If not given, or is '-', reads from stdin
  output            Output file . If not given, or is '-', writes to stdout

options:
  -h, --help        show this help message and exit
  --use-classes     Include a class name in each generated tag
  --no-use-classes  Do not include a class name in each generated tag
  ```

# Module API
```python
from SimpleTextMarkup import stm_convert, stm_convert_to_file

options = {
    'use-classes' : True,
}

# Read from file :
output = stm_convert('/path/to/file.stm', options)

from pathlib import Path
output = stm_convert(Path('/path/to/file.stm'))

# Read from open file
with open('/path/to/file.stm', 'r') as f:
    output = stm_convert(f)

# stm_convert_to_file is a thin wrapper around stm_convert
# that writes to file/Path/TextIO rather than returning a string.
stm_convert_to_file('/path/to/file.stm', sys.stdout)
```

# Markup Language

## Paragraph
A series of lines delimited by one or more blank lines.

## Block Formatters
Block formatters must come after a blank line, but do not need to be followed by a blank line.

The colon must be the first character on the line.

### Horizontal Rule
``:hr``

``:hr=my-class``

Text may follow the formatter, but it will be ignored. It must be separated from the
formatter by at least one space

``:hr This text is ignored``

### Header
`=` or `:h1`

`==` or `:h2`

`===` or `:h3`

`====` or `:h4`

`=====` or `:h5`

`======` or `:h6`

`:h5=my-class Header Text`


## In-line Formatters

Formatters can be nested (mostly), but not inside themselves.

Formatters cannot span paragaphs, but can span line breaks.

If a formatter is still open when the paragraph ends, it will be closed as if the terminator characters had been seen. (May change this)

If a formatter is still open when a surrounding formatter is closed, the inner formatter is ignored.
e.g.

``t **bold ~~italics more**`` => "t **bold \~\~italics more**"

### Alternate Form
Most of the In-line formatters have an alternate form that allow specifying a CSS class to embed
in tag. In these, the class can be empty. If so, the equal-sign my be omitted.

### Bold
``**Text**`` => **Text**

alt form : ``$<b=class:Text To Bold>``

### Italics
``~~Text~~`` => *Text*

Alt Form : ``$<i=class:Text to Italicize>``

### Code
``\`\`Text\`\` `` => ``Text``

(See? There is no clean way to get the back-ticks through)

Other formatter cannot be nested inside code, though it can be nested inside others.

``**\`\`bold code\`\`**`` => **``bold code``**

Alt Form : ``$<code=class:Text as code>``

### Span
This allows you to surround text with a ``<span>`` html tag. It only has an alt form.

Alt Form : ``$<span=class:Text to embed in span>``

### Link
Standard Markdown Link

``[text to display](url)``

Unlike the others, this may not stretch over multiple lines.
Also, there may not be a space between the closing bracket and opening parenthesis.

# Building

```bash
$ git clone ...
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
$ flit build

# It can be installed locally via pip
$ pip install ${path to repo}/dist/simpletextmarkup-0.1.0-py2.py3-none-any.whl
```

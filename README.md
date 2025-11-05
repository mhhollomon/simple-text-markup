# simple-text-formatter

Not sure it is really simple.

Based largely on Markdown, but with some "rationalizations".

## Paragraph
A series of lines delimited by one or more blank lines.

## In-line Formatters

Formatters can be nested (mostly), but not inside themselves.

Formatters cannot span paragaphs, but can span line breaks.

If a formatter is still open when the paragraph ends, it will be closed as if the terminator characters had been seen. (May change this)

If a formatter is still open when a surrounding formatter is closed, the inner formatter is ignored.
e.g.
``t **bold ~~italics more**`` => "t **bold \~\~italics more**"

### Bold
``**Text**`` => **Text**

### Italics
``~~Text~~`` => *Text*

### Code
``\`\`Text\`\` `` => ``Text``

(See? There is no clean way to get the back-ticks through)

Other formatter cannot be nested inside code, though it can be nested inside others.
``**\`\`bold code\`\`**`` => **``bold code``**
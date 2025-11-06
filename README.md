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

### Alternate Form
Most of the In-line formatters have an alternate form that allwo specifying a CSS class to embed
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
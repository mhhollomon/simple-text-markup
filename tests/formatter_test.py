from SimpleTextMarkup.convert import STMConverter

def test_formatters():
    assert STMConverter().convert("test **bold** test") == "<p>test <strong>bold</strong> test</p>"
    assert STMConverter().convert("test ~~italic~~ test") == "<p>test <em>italic</em> test</p>"
    assert STMConverter().convert("test ``code`` test") == "<p>test <code>code</code> test</p>"

def test_no_space_formatters() :
    assert STMConverter().convert("test**bold**test") == "<p>test<strong>bold</strong>test</p>"
    assert STMConverter().convert("test~~italic~~test") == "<p>test<em>italic</em>test</p>"
    assert STMConverter().convert("test``code``test") == "<p>test<code>code</code>test</p>"

def test_backslashed_formatters():
    assert STMConverter().convert("test \\**bold\\** test") == "<p>test \\**bold\\** test</p>"
    assert STMConverter().convert("test \\~~italic\\~~ test") == "<p>test \\~~italic\\~~ test</p>"
    assert STMConverter().convert("test \\``code\\`` test") == "<p>test \\``code\\`` test</p>"

def test_correctly_nested_formatters():
    assert STMConverter().convert("test **bold ~~italic~~ bold** test") == "<p>test <strong>bold <em>italic</em> bold</strong> test</p>"
    assert STMConverter().convert("test **bold ``code`` bold** test") == "<p>test <strong>bold <code>code</code> bold</strong> test</p>"

def test_multiple_lines_formatted():
    assert STMConverter().convert("test **bold ~~italic~~ test\nmore text**") == "<p>test <strong>bold <em>italic</em> test more text</strong></p>"

def test_unterminated_formatters():
    """Unterminated formatters should be closed at the end of the block"""
    assert STMConverter().convert("test **bold ~~italic~~") == "<p>test <strong>bold <em>italic</em></strong></p>"
    assert STMConverter().convert("test ~~italic **bold**\nAnother line") == "<p>test <em>italic <strong>bold</strong> Another line</em></p>"
    assert STMConverter().convert("test **bold ~~italic~~\nAnother line\n\nNew Paragraph") == \
        "<p>test <strong>bold <em>italic</em> Another line</strong></p><p>New Paragraph</p>"
    
def test_unterminated_nested_formatters():
    assert STMConverter().convert("test **bold ~~italic**") == "<p>test <strong>bold ~~italic</strong></p>"
    assert STMConverter().convert("test ~~italic **bold~~") == "<p>test <em>italic **bold</em></p>"

def test_no_nesting_in_code():
    assert STMConverter().convert("test ``code ~~italic~~ code`` test") == "<p>test <code>code ~~italic~~ code</code> test</p>"
    assert STMConverter().convert("test ``code **bold** code`` test") == "<p>test <code>code **bold** code</code> test</p>"
    assert STMConverter().convert("test ``code **bold ~~italic~~ bold** code`` test") == "<p>test <code>code **bold ~~italic~~ bold** code</code> test</p>"
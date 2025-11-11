from SimpleTextMarkup import stm_convert

def test_class():
    assert stm_convert("test $<b=bold-c:bold> test") == "<p>test <strong class=\"bold-c\">bold</strong> test</p>"
    assert stm_convert("test $<i=my__class:some italic text> test") == "<p>test <em class=\"my__class\">some italic text</em> test</p>"
    assert stm_convert("test $<code=my__class:some codish text> test") == "<p>test <code class=\"my__class\">some codish text</code> test</p>"

def test_class_no_class():
    assert stm_convert("test $<b:bold> test") == "<p>test <strong>bold</strong> test</p>"
    assert stm_convert("test $<i:italic> test") == "<p>test <em>italic</em> test</p>"
    assert stm_convert("test $<code:codish> test") == "<p>test <code>codish</code> test</p>"
    assert stm_convert("test $<b=:bold> test") == "<p>test <strong>bold</strong> test</p>"
    assert stm_convert("test $<i=:italic> test") == "<p>test <em>italic</em> test</p>"
    assert stm_convert("test $<code=  :codish> test") == "<p>test <code>codish</code> test</p>"

def test_class_with_spaces():
    assert stm_convert("test $<b=bold-c another_class:bold> test") == "<p>test <strong class=\"bold-c another_class\">bold</strong> test</p>"


def test_class_nested():
    assert stm_convert('test $<b=bold-c:bold $<i=foo: italic>> test') == "<p>test <strong class=\"bold-c\">bold <em class=\"foo\"> italic</em></strong> test</p>"

def test_class_and_normal_nested():
    assert stm_convert("test $<b=bold-c:bold **bold**> normal test") == "<p>test <strong class=\"bold-c\">bold **bold**</strong> normal test</p>"
    assert stm_convert("test $<b=bold-c:bold ~~italic~~> normal test") == "<p>test <strong class=\"bold-c\">bold <em>italic</em></strong> normal test</p>"

def test_class_nested_in_normal():
    assert stm_convert("test **This is bold. This is $<i=foo: italic too>** test") == "<p>test <strong>This is bold. This is <em class=\"foo\"> italic too</em></strong> test</p>"

def test_extras():
    assert stm_convert("test $<strike:strike> test") == "<p>test <s>strike</s> test</p>"
    assert stm_convert("test $<sub:subscript> test") == "<p>test <sub>subscript</sub> test</p>"
    assert stm_convert("test $<sup:superscript> test") == "<p>test <sup>superscript</sup> test</p>"

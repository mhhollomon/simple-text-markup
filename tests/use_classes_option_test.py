from SimpleTextMarkup.converter import stm_convert


def test_off():
    assert stm_convert("test **bold** test") == "<p>test <strong>bold</strong> test</p>"
    assert stm_convert("test ~~italic~~ test") == "<p>test <em>italic</em> test</p>"
    assert stm_convert("test ``code`` test") == "<p>test <code>code</code> test</p>"

def test_on() :
    options = { "use_classes": "true" }
    assert stm_convert("test **bold** test", options) == \
        '<p class="stm-p">test <strong class="stm-strong">bold</strong> test</p>'
    assert stm_convert("test ~~italic~~ test", options) == \
        '<p class="stm-p">test <em class="stm-em">italic</em> test</p>'
    assert stm_convert("== header", options) == \
        '<h2 class="stm-h2">header</h2>'
    assert stm_convert("--- ", options) == \
        '<hr class="stm-hr">'

    # span should not be styled
    assert stm_convert("$<span: test>", options) == \
        '<p class="stm-p"><span> test</span></p>'

def test_overridden() :
    options = { "use_classes": "true" }
    assert stm_convert(":hr=bar extra to be ignored", options) == \
        '<hr class="bar">'
    assert stm_convert(":h3=bar my header", options) == \
        '<h3 class="bar">my header</h3>'
    assert stm_convert("$<span=span-class: test>", options) == \
        '<p class="stm-p"><span class="span-class"> test</span></p>'

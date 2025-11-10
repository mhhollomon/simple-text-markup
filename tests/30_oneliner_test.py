from SimpleTextMarkup import stm_convert

def test_hr_oneliner():
    assert stm_convert("--- extra to be ignored\nparagraph with **bold**") == "<hr><p>paragraph with <strong>bold</strong></p>"

def test_hr_with_class():
    assert stm_convert(":hr=bar extra to be ignored\nparagraph with **bold**") == "<hr class=\"bar\"><p>paragraph with <strong>bold</strong></p>"

def test_header():
    assert stm_convert("# This is a header") == "<h1>This is a header</h1>"
    assert stm_convert("## This is a header") == "<h2>This is a header</h2>"
    assert stm_convert("### This is a header") == "<h3>This is a header</h3>"
    assert stm_convert("#### This is a header") == "<h4>This is a header</h4>"
    assert stm_convert("##### This is a header") == "<h5>This is a header</h5>"
    assert stm_convert("###### This is a header") == "<h6>This is a header</h6>"

    assert stm_convert("##No Space") == "<p>##No Space</p>"

def test_directive_header():
    assert stm_convert(":h1 This is a header") == "<h1>This is a header</h1>"
    assert stm_convert(":h2 This is a header") == "<h2>This is a header</h2>"
    assert stm_convert(":h3 This is a header") == "<h3>This is a header</h3>"
    assert stm_convert(":h4 This is a header") == "<h4>This is a header</h4>"
    assert stm_convert(":h5 This is a header") == "<h5>This is a header</h5>"
    assert stm_convert(":h6 This is a header") == "<h6>This is a header</h6>"

    assert stm_convert(":h1=new-class This is a header") == "<h1 class=\"new-class\">This is a header</h1>"

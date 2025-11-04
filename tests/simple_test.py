import SimpleTextMarkup as stm
from SimpleTextMarkup.convert import STMConverter


def test_version():
    assert stm.__version__ == "0.1.0"

def test_string_convert():

    obj = STMConverter()
    assert obj.convert("test") == "<p>test</p>"

def test_path_convert(tmp_path):
    file = tmp_path / "test.stm"
    file.write_text("second test")
    obj = STMConverter()
    assert obj.convert(file) == "<p>second test</p>"

def test_two_lines():
    obj = STMConverter()
    assert obj.convert("first line\nsecond line") == "<p>first line second line</p>"

def test_two_paras():
    obj = STMConverter()
    assert obj.convert("first line\n\nsecond line") == "<p>first line</p><p>second line</p>"

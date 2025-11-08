import SimpleTextMarkup as stm


def test_version():
    assert stm.__version__ == "0.1.0"

def test_string_convert():
    assert stm.stm_convert("test") == "<p>test</p>"

def test_path_convert(tmp_path):
    file = tmp_path / "test.stm"
    file.write_text("second test")
    assert stm.stm_convert(file) == "<p>second test</p>"

def test_textio_convert(tmp_path):
    file = tmp_path / "test.stm"
    file.write_text("third test")
    with open(file, "r") as f :
        assert stm.stm_convert(f) == "<p>third test</p>"

def test_two_lines():
    assert stm.stm_convert("first line\nsecond line") == "<p>first line second line</p>"

def test_two_paras():
    assert stm.stm_convert("first line\n\nsecond line") == "<p>first line</p><p>second line</p>"

def test_write_to_file(tmp_path) :
    file = tmp_path / "test.html"
    stm.stm_convert_to_file("first line\n\nsecond line", file)
    assert file.read_text() == "<p>first line</p><p>second line</p>"

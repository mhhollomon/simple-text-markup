import pytest
import SimpleTextMarkup as stm

def test_unordered_simple():
    assert stm.stm_convert("- item 1\n- item 2") == "<ul><li>item 1</li><li>item 2</li></ul>"

def test_unordered_bad_indent() :
    with pytest.raises(Exception):
        stm.stm_convert("- item 1\n - item 2")

def test_unordered_sublist() :
    assert stm.stm_convert("- item 1\n    - item 2") == "<ul><li>item 1<ul><li>item 2</li></ul></li></ul>"

def test_ordered_simple() :
    assert stm.stm_convert("# item 1\n# item 2") == "<ol><li>item 1</li><li>item 2</li></ol>"

def test_ordered_bad_indent() :
    with pytest.raises(Exception):
        stm.stm_convert("# item 1\n # item 2")

def test_ordered_sublist() :
    assert stm.stm_convert("# item 1\n    # item 2") == "<ol><li>item 1<ol><li>item 2</li></ol></li></ol>"

def test_ordered_inside_ul() :
    assert stm.stm_convert("- item 1\n    # item 2") == "<ul><li>item 1<ol><li>item 2</li></ol></li></ul>"

def test_return_to_outer_list() :
    assert stm.stm_convert("- item 1\n    # item 2\n- item 3") == \
      "<ul><li>item 1<ol><li>item 2</li></ol></li><li>item 3</li></ul>"

def test_unwrapped_paragraph_in_list() :
    assert stm.stm_convert("- .{ paragraph\n    .}") == "<ul><li>paragraph</li></ul>"
    assert stm.stm_convert("- .{\n    paragraph\n    .}") == "<ul><li>paragraph</li></ul>"

@pytest.mark.skip
def test_wrapped_paragraph_in_list() :
    assert stm.stm_convert("- .p{\n    paragraph\n    .}\n- item 2") == \
        "<ul><li><p>paragraph</p></li><li>item 2</li></ul>"


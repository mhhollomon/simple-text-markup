import pytest
import SimpleTextMarkup as stm

def test_paragraph():
    assert stm.stm_convert(".p{ test\n.}") == "<p>test</p>"

def test_ptype_doesnt_stop_at_blank_line():
    assert stm.stm_convert(".p{ test\n\ntest 2\ntest 3\n.}") == "<p>test test 2 test 3</p>"

def test_block_context_as_para() :
    assert stm.stm_convert(".{ test\n.}") == "<p>test</p>"

def test_implied_paragraph() :
    assert stm.stm_convert("test\nsecond line") == "<p>test second line</p>"
    assert stm.stm_convert("test\n\nsecond paragraph") == "<p>test</p><p>second paragraph</p>"

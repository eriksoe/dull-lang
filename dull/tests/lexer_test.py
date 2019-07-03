import dull.lexer
from dull.lexer import LabelToken

def tokens(s): return dull.lexer.tokenize(s)

def test_empty_source():
    assert tokens("") == []

def test_blank_line():
    assert tokens("\n") == []

def test_comment_line():
    assert tokens("#This is a comment\n") == []

def test_reference_text():
    assert tokens("All work and no play makes Jack a dull boy\n") == [LabelToken("All")]

def test_reference_text_with_padding():
    assert tokens(" \tAll work and no play makes Jack a dull boy\t \n") == [LabelToken("All")]

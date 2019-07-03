import dull.lexer
from dull.lexer import *#LabelToken, InsertionToken, Deletiontoken

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

def test_label_none():
    # No mutation, no uppercased words:
    assert tokens("all work and no play makes Jack a dull boy\n") == [LabelToken("")]

def test_label_none2():
    # Insertion + lowercased:
    assert tokens("xall work and no play makes Jack a dull boy\n") == [LabelToken(""), InsertionToken("x")]

def test_label_none3():
    # Insertion + uppercased:
    assert tokens("xAll work and no play makes Jack a dull boy\n") == [LabelToken(""), InsertionToken("x")]

def test_label_none4():
   # Deletion:
   assert tokens("LL work and no play makes Jack a dull boy\n") == [LabelToken(""), DeletionToken("a")]
# OBS This is interpreted as Replace+Delete.

def test_label_none5():
    # Insertion in middle of word:
    assert tokens("al,L work and no play makes Jack a dull boy\n") == [LabelToken(""), InsertionToken(",")]

def test_doubling():
    assert tokens("all work and no pllay makes Jack a dull boy\n") == [LabelToken(""), DoublingToken("l")]
def test_transposition():
    assert tokens("all work and no paly makes Jack a dull boy\n") == [LabelToken(""), TranspositionToken("l","a")]
def test_replacement():
    assert tokens("all work and no pway makes Jack a dull boy\n") == [LabelToken(""), ReplacementToken("l","w")]
def test_deletion():
    assert tokens("all work and no ply makes Jack a dull boy\n") == [LabelToken(""), DeletionToken("a")]
def test_insertion():
    assert tokens("all work and no polay makes Jack a dull boy\n") == [LabelToken(""), InsertionToken("o")]

def test_all_mutations_in_one_line():
    assert tokens("aallw ork amdno plkay makes Jack a dull boy\n") == [
        LabelToken(""),
        DoublingToken("a"),
        TranspositionToken(" ","w"),
        ReplacementToken("n","m"),
        DeletionToken(" "),
        InsertionToken("k")]

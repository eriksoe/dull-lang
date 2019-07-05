import dull.lexer
from dull.lexer import *

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

def test_reference_text_split_on_several_lines():
    # Plain split:
    assert tokens("All work and no play\nmakes Jack a dull boy") == [LabelToken("All")]
    # With whitespace padding:
    assert tokens("All work and no play \n makes Jack a dull boy") == [LabelToken("All")]
    # More than two lines:
    assert tokens("All work\nand no play\nmakes Jack\na dull boy") == [LabelToken("All")]

def test_newline_within_word_means_inserted_space():
    # Split in the middle of a work means an inserted space:
    assert tokens("All work and no pl\nay makes Jack a dull boy") == [LabelToken("All"), InsertionToken(" ")]

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

def test_label_none5():
    # Insertion in middle of word:
    assert tokens("al,L work and no play makes Jack a dull boy\n") == [LabelToken(""), InsertionToken(",")]

def test_label_midword():
    # Insertion in middle of word:
    assert tokens("aL,L work and no play makes Jack a dull boy\n") == [LabelToken("aL"), InsertionToken(",")]

def test_label_midword2():
    # Insertion in middle of word:
    assert tokens("All Wor,k and no play makes Jack a dull boy\n") == [LabelToken("All Wor"), InsertionToken(",")]

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

def test_all_deletion_locations():
    ref = dull.lexer.REFERENCE_TEXT
    for i in range(len(ref)):
        s = ref[:i] + ref[i+1:]
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            DeletionToken(ref[i])]

def test_all_insertion_locations():
    ref = dull.lexer.REFERENCE_TEXT
    for i in range(len(ref)+1):
        s = ref[:i] + "x" + ref[i:]
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            InsertionToken("x", i==len(ref))]

def test_all_replacement_locations():
    ref = dull.lexer.REFERENCE_TEXT
    for i in range(len(ref)):
        s = ref[:i] + "x" + ref[i+1:]
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            ReplacementToken(ref[i], "x")]

def test_all_transposition_locations():
    ref = dull.lexer.REFERENCE_TEXT
    for i in range(len(ref)-1):
        (a,b) = (ref[i], ref[i+1])
        if a==b: continue

        s = ref[:i] + b + a + ref[i+2:]
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            TranspositionToken(a, b)]

def test_all_doubling_locations():
    ref = dull.lexer.REFERENCE_TEXT
    for i in range(len(ref)):
        c = ref[i]
        if i<len(ref)-2 and c==ref[i+2]:
            # Confusable with transposition+insertion; needs 3 lookahead to distinguish.
            continue

        s = ref[:i] + c + ref[i:]
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            DoublingToken(c)]

def test_end_punctuation():
    ref = dull.lexer.REFERENCE_TEXT
    for punct in [".", ",", ":", ";", "?", "!", "'"]:
        s = ref + punct
        print("Testing '%s'..." % s)
        assert tokens(s) == [
            LabelToken(""),
            InsertionToken(punct, True)]
    assert tokens(ref + "...") == [
        LabelToken(""),
        InsertionToken(".", True), InsertionToken(".", True), InsertionToken(".", True)]

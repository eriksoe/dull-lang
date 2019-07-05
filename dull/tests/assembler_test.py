from dull.lexer import tokenize
from dull.assembler import tokensToCode
from dull.runtime import *

def test_empty():
    s = "all work and no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == []

def test_label_only():
    s = "All Work and no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == []

def test_push_integer():
    s = "all work abnd no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pushInteger,2)]

def test_push_integer2():
    s = "all work abnd noz play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pushInteger,2), (i_pushInteger, 26)]

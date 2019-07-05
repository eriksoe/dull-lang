from dull.lexer import tokenize
from dull.assembler import tokensToCode
from dull.runtime import *

def test_empty():
    s = "all work and no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == []

def test_label_only():
    s = "All Work and no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == []

#========== Stack operations: ========================================
def test_push_integer():
    s = "all work abnd no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pushInteger,2)]

def test_push_integer2():
    s = "all work abnd noz play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pushInteger,2), (i_pushInteger, 26)]

def test_push_marker():
    s = "all work a nd no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pushMarker,None)]

def test_pop():
    s = "all work an no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_pop,None)]

def test_swap():
    s = "all wrk and no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_swap,None)]

def test_dup():
    s = "all work aand no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_dup,None)]

#========== Arithmetic: ========================================
def test_add():
    s = "all work and no paly makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_add, None)]

def test_sub():
    s = "all work and no play mkaes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_sub, None)]

def test_mul():
    s = "all work and no lpay makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_mul, None)]

def test_div():
    s = "all work and no plya makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_div, None)]

#==================== Array operations: ==============================
def test_create_array():
    s = "all workand no play makes Jack a dull boy"
    assert tokensToCode(tokenize(s)) == [(i_createArray,None)]

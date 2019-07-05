from dull.lexer import *
from dull.runtime import *

# Code representation:
# - Resolved: (ins, arg)
# - Unresolved: (ins, tag, labelName, posInLabelMap)

# Tag values for tagging unresolved labels
LBL_UNIQUE = {}
LBL_BEFORE = {}
LBL_AFTER = {}

PUNCTUATION = ".,:;!?"
VOWELS = "aeiouy"

class SyntaxError(Exception):
    def __init__(self, msg): Error.__init__(self, msg)

def tokensToCode(tokens):
    code = []
    labelMap = dict()
    # Pass 1: convert tokens to instructions
    generateInstructions(tokens, code, labelMap)
    # Pass 2: resolve labels
    resolveLabels(code, labelMap)
    return code

def generateInstructions(tokens, code, labelMap):
    state = State(code, labelMap)
    visitor = Visitor(state)
    for t in tokens:
        t.visitWith(visitor)

def isa(c, charClass):
    return charClass.find(c)>=0

class State:
    def __init__(self, code, labelMap):
        self.code = code
        self.labelMap = labelMap
        self.curLabel = None

    def registerLabel(self, label):
        addrs = self.labelMap.get(label)
        if addrs == None:
            addrs = []
            self.labelMap[label] = addrs
        addrs.append(len(self.code))

class Visitor:
    def __init__(self, state):
        self.state = state

    def appendInstruction(self, ins):
        self.state.code.append(ins)

    def handleLabel(self, label):
        self.state.curLabel = label
        if label != "": self.state.registerLabel(label)

    def handleInsertion(self, c, atEnd):
        if c>='a' and c<='z':
            self.appendInstruction((i_pushInteger, ord(c)-ord('a')+1))
        elif c == " ":
            self.appendInstruction((i_pushMarker, None))
        elif isa(c, PUNCTUATION):
            pass # No operation; serves as part of the labelling mechanism.
        elif c == "'":
            self.appendInstruction((i_printDebugDump, None))
        else:
            raise Error("Unexpected insertion: '%s' is not recognized" % (c,))

    def handleDeletion(self, c):
        if c>="a" and c<="z":
            if isa(c, VOWELS):
                self.appendInstruction((i_swap, None))
            else:
                self.appendInstruction((i_pop, None))
        elif c==" ": 
            self.appendInstruction((i_createArray, None))
        else:  
            raise Error("Unexpected deletion: '%s' is not recognized" % (c,))
       
    def handleDoubling(self, c):
        if c>="a" and c<="z":
            self.appendInstruction((i_dup, None))
        else:  
            raise Error("Unexpected deletion: '%s' is not recognized" % (c,))

def resolveLabels(code, labelMap):
    pass

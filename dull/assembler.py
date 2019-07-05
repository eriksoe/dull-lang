from dull.lexer import *
from dull.runtime import *

# Code representation:
# - Resolved: (ins, arg)
# - Unresolved: (ins, tag, labelName, posInLabelMap)

# Tag values for tagging unresolved labels
LBL_UNIQUE = {}
LBL_BEFORE = {}
LBL_AFTER = {}

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

    def handleLabel(self, label):
        self.state.curLabel = label
        if label != "": self.state.registerLabel(label)

    def handleInsertion(self, c, atEnd):
        c = c.lower()
        if c>='a' and c<='z':
            self.state.code.append((i_pushInteger, ord(c)-ord('a')+1))
        else:
            raise Error("Unexpected insertion: '%s' is not recognized" % (c,))

def resolveLabels(code, labelMap):
    pass

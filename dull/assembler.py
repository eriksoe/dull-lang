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
    curLabel = None
    for t in tokens:
        print("DEBUG generateInstructions: token=%s/%s/%s" % (t,type(t), t.__class__))
        tokenClass = t.__class__
        if tokenClass == LabelToken:
            print("DEBUG a label: %s" % (t,))
            label = t.label
            curLabel = label
            if label != "": registerLabel(label, labelMap, code)
        elif tokenClass == InsertionToken:
            print("DEBUG an insertion: %s" % (t,))
            c = t.character.lower()
            if c>='a' and c<='z':
                code.append((i_pushInteger, ord(c)-ord('a')+1))
            else:
                raise Error("Unexpected insertion: '%s' is not recognized" % (c,))

def registerLabel(label, labelMap, code):
    addrs = labelMap.get(label)
    if addrs == None:
        addrs = []
        labelMap[label] = addrs
    addrs.append(len(code))

def resolveLabels(code, labelMap):
    pass

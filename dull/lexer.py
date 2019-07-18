import re

REFERENCE_TEXT = "all work and no play makes jack a dull boy"

#==== Tokens: ========================================================
class Token:
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __ne__(self, other): return not self.__eq__(other)
    def __repr__(self):
        clsName = "%s" % (self.__class__,)
        clsName = clsName.split(".")[-1]
        return "%s(%s)" % (clsName, self.args)
    def __hash__(self):
        return hash(self.__repr__)

class LabelToken(Token):
    def __init__(self, label):
        self.label = label
        self.args = [label]
    def visitWith(self, visitor): visitor.handleLabel(self.label)

class DoublingToken(Token):
    def __init__(self, c):
        self.character = c
        self.args = [c]
    def visitWith(self, visitor): visitor.handleDoubling(self.character)

class InsertionToken(Token):
    def __init__(self, c, atEnd = False):
        self.character = c
        self.atEnd = atEnd
        self.args = [c, atEnd]
    def visitWith(self, visitor): visitor.handleInsertion(self.character, self.atEnd)

class DeletionToken(Token):
    def __init__(self, c):
        self.character = c
        self.args = [c]
    def visitWith(self, visitor): visitor.handleDeletion(self.character)

class ReplacementToken(Token):
    def __init__(self, org, repl):
        self.original = org
        self.replacement = repl
        self.args = [org,repl]
    def visitWith(self, visitor): visitor.handleReplacement(self.org, self.replacement)

class TranspositionToken(Token):
    def __init__(self, org1, org2):
        self.original1 = org1
        self.original2 = org2
        self.args = [org1,org2]
    def visitWith(self, visitor): visitor.handleTransposition(self.original1, self.original2)

#==== Lexer entry point: ==============================================
def normalizeChar(c):
    if c=='\n': return ' '
    return c

def tokenize(src):
    state = LexerState()
    lineNo = 0
    for line in src.splitlines(True):
        lineNo += 1
        line = normalizeLine(line)
        if line=="": continue

        i = 0
        while i<len(line):
            c  = normalizeChar(line[i])
            c2 = normalizeChar(line[i+1]) if i<len(line)-1 else ' '
            c3 = normalizeChar(line[i+2]) if i<len(line)-2 else ' '
            delta_i = handleCharacter(c, c2, c3, state, lineNo)
            i += delta_i
        # Process end-of-line:
        handleCharacter(" ", " ", " ", state, lineNo)

    return state.tokens

#==== Source pre-processing (normalization): ==========================

def normalizeLine(line):
    line = line.strip()
    if line.startswith("#"): return ""
    return line
    
#==== Lexer proper - typo detector: ==========================
def handleCharacter(c, c2, c3, state, lineNo):
    lb = state.labelBuilder
    labelDone = lb.done
    refChar = state.referenceChar()

    # Identify text mutations:
    (mutToken, delta_i) = identifyMutation(state, c, c2, c3)

    if not labelDone:
        if len(state.tokens) > 0 or mutToken != None:
            # Mutation found - time to close label.
            lb.finalizeLabel()
            state.addToken(LabelToken(lb.closeAndGetLabel()))
        else:
            labelDone = lb.addCharacter(c, refChar)
            if labelDone:
                state.addToken(LabelToken(lb.closeAndGetLabel()))
                #return 0
            #else:
                #state.advanceReference()
                #return 1

    if mutToken != None:
        state.addToken(mutToken)
    return delta_i

def tryPattern(patternSpec, srcWindow, state, adv):
    match = True
    (pattern, advSrc, advRef) = patternSpec
    for (srcIdx, refIdx) in pattern:
        if srcWindow[srcIdx] != state.referenceChar(refIdx):
            match = False
            break
    if match:
        adv[0] = advSrc
        adv[1] = advRef
    return match

NO_CHANGE_PATTERN = ([(0,0)], 1,1)
DOUBLING_PATTERN = ([(0,-1),(1,0)], 1,0)
DOUBLING_PATTERN_SYNCED = ([(0,-1),(1,0),(2,1)], 2,1)
REPLACEMENT_PATTERN = ([(1,1)], 2,2)
DELETION_PATTERN = ([(0,1)], 1,2)
DELETION_PATTERN_SYNCED = ([(0,1),(1,2)], 2,3)
INSERTION_PATTERN = ([(1,0)], 1,0)
INSERTION_PATTERN_SYNCED = ([(1,0),(2,1)], 1,0)
TRANSPOSITION_PATTERN = ([(0,1),(1,0)], 2,2)
TRANSPOSITION_PATTERN_SYNCED = ([(0,1),(1,0),(2,2)], 3,3)

def identifyMutation(state, c, c2, c3):
    c = c.lower()
    c2 = c2.lower()
    c3 = c3.lower()
    adv = [0,0]

    srcWindow = [c,c2,c3]

    refChar = state.referenceChar()
    if tryPattern(NO_CHANGE_PATTERN, srcWindow, state, adv):
        token = None

    elif tryPattern(TRANSPOSITION_PATTERN_SYNCED, srcWindow, state, adv):
        token = TranspositionToken(refChar, state.referenceChar(1))
    elif tryPattern(DELETION_PATTERN_SYNCED, srcWindow, state, adv):
        token = DeletionToken(refChar)
    elif tryPattern(DOUBLING_PATTERN_SYNCED, srcWindow, state, adv):
        token = DoublingToken(c)
    elif tryPattern(INSERTION_PATTERN_SYNCED, srcWindow, state, adv):
        token = InsertionToken(c, state.isAtEnd())

    elif tryPattern(REPLACEMENT_PATTERN, srcWindow, state, adv):
        token = ReplacementToken(refChar, c)

    elif tryPattern(TRANSPOSITION_PATTERN, srcWindow, state, adv):
        token = TranspositionToken(refChar, state.referenceChar(1))
    elif tryPattern(DELETION_PATTERN, srcWindow, state, adv):
        token = DeletionToken(refChar)
    elif tryPattern(DOUBLING_PATTERN, srcWindow, state, adv):
        token = DoublingToken(c)
    elif tryPattern(INSERTION_PATTERN, srcWindow, state, adv):
        token = InsertionToken(c, state.isAtEnd())
    elif " .,:;!?'".find(c)>=0:
        # Insertion of punctuation
        token = InsertionToken(c, state.isAtEnd())
        adv = [1,0]
    else:
        refChar2 = state.referenceChar(1)
        raise Exception("Syntax error at '%s%s' (ref: '%s%s')" % (c,c2,refChar,refChar2))
    (advSrc, advRef) = adv
    state.advanceReference(advRef)
    # if token!=None:
    #     refChar2 = state.referenceChar(1)
    #     print("DEBUG: token=%s at '%s%s' (ref: '%s%s')" % (token, c,c2,refChar,refChar2))
    return (token, advSrc)

class LexerState:
    def __init__(self):
        self.refPos = 0         # Position in reference text
        self.tokens = []        # The tokens found so far
        self.labelBuilder = LabelBuilder()  # The line label
        
    def currentLine(self):
        endPos = self.src.find("\n", self.lineStart)
        if endPos<0: endPos = len(self.src)
        return self.src[self.lineStart:endPos]

    def isAtEnd(self):
        return self.refPos >= len(REFERENCE_TEXT)

    def resetLabel(self):
        self.labelBuilder = ""

    def addToLabel(self, c):
        self.labelBuilder += c
    
    def addToken(self, token):
        self.tokens.append(token)

    def referenceChar(self, delta=0):
        pos = self.refPos + delta
        return REFERENCE_TEXT[pos] if pos>=0 and pos < len(REFERENCE_TEXT) else " "

    def advanceReference(self, delta=1):
        self.refPos += delta

class LabelBuilder:
    def __init__(self):
        self.buffer = ""
        self.lastUppercasePos = -1
        self.lastSpacePos = -1
        self.nextLastSpacePos = -1
        self.done = False

    def addCharacter(self, c, refChar):
        if not self.done:
            clow = c.lower()
            if clow != refChar:
                self.finalizeLabel()
            else:
                pos = len(self.buffer)
                if c==" ":
                    self.nextLastSpacePos = self.lastSpacePos
                    self.lastSpacePos = pos
                    if self.shouldTrim():
                        self.finalizeLabel()
                elif c>="A" and c<="Z":
                    self.lastUppercasePos = pos
                if not self.done:
                    self.buffer += c
        return self.done
    
    def closeAndGetLabel(self):
        if not self.done:
            self.finalizeLabel()
        return self.buffer

    def finalizeLabel(self):
        self.done = True
        self.trimToLastIncludedWord()

    def trimToLastIncludedWord(self): # private
        if self.shouldTrim():
            cutPos = max(0, self.nextLastSpacePos)
            self.buffer = self.buffer[0:cutPos]

    def shouldTrim(self):
        return self.nextLastSpacePos >= self.lastUppercasePos

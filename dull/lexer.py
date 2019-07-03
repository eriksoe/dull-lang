import re

REFERENCE_TEXT = "all work and no play makes jack a dull boy"

#==== Tokens: ========================================================
class Token:
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __repr__(self):
        clsName = "%s" % (self.__class__,)
        clsName = clsName.split(".")[-1]
        return "%s(%s)" % (clsName, self.args)

class LabelToken(Token):
    def __init__(self, label):
        self.label = label
        self.args = [label]

class DoublingToken(Token):
    def __init__(self, c):
        self.character = c
        self.args = [c]

class InsertionToken(Token):
    def __init__(self, c):
        self.character = c
        self.args = [c]

class DeletionToken(Token):
    def __init__(self, c):
        self.character = c
        self.args = [c]

class ReplacementToken(Token):
    def __init__(self, org, repl):
        self.original = org
        self.replacement = repl
        self.args = [org,repl]

class TranspositionToken(Token):
    def __init__(self, org1, org2):
        self.original1 = org1
        self.original2 = org2
        self.args = [org1,org2]

#==== Lexer entry point: ==============================================
def tokenize(src):
    state = LexerState()
    lineNo = 0
    for line in src.splitlines(True):
        lineNo += 1
        line = normalizeLine(src)
        if line=="": continue

        i = 0
        while i<len(line):
            c = line[i]
            c2 = line[i+1] if i<len(line)-1 else ' '
            delta_i = handleCharacter(c, c2, state, lineNo)
            i += delta_i
    return state.tokens

#==== Source pre-processing (normalization): ==========================

def normalizeLine(line):
    line = line.strip()
    if line.startswith("#"): return ""
    return line
    
#==== Lexer proper - typo detector: ==========================
def handleCharacter(c, c2, state, lineNo):
    lb = state.labelBuilder
    labelDone = lb.done
    refChar = state.referenceChar()

    # Identify text mutations:
    (mutToken, delta_i) = identifyMutation(state, c, c2)

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

def identifyMutation(state, c, c2):
    c = c.lower()
    c2 = c2.lower()
    refChar = state.referenceChar()
    token = None
    #print("DEBUG identifyMutation: %s,%s ref=%s" % (c,c2,refChar))
    if c == refChar:
        if c2 == refChar and c2 != state.nextReferenceChar():
            # Doubled character.
            token = DoublingToken(c)
            (adv_i, adv_j) = (2,1)
        else:
            # No change.
            (adv_i, adv_j) = (1,1)
    else:
        nextRefChar = state.nextReferenceChar()
        #print("DEBUG identifyMutation2: %s,%s ref=%s,%s" % (c,c2,refChar, nextRefChar))
        if c == nextRefChar and c2 == refChar:
            # Transposition.
            token = TranspositionToken(refChar, nextRefChar)
            (adv_i, adv_j) = (2,2)
        elif c == nextRefChar:
            # Deletion.
            token = DeletionToken(refChar)
            (adv_i, adv_j) = (0,1)
        elif c2 == nextRefChar:
            # Replacement.
            token = ReplacementToken(refChar, c)
            (adv_i, adv_j) = (1,1)
        # TODO: end-of-line stuff.
        elif c2 == refChar: # Or c non-letter, non-space
            token = InsertionToken(c)
            (adv_i, adv_j) = (1,0)
        else:
            raise Exception("Syntax error at '%s%s' (ref: '%s%s')" % (c,c2,refChar,nextRefChar))
        
    state.advanceReference(adv_j)
    return (token, adv_i)

class LexerState:
    def __init__(self):
        self.refPos = 0         # Position in reference text
        self.tokens = []        # The tokens found so far
        self.labelBuilder = LabelBuilder()  # The line label
        
    def currentLine(self):
        endPos = self.src.indexOf("\n", self.lineStart)
        if endPos<0: endPos = len(self.src)
        return self.src[self.lineStart:endPos]

    def resetLabel(self):
        self.labelBuilder = ""

    def addToLabel(self, c):
        self.labelBuilder += c
    
    def addToken(self, token):
        self.tokens.append(token)

    def referenceChar(self):
        return REFERENCE_TEXT[self.refPos]
    def nextReferenceChar(self):
        return REFERENCE_TEXT[self.refPos+1]

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

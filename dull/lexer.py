import re

REFERENCE_TEXT = "all work and no play makes jack a dull boy"

#==== Tokens: ========================================================
class Token:
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __repr__(self):
        return "%s(%s)" % (self.__class__, self.__dict__)

class LabelToken(Token):
    def __init__(self, label):
        self.label = label

#==== Lexer entry point: ==============================================
def tokenize(src):
    state = LexerState()
    lineNo = 0
    for line in src.splitlines(True):
        lineNo += 1
        line = normalizeLine(src)
        if line=="": continue

        for i in range(0, len(line)):
            c = line[i]
            c2 = line[i+1] if i<len(line)-1 else ' '
            handleCharacter(c, c2, state, lineNo)
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
    if not labelDone:
        labelDone = lb.addCharacter(c, refChar)
        if labelDone:
            state.addToken(LabelToken(lb.closeAndGetLabel()))
        else:
            state.advanceReference()

    if labelDone:
        # Identify text mutations:
        identifyMutation(state, c, c2)

def identifyMutation(state, c, c2):
    refChar = state.referenceChar()
    # TODO:
    #print("DEBUG identifyMutation: %s->%s ref=%s" % (c,c2,refChar))
    # if c == refChar:
    #     if c2 == refChar and c2 != state.nextReferenceChar():
    #         # Doubled character.
    #     else:
    #         # No change.
    adv = True
    if adv: state.advanceReference()

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

    def advanceReference(self):
        self.refPos += 1

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
            self.buffer = self.buffer[0:self.nextLastSpacePos]

    def shouldTrim(self):
        return self.nextLastSpacePos >= self.lastUppercasePos

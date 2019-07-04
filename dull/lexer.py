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
            c3 = line[i+2] if i<len(line)-2 else ' '
            delta_i = handleCharacter(c, c2, c3, state, lineNo)
            i += delta_i
            
    # Handle end-of-file deletion, if any:
    if state.refPos != 0 and state.refPos != len(REFERENCE_TEXT):
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

def identifyMutation(state, c, c2, c3):
    c = c.lower()
    c2 = c2.lower()
    refChar = state.referenceChar()
    token = None
    #print("DEBUG identifyMutation: %s,%s ref=%s" % (c,c2,refChar))
    if c == refChar:
        # Pattern: A ~ A
        refChar2 = state.referenceChar(1)
        if c2 == refChar and c2 != refChar2 and (refChar2 == c3 or c2 != state.referenceChar(2)):
            # Pattern: (AA ~ AB but not AA ~ ABA) or AAB ~ AB
            # Doubled character.
            token = DoublingToken(c)
            (adv_i, adv_j) = (2,1)
        else:
            # No change.
            (adv_i, adv_j) = (1,1)
    else:
        # Pattern: A ~ B
        refChar2 = state.referenceChar(1)
        #print("DEBUG identifyMutation2: %s,%s ref=%s,%s" % (c,c2,refChar, refChar2))
        if c == refChar2:
            # Pattern: A ~ BA
            if c2 == refChar and c2 != state.referenceChar(2):
                # Pattern: AB ~ BA
                # Transposition.
                token = TranspositionToken(refChar, refChar2)
                (adv_i, adv_j) = (2,2)
            else:
                # Deletion.
                token = DeletionToken(refChar)
                (adv_i, adv_j) = (0,1)
        elif c2 == refChar2:
            # Pattern: AC ~ BC or AB ~ BB
            if c2 == refChar and c3 == refChar2:
                # Pattern: ABB ~ BB
                token = InsertionToken(c)
                (adv_i, adv_j) = (1,0)
            else:
                # Pattern: AC ~ BC or ABX ~ BB
                token = ReplacementToken(refChar, c)
                (adv_i, adv_j) = (1,1)
        elif c2 == refChar:
            # Pattern: AB ~ B
            token = InsertionToken(c)
            (adv_i, adv_j) = (1,0)
        # TODO: end-of-line stuff.
        else:
            raise Exception("Syntax error at '%s%s' (ref: '%s%s')" % (c,c2,refChar,refChar2))
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

    def referenceChar(self, delta=0):
        pos = self.refPos + delta
        return REFERENCE_TEXT[pos] if pos < len(REFERENCE_TEXT) else " "

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

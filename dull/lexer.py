import re

REFERENCE_TEXT = "all work and no play makes jack a dull boy"

#==== Tokens: ========================================================
class Token:
    def __eq__(self, other):
        print("DB: Token.eq: %s vs %s" % (self, other))
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __repr__(self):
        return "%s(%s)" % (self.__class__, self.__dict__)

class LabelToken(Token):
    def __init__(self, label):
        self.label = label
#    def __eq__(self, other): return 

#==== Lexer entry point: ==============================================
def tokenize(src):
    src = normalize(src)
    state = LexerState(src)
    for c in src:
        handleCharacter(c, state)
    return state.tokens

#==== Source pre-processing (normalization): ==========================

whitespaceTrimmingRe = re.compile("^[ \t]+|[ \t\r]+$", re.MULTILINE)
commentTrimmingRe = re.compile("^#.*", re.MULTILINE)
blankLineTrimmingRe = re.compile("^\n+", re.MULTILINE)
def normalize(src):
    (src,_) = whitespaceTrimmingRe.subn("", src)
    (src,_) = commentTrimmingRe.subn("", src)
    (src,_) = blankLineTrimmingRe.subn("", src)
    return src
    
#==== Lexer proper - typo detector: ==========================
def handleCharacter(c, state):
    #print("char: '%c'" % c)
    if state.refMatchPos == state.pos:
        state.addToken(LabelToken(labelFrom(state.src[state.pos:])))
    state.pos += 1

def labelFrom(s):
    i=0
    upperSeen = False
    wordEnd = 0
    while i<len(s) and i<len(REFERENCE_TEXT):
        c = s[i]
        cl = c.lower()
        if cl != REFERENCE_TEXT[i].lower():
            break
        if c != cl:
            upperSeen = True
        if c == " ":
            if not upperSeen:
                i = wordEnd
                break
            else:
                upperSeen = False
                wordEnd = i
        i += 1
    return s[0:i]

class LexerState:
    def __init__(self, src):
        self.src = src          # The program source text
        self.pos = 0            # Current read position
        self.lineNo = 1         # Current line number
        self.refPos = 0         # Position in reference text
        self.lineStart = 0      # Position of the start of the current line
        self.refMatchPos = 0    # Position in the source where current ref-matchup starts
        self.tokens = []        # The tokens found so far
        
    def setLineStart(self):
        self.lineStart = self.pos

    def lineNumber(self):
        return self.lineNo
    def columnNumber(self):
        return self.pos - self.lineStart + 1

    def currentLine(self):
        endPos = self.src.indexOf("\n", self.lineStart)
        if endPos<0: endPos = len(self.src)
        return self.src[self.lineStart:endPos]

    def addToken(self, token):
        self.tokens.append(token)

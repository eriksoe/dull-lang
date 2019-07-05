from dull.lexer import tokenize
from dull.assembler import tokensToCode
from dull.runtime import run

import sys

if len(sys.argv) < 2:
    print("Usage: python -m dull <srcfile>")
    sys.exit(1)

srcfile = sys.argv[1]
with open(srcfile, "r") as f:
    lines = f.readlines()
    src = "".join(lines)
    code = tokensToCode(tokenize(src))
    #print("DEBUG code=%s" % (code,))
    run(code)

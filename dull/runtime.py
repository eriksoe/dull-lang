#==================== Engine ====================
def run(code):
    state = EngineState()
    while True:
        ip = state.ip
        if ip >= len(code): break
        state.ip = ip + 1
        (fun,arg) = code[ip]
        fun(state, arg)

class EngineState:
    def __init__(self):
        self.ip = 0
        self.gctx = []
        self.lctx = []
        self.stack = []
        self.ctxStack = []

    def push(self, v): self.stack.append(v)
    def pop(self): return self.stack.pop()
    def peek(self): return self.stack[-1]
    def swap(self):
        st = self.stack
        (st[-1],st[-2]) = (st[-2],st[-1])
    
#==================== Instructions ====================

#==================== Stack manipulation
def i_dup(state,arg): state.push(state.peek())
def i_pop(state,arg): state.pop()
def i_swap(state,arg): state.swap()
def i_pushInteger(state,arg):
    state.push(arg)
def i_pushMarker(state,arg): pass

#====================  Arithmetic
def i_add(state,arg): state.push(state.pop() + state.pop())
def i_sub(state,arg): state.push(state.pop() - state.pop())
def i_mul(state,arg): state.push(state.pop() * state.pop())
def i_div(state,arg): pass

#====================  I/O
def i_input(state,arg): pass
def i_output(state,arg):
    v = state.pop()
    printIOList(v)
def i_printDebugDump(state,arg):
    print("/---- DUMP:")
    print("Stack: %s" % (state.stack,))
    print("\\----")

def printIOList(v):
    if type(v) == type(0):
        print(chr(v))
    else:
        for x in v:
            printIOList(x)
    
#====================  Flow control
def i_branch(state,arg): pass
def i_branchIfPositive(state,arg): pass
def i_call(state,arg): pass
def i_return(state,arg): pass

#====================  Arrays
def i_createArray(state,arg): pass
def i_arrayFetch(state,arg): pass
def i_arrayStore(state,arg): pass
def i_arrayGetSize(state,arg): pass
def i_arrayResize(state,arg): pass

#==================== Context access
def i_pushLocalContext(state,arg): pass
def i_pushGlobalContext(state,arg): pass
def i_enterScope(state,arg): pass
def i_exitScope(state,arg): pass
def i_(state,arg): pass

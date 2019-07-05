#==================== Instructions ====================

#==================== Stack manipulation
def i_dup(state,arg): pass
def i_pop(state,arg): pass
def i_swap(state,arg): pass
def i_pushInteger(state,arg): pass
def i_swap(state,arg): pass

#====================  Arithmetic
def i_add(state,arg): pass
def i_sub(state,arg): pass
def i_mul(state,arg): pass
def i_div(state,arg): pass

#====================  I/O
def i_input(state,arg): pass
def i_output(state,arg): pass
def i_printDebugDump(state,arg): pass

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

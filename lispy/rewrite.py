def lisp_eval( expr, env ):
    ### lisp_eval() is the Python definition of the canonical lisp
    ### function "eval".  This definition is ITERATIVE (not
    ### recursive), which avoids the use of the Python callstack and
    ### allows the lisp callstack to be exposed.
    
    ## Begin with simple cases (not S-expressions)
    if isatom(expr):
        return expr
    if issymbol(expr):
        return Global_Env.lookup(expr)
    if not iscode(expr):
        return Exception( None, "EVAL received an improper S-expression: %s" % expr )

    ## Everything else is for handling the case when expr is an S-expression

    The_Stack = Stack( expr, None, env )   # the bottom of the callstack
    cur_stack = The_Stack                  # the top of the callstack
    
    ## The main loop:
    while not The_Stack.isdone():
        
        ## This section handles looking up the function at the head of expr
        if not cur_stack.has_fn:
            if cur_stack.is_receiving_fn:
                cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                cur_stack.receiving_fn = False
                cur_stack.has_fn = True
            # "elif" is important here to avoid infinite loop, unlike below
            elif isatom(cur_stack.expr.car):
                cur_stack.fn = cur_stack.expr.car
                cur_stack.has_fn = True
            elif issymbol(cur_stack.expr.car):
                cur_stack.fn = cur_stack.env.lookup(expr)                
                cur_stack.has_fn = True
                ### MISSING BIT
                ### How to return an exception for failed lookup?
                ### cur_stack.make_Exception( "stuff" )?
                ### ALSO RUN A SPELL CHECK ON ALL THIS
            else:
                ## if (car expr) is itself an S-exp, put it on the stack
                cur_stack.receiving_fn = True
                cur_stack = Stack( cur_stack.expr.car,
                                   cur_stack,
                                   Environment(cur_stack.env) )
                
        ## This section handles the assembly of the arguments list
        elif not cur_stack.has_args:
            ###
            ### DON'T FORGET TO CHECK FOR METHODNESS
            ###
            if cur_stack.receiving_arg:   # analogous to the section above
                cur_stack.args_array.append(ret)
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack.receiving_arg = False
            # "if" is ok here, unlike above
            if cur_stack.arg_ptr == None:

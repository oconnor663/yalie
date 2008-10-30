opdef lisp_eval( expr, env ):
    ### lisp_eval() is the Python definition of the canonical lisp
    ### function "eval".  This definition is ITERATIVE (not
    ### recursive), which avoids the use of the Python callstack and
    ### allows the lisp callstack to be exposed.
    
    ## Begin with simple cases (not S-expressions)
    if isatom(expr):
        return expr
    if issymbol(expr):
        return Global_Env.lookup(expr)
    #
    # CHECK FOR MALFORMATTED CODE
    #

    ## Everything else is for handling the case when expr is an S-expression

    cur_stack = Stack( expr, None, env )
    
    ## The main loop:
    while True:
        
        ## This section handles looking up the function at the head of expr
        if not cur_stack.has_fn:
            if cur_stack.is_receiving_fn:
                cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                cur_stack.receiving_fn = False
                cur_stack.has_fn = True
                #
                # CHECK ERRORS HERE
                #
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
                cur_stack.receiving_arg = False
                #
                # CHECK ERRORS HERE
                #
            # "if" is ok here, unlike above
            if cur_stack.arg_ptr == None:
                cur_stack.has_args = True
            elif isform(cur_stack.fn):    # this means that the arguments should not be eval'd
                cur_stack.args_array.append(cur_stack.arg_ptr.car)
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
            ## below this point, arguments need to be evaluated
            elif isatom(cur_stack.arg_ptr.car):
                cur_stack.args_array.append(cur_stack.arg_ptr.car)
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
            elif issymbol(cur_stack.arg_ptr.car):
                cur_stack.args_array.append(cur_stack.env.lookup(cur_stack.arg_ptr.car))
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
            else:  # arg is an S-exp
                cur_stack.receiving_arg = True
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack = Stack( cur_stack.arg_ptr.car,
                                   cur_stack,
                                   Environment(cur_stack.env) )

        ## Now, fn and args_array in hand, we're going to evaluate the body of the function!
        else:

            #
            # CHECK THE VALIDITY OF THE ARGS LIST AGAINST THE FUNCTION
            # AND ADD EXCEPTION HANDLING TO ALL OF THESE
            #
            
            ## Run through the body. Lisp forms are differentiated later.
            if islisp( cur_stack.fn ):

                if cur_stack.body_ptr == None:
                    cur_stack.isdone = True
                elif isatom(cur_stack.body_ptr.car):
                    ret = cur_stack.body.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                elif issymbol(cur_stack.body_ptr.car):
                    ret = cur_stack.env.lookup(cur_stack.body_ptr.car)
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                else:
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                    cur_stack = Stack( cur_stack.body_ptr.car,
                                       cur_stack,
                                       Environment(cur_stack.env) )

            else:  # a form/func written in Python
                ret = apply( cur_stack.call, cur_stack.args_array )
                cur_stack.isdone = True

            ###CHECK FOR ERRORS

            ## The returns from Lisp forms are evaluated in the calling environment.
            if cur_stack.isdone and cur_stack.
                #
                # CHECK FOR MALFORMATTED CODE
                #
                cur_stack.ret_evaluated = True
                if isatom(ret):
                    pass
                if issymbol(ret):
                    ret = cur_stack.env.lookup(ret)
                else:
                    cur_stack
            
            ## Once everything is wrapped up, this will pop the current stack.
            if cur_stack.isdone:
                if cur_stack.parent==None:
                    return ret
                else:
                    cur_stack = cur_stack.parent


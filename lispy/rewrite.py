def lisp_eval( expr, env ):
    ### lisp_eval() is the Python definition of the canonical lisp
    ### function "eval".  This definition is ITERATIVE (not
    ### recursive), which avoids the use of the Python callstack and
    ### allows the lisp callstack to be exposed.
    
    ## Begin with simple cases (not S-expressions)
    if isatom(expr):
        return expr
    if issymbol(expr):
        return env.lookup(expr)
    #
    # CHECK FOR MALFORMATTED CODE
    #

    ## Everything else is for handling the case when expr is an S-expression

    cur_stack = Callstack( expr, None, env )
    
    ## The main loop:
    while True:
        
        ## This section handles looking up the function at the head of expr
        if not cur_stack.has_fn:
            if cur_stack.receiving_fn:
                cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                cur_stack.receiving_fn = False
                cur_stack.has_fn = True
                if islisp(ret):
                    cur_stack.body_ptr = ret.body
                cur_stack.eval_ret = isform(ret) and islisp(ret) #Python never returns code
                #
                # CHECK ERRORS HERE
                #
            # "elif" is important here to avoid infinite loop, unlike below
            elif isatom(cur_stack.expr.car):
                cur_stack.fn = cur_stack.expr.car
                cur_stack.has_fn = True
                if islisp(cur_stack.fn):
                    cur_stack.body_ptr = cur_stack.fn.body
                cur_stack.eval_ret = isform(cur_stack.fn) and islisp(cur_stack.fn)
            elif issymbol(cur_stack.expr.car):
                cur_stack.fn = cur_stack.env.lookup(cur_stack.expr.car)                
                cur_stack.has_fn = True
                if islisp(cur_stack.fn):
                    cur_stack.body_ptr = cur_stack.fn.body
                cur_stack.eval_ret = isform(cur_stack.fn) and islisp(cur_stack.fn)
                ### MISSING BIT
                ### How to return an exception for failed lookup?
                ### cur_stack.make_Exception( "stuff" )?
                ### ALSO RUN A SPELL CHECK ON ALL THIS
            else:
                ## if (car expr) is itself an S-exp, put it on the stack
                cur_stack.receiving_fn = True
                cur_stack = Callstack( cur_stack.expr.car,
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
                if islisp(cur_stack.fn):  # variables must be bound in the local env
                    for i in xrange(len(fn.arg_names)):
                        cur_stack.env.bind_sym(cur_stack.env.get_sym(fn.arg_names[i]),
                                               cur_stack.args_array[i])
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
                tmp = cur_stack.arg_ptr.car
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack = Callstack( tmp,
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
                    tmp = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                    cur_stack = Callstack( tmp,
                                           cur_stack,
                                           Environment(cur_stack.env) )

            else:  # a form/func written in Python
                ret = apply( cur_stack.fn.call, cur_stack.args_array )
                cur_stack.isdone = True

            ###CHECK FOR ERRORS

            ## The returns from Lisp forms are evaluated in the calling environment.
            if cur_stack.isdone and cur_stack.eval_ret:
                #
                # CHECK FOR MALFORMATTED CODE
                #
                cur_stack.eval_ret = False
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


class Callstack():
    def __init__( self, expr, parent, env ):
        self.expr = expr
        self.parent = parent
        self.env = env
        self.has_fn = False
        self.receiving_fn = False
        self.has_args = False
        self.receiving_arg = False
        self.args_array = []
        self.arg_ptr = expr.cdr
        ## fn, body_ptr, and eval_ret will be added by lisp_eval

class Environment():
    def __init__( self, parent ):
        self.parent = parent
        self.bindings = {}
        if parent==None:
            self.symbols = {}
    def lookup( self, sym ):
        if sym.name in self.bindings:
            return self.bindings[sym.name]
        elif self.parent:
            return self.parent.lookup(sym)
        else:
            raise RuntimeError, "MOOOOO!!!"
    def get_sym( self, name ):
        if self.parent:
            return self.parent.get_sym(name)
        elif name in self.symbols:
            return self.symbols[name]
        else:
            ret = Symbol(name)
            self.symbols[name] = ret
            return ret
    def bind_sym( self, sym, val ):
        self.bindings[sym.name] = val

class Symbol():
    def __init__( self, name ):
        self.name = name
        self.isglobal = False
        self.iskeyword = (name[0]==':')
    def __repr__( self ):
        return self.name

class Cons():
    def __init__( self, car, cdr ):
        self.car = car
        self.cdr = cdr
    def __repr__( self ):
        ret = '('
        tmp = self
        while isinstance(tmp.cdr,Cons):
            ret += repr(tmp.car) + ' '
            tmp = tmp.cdr
        if tmp.cdr==None:
            ret += repr(tmp.car)+')'
        else:
            ret += repr(tmp.car)+' . '+repr(tmp.cdr)+')'
        return ret

def isatom(expr):
    return not isinstance(expr,Symbol) and not isinstance(expr,Cons)

def issymbol(expr):
    return isinstance(expr,Symbol)

class PyCode():
    def __init__( self, call, isform=False ):
        self.call = call
        self.isform = isform

class LispCode():
    def __init__( self, body, arg_names, isform=False ):
        self.body = body
        self.arg_names = arg_names
        self.isform = isform

def islisp(expr):
    return isinstance(expr,LispCode)

def isform(expr):
    return expr.isform


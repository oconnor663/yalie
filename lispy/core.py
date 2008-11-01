def lisp_eval( expr, Global_Env ):
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

    cur_stack = Callstack( expr, None, Global_Env )
    
    ## The main loop:
    while True:
        
        ## This section handles looking up the function at the head of expr
        if not cur_stack.has_fn:
            if cur_stack.receiving_fn:
                cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                cur_stack.receiving_fn = False
                cur_stack.has_fn = True
                if ret.islisp:
                    cur_stack.body_ptr = ret.body
                cur_stack.eval_ret = ret.eval_ret
                ret.stack = cur_stack
                #
                # CHECK ERRORS HERE
                #
            # "elif" is important here to avoid infinite loop, unlike below
            elif isatom(cur_stack.expr.car):
                cur_stack.fn = cur_stack.expr.car
                cur_stack.has_fn = True
                if cur_stack.fn.islisp:
                    cur_stack.body_ptr = cur_stack.fn.body
                cur_stack.eval_ret = cur_stack.fn.eval_ret
            elif issymbol(cur_stack.expr.car):
                cur_stack.fn = cur_stack.env.lookup(cur_stack.expr.car)                
                cur_stack.has_fn = True
                if cur_stack.fn.islisp:
                    cur_stack.body_ptr = cur_stack.fn.body
                cur_stack.eval_ret = cur_stack.fn.eval_ret
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
            elif cur_stack.arg_ptr == None:
                
                cur_stack.has_args = True
                if cur_stack.fn.islisp:  # variables must be bound in the local env
                    tmp = cur_stack.fn.arg_syms
                    for a in cur_stack.args_array:
                        cur_stack.env.bind_sym(tmp.car,a)
                        tmp = tmp.cdr
                else:
                    # Python functions/forms take self as a first arg
                    cur_stack.args_array = [cur_stack.fn] + cur_stack.args_array
            elif not cur_stack.fn.eval_args:    # this means that the arguments should not be eval'd
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
            
            ## This loop first checks whether it needs to evaluate the
            ## return from a previous call
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
                    cur_stack = Callstack( ret,
                                           cur_stack,
                                           Environment(cur_stack.env) )
            
            ## Once everything is wrapped up, this will pop the current stack.
            elif cur_stack.isdone and not cur_stack.eval_ret:
                if cur_stack.parent==None:
                    return ret
                else:
                    cur_stack = cur_stack.parent

            elif cur_stack.fn.islisp:

                if cur_stack.body_ptr == None:
                    cur_stack.isdone = True
                elif isatom(cur_stack.body_ptr.car):
                    ret = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                elif issymbol(cur_stack.body_ptr.car):
                    ## Scoping rule: anything without eval_ret is lexical
                    if not cur_stack.fn.eval_ret:
                        ret = cur_stack.fn.env.lookup(cur_stack.body_ptr.car)
                    else:
                        ret = cur_stack.env.lookup(cur_stack.body_ptr.car)
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                else:
                    tmp = cur_stack.body_ptr.car
                    ## Same scoping rule as above
                    if cur_stack.fn.islisp and not cur_stack.fn.eval_ret:
                        tmp_env = cur_stack.fn.env
                    else:
                        tmp_env = cur_stack.env
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                    cur_stack = Callstack( tmp,
                                           cur_stack,
                                           Environment(tmp_env) )

            else:  # a form/func written in Python
                ret = apply( cur_stack.fn.call, cur_stack.args_array )
                cur_stack.isdone = True

            ###CHECK FOR ERRORS


class Callstack():
    def __init__( self, expr, parent, env ):
        self.expr = expr
        self.parent = parent
        self.env = env
        if isinstance(expr,Cons):
            self.has_fn = False
            self.receiving_fn = False
            self.has_args = False
            self.receiving_arg = False
            self.args_array = []
            self.arg_ptr = expr.cdr
            self.isdone = False
            ## fn, body_ptr, and eval_ret will be added by lisp_eval

class Environment():
    def __init__( self, parent ):
        self.parent = parent
        self.bindings = {}
        if parent==None:
            self.symbols = {}
            self.import_python("builtins")
    def lookup( self, sym ):
        if sym.name in self.bindings:
            return self.bindings[sym.name]
        elif self.parent:
            return self.parent.lookup(sym)
        else:
            raise RuntimeError, "MOOOOO!!! %s" % sym.name
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
    def import_python( self, module_name ):
        if module_name in dir():
            raise RuntimeError, "MOOOOOOOOOOOOOOOO!!!"
        exec "import %s" % module_name
        for i in eval("dir(%s)" % module_name):
            x = eval("%s.%s" % (module_name,i))
            if isinstance(x,PyCode):
                x.env = self
                sym = self.get_sym(x.name)
                self.bind_sym(sym,x)

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
    '''Object representation of Python functions and special forms.'''
    def __init__( self, call, name, eval_args=True, eval_ret=False ):
        self.islisp = False
        self.name = name # only used for the initial binding during import
        self.call = call
        self.eval_args = eval_args
        self.eval_ret = eval_ret
        #self.env will be set by import_python
        #self.stack will be set during evaluation

class LispCode():
    '''Object representation of Lisp functions and forms.'''
    def __init__( self, body, arg_syms, lexical_env ):
        self.islisp = True
        self.body = body
        self.arg_syms = arg_syms
        self.env = lexical_env
        self.eval_ret = (lexical_env==None)
        self.eval_args = (lexical_env!=None)

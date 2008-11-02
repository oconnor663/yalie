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
        
        ## This section first checks whether it needs to evaluate the
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
                                       cur_stack.env )
            
        ## If everything is finished, this will pop the current stack.
        elif cur_stack.isdone:
            if cur_stack.parent==None:
                return ret
            else:
                cur_stack = cur_stack.parent

        ## If we're starting a new stack, this section handles looking
        ## up the function at the head of expr
        elif not cur_stack.has_fn:
            
            if cur_stack.receiving_fn:
                cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                cur_stack.receiving_fn = False
                cur_stack.has_fn = True
                if ret.islisp:
                    cur_stack.body_ptr = ret.body
                cur_stack.eval_ret = ret.eval_ret
                #
                # CHECK ERRORS HERE
                #
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
                                       cur_stack.env )
                
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
                ## All scoping happens right here, after all arguments
                ## have been evaluated (or not, in the case of a
                ## form). Lexical scoping is given to anything that
                ## evaluates its arguments but not its return.
                if cur_stack.fn.eval_args and not cur_stack.fn.eval_ret:
                    cur_stack.env = Environment(cur_stack.fn.env)
                else:
                    cur_stack.env = Environment(cur_stack.env)

                if cur_stack.fn.islisp:  # variables must be bound in the local env
                    tmp = cur_stack.fn.arg_syms
                    for a in cur_stack.args_array:
                        cur_stack.env.bind_sym(tmp.car,a)
                        tmp = tmp.cdr
                else:
                    # Python functions/forms take (self,stack) as a first arg
                    cur_stack.args_array = [(cur_stack.fn,cur_stack)] + cur_stack.args_array

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
                                       cur_stack.env )

        ## Now, fn and args_array in hand, we're going to evaluate the body of the function!
        else:

            #
            # CHECK THE VALIDITY OF THE ARGS LIST AGAINST THE FUNCTION
            # AND ADD EXCEPTION HANDLING TO ALL OF THESE
            #

            if cur_stack.fn.islisp:

                if cur_stack.body_ptr == None:
                    cur_stack.isdone = True
                elif isatom(cur_stack.body_ptr.car):
                    ret = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                elif issymbol(cur_stack.body_ptr.car):
                    ret = cur_stack.env.lookup(cur_stack.body_ptr.car)
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                else:
                    tmp = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                    cur_stack = Callstack( tmp,
                                           cur_stack,
                                           cur_stack.env )

            else:  # a form/func written in Python
                ret = apply( cur_stack.fn.call, cur_stack.args_array )
                cur_stack.isdone = True

            ###CHECK FOR ERRORS


class Callstack():
    def __init__( self, expr, parent, env ):
        self.expr = expr
        self.parent = parent
        self.env = env
        if iscons(expr):
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
            self.unique_counter = 0
            self.import_python("builtins")
    def lookup( self, sym ):
        if sym.name in self.bindings:
            return self.bindings[sym.name]
        elif self.parent:
            return self.parent.lookup(sym)
        else:
            raise RuntimeError, "MOOOOO!!! %s" % sym.name
    def get_sym( self, name ):
        if type(name)!=type(''):
            raise RuntimeError, "Moo."
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
    def import_lisp( self, module_name ):
        input = Input(open(module_name+'.lisp',"r"))
        expr = input.read()
        while expr:
            #
            # Error check
            #
            lisp_eval(expr,self)
            #
            # Error check
            #
            expr = input.read()

class Symbol():
    def __init__( self, name ):
        self.name = name
        self.isglobal = False
        self.iskeyword = (name[0]==':')
    def __repr__( self ):
        if type(self.name)!=type(''):
            raise RuntimeError, "Moooo..."
        return self.name

class Cons():
    def __init__( self, car, cdr ):
        self.car = car
        self.cdr = cdr
    def __repr__( self ):
        ret = '('
        tmp = self
        while iscons(tmp.cdr):
            ret += repr(tmp.car) + ' '
            tmp = tmp.cdr
        if tmp.cdr==None:
            ret += repr(tmp.car)+')'
        else:
            ret += repr(tmp.car)+' . '+repr(tmp.cdr)+')'
        return ret
    def py_list( self ):
        ret = []
        tmp = self
        while tmp != None:
            ret.append(tmp.car)
            tmp = tmp.cdr
        return ret

def list2cons( list ):
    ret = None
    for i in range(len(list)-1,-1,-1):
        ret = Cons(list[i],ret)
    return ret

def isatom(expr):
    return not isinstance(expr,Symbol) and not isinstance(expr,Cons)

def issymbol(expr):
    return isinstance(expr,Symbol)

def iscons(expr):
    return isinstance(expr,Cons)

def iscode(expr):
    '''Checks the well-formedness of an S-expression.'''
    if not iscons(expr):
        return True
    elif not iscons(expr.cdr) and expr.cdr!=None:
        return False
    elif not iscons(expr.car):
        return iscode(expr.cdr)
    else:
        return iscode(expr.car) and iscode(expr.cdr)

class PyCode():
    '''Object representation of Python functions and special forms.'''
    def __init__( self, call, name, eval_args=True, eval_ret=False ):
        self.islisp = False
        self.name = name # only used for the initial binding during import
        self.call = call # call must take a specific form. see builtins.
        self.eval_args = eval_args
        self.eval_ret = eval_ret
        #self.env will be set by import_python

class LispCode():
    '''Object representation of Lisp functions and forms.'''
    def __init__( self, arg_syms, body, lexical_env ):
        self.islisp = True
        self.body = body  # a cons list
        self.arg_syms = arg_syms  # another cons list
        self.env = lexical_env
        self.eval_ret = (lexical_env==None)
        self.eval_args = (lexical_env!=None)

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
    if not iscode(expr):
        return Exception("Eval received improper list: %s" % expr, None)

    ## Everything else is for handling the case when expr is an S-expression

    cur_stack = Callstack( expr, None, Global_Env )
    
    ## The main loop:
    while True:
        
        ## This section first checks whether it needs to evaluate the
        ## return from a previous call
        if cur_stack.isdone and cur_stack.eval_ret:
            cur_stack.eval_ret = False
            if isatom(ret):
                pass
            elif issymbol(ret):
                # eval needs to happen in the calling env. lisp forms
                # will have dropped a scope.
                tmp_env = cur_stack.env.parent if cur_stack.fn.islisp else cur_stack.env
                ret = tmp_env.lookup(ret)
                if iserror(ret):
                    ret = Exception( "In "+lisp_repr(cur_stack.expr)+':', ret )
            elif iserror(ret):
                ret = Exception("In return from "+lisp_repr(cur_stack.expr)+':', ret )
            else:
                if not iscode(ret):
                    ret = Exception("Form %s returned improper list: %s" % (cur_stack.expr,ret), None )
                else:
                ### SHOULD THE FOLLOWING LINE BE HERE
                #tmp_env = cur_stack.env.parent if cur_stack.fn.islisp else cur_stack.env
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
                if iserror(ret):
                    cur_stack.isdone = True
                    ret = Exception( "In "+lisp_repr(cur_stack.expr.car)+':', ret )
                else:
                    cur_stack.fn = ret   # ret is set when cur_stack returns, see below
                    cur_stack.receiving_fn = False
                    cur_stack.has_fn = True
                    if ret.islisp:
                        cur_stack.body_ptr = ret.body
                    cur_stack.eval_ret = ret.eval_ret
            elif isatom(cur_stack.expr.car):
                cur_stack.fn = cur_stack.expr.car
                cur_stack.has_fn = True
                if not isinstance(cur_stack.fn,LispCode) and not isinstance(cur_stack.fn,PyCode):
                    cur_stack.isdone = True
                    ret = Exception( "%s is not a function" % cur_stack.fn, None )
                else:
                    if cur_stack.fn.islisp:
                        cur_stack.body_ptr = cur_stack.fn.body
                    cur_stack.eval_ret = cur_stack.fn.eval_ret
            elif issymbol(cur_stack.expr.car):
                tmp = cur_stack.env.lookup(cur_stack.expr.car)                
                if iserror(tmp):
                    cur_stack.isdone = True
                    ret = Exception( "In "+lisp_repr(cur_stack.expr)+':', tmp )
                else:
                    cur_stack.fn = tmp
                    cur_stack.has_fn = True
                    if cur_stack.fn.islisp:
                        cur_stack.body_ptr = cur_stack.fn.body
                    cur_stack.eval_ret = cur_stack.fn.eval_ret
            else:
                ## if (car expr) is itself an S-exp, put it on the stack
                cur_stack.receiving_fn = True
                cur_stack = Callstack( cur_stack.expr.car,
                                       cur_stack,
                                       cur_stack.env )
                
        ## This section handles the assembly of the arguments list
        elif not cur_stack.has_args:
            if cur_stack.receiving_arg:   # analogous to the section above
                if iserror(ret):
                    cur_stack.isdone = True
                    ret = Exception( "In "+lisp_repr(cur_stack.expr.car)+':', ret )
                else:
                    cur_stack.args_array.append(ret)
                    cur_stack.receiving_arg = False
            elif cur_stack.arg_ptr == None:
                cur_stack.has_args = True
                
                #
                # CHECK THE VALIDITY OF THE ARGUMENTS LIST
                #
                
                ## All scoping happens right here, after all arguments
                ## have been evaluated (or not, in the case of a
                ## form). Lexical scoping is given to any lisp code
                ## evaluates its arguments but not its return. Python
                ## code is not scoped here. (But it is scoped by the
                ## Python interpreter.)

                if cur_stack.fn.islisp:
                    if cur_stack.fn.eval_args and not cur_stack.fn.eval_ret:
                        cur_stack.env = Environment(cur_stack.fn.env)
                    else:
                        cur_stack.env = Environment(cur_stack.env)
                    ## Bind arguments to the new scope.
                    tmp = cur_stack.fn.arg_syms
                    for a in cur_stack.args_array:
                        cur_stack.env.bind_sym(tmp.car,a)
                        tmp = tmp.cdr
                else:
                    # Python functions/forms take (self,stack) as a first arg
                    cur_stack.args_array = [(cur_stack.fn,cur_stack)] + cur_stack.args_array

            elif not cur_stack.fn.eval_args and (cur_stack.fn.islisp or \
                    cur_stack.arg_index not in cur_stack.fn.eval_indices):   # this means that the argument
                cur_stack.args_array.append(cur_stack.arg_ptr.car)           # should not be eval'd
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack.arg_index += 1
            ## below this point, arguments need to be evaluated
            elif isatom(cur_stack.arg_ptr.car):
                cur_stack.args_array.append(cur_stack.arg_ptr.car)
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack.arg_index += 1
            elif issymbol(cur_stack.arg_ptr.car):
                tmp = cur_stack.env.lookup(cur_stack.arg_ptr.car)
                if iserror(tmp):
                    cur_stack.isdone = True
                    ret = Exception( "In "+lisp_repr(cur_stack.expr)+':', tmp )
                else:
                    cur_stack.args_array.append(tmp)
                    cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                    cur_stack.arg_index += 1
            else:  # arg is an S-exp
                cur_stack.receiving_arg = True
                tmp = cur_stack.arg_ptr.car
                cur_stack.arg_ptr = cur_stack.arg_ptr.cdr
                cur_stack.arg_index += 1
                cur_stack = Callstack( tmp,
                                       cur_stack,
                                       cur_stack.env )

        ## Now, fn and args_array in hand, we're going to evaluate the body of the function!
        else:

            ## The first bit just checks if the previous body form returned an error.
            if cur_stack.receiving_body:
                cur_stack.receiving_body = False
                if iserror(ret):
                    cur_stack.isdone = True
                    ret = Exception( "In "+lisp_repr(cur_stack.expr.car)+':', ret )                

            elif cur_stack.fn.islisp:

                if cur_stack.body_ptr == None:
                    cur_stack.isdone = True
                elif isatom(cur_stack.body_ptr.car):
                    ret = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                elif issymbol(cur_stack.body_ptr.car):
                    ret = cur_stack.env.lookup(cur_stack.body_ptr.car)
                    if iserror(ret):
                        cur_stack.isdone = True
                        ret = Exception( "In "+lisp_repr(cur_stack.expr.car)+':', ret )
                    else:
                        cur_stack.body_ptr = cur_stack.body_ptr.cdr
                else:
                    tmp = cur_stack.body_ptr.car
                    cur_stack.body_ptr = cur_stack.body_ptr.cdr
                    cur_stack.receiving_body = True
                    cur_stack = Callstack( tmp,
                                           cur_stack,
                                           cur_stack.env )

            else:  # a form/func written in Python
                ret = apply( cur_stack.fn.call, cur_stack.args_array )
                if iserror(ret):
                    ret = Exception( "In "+lisp_repr(cur_stack.expr.car)+':', ret )
                # and whether or not there was an error...
                cur_stack.isdone = True


class Callstack():
    def __init__( self, expr, parent, env ):
        self.expr = expr
        self.parent = parent
        self.env = env
        self.isdone = False
        self.eval_ret = False
        if iscons(expr):
            self.has_fn = False
            self.receiving_fn = False
            self.has_args = False
            self.receiving_arg = False
            self.args_array = []
            self.arg_ptr = expr.cdr
            self.arg_index = 0 #for selective evaluation
            self.receiving_body = False
            ## fn, body_ptr, and eval_ret will be added by lisp_eval

class Exception():
    def __init__(self, string, child ):
        self.string = string
        self.child = child
    def __repr__(self):
        if self.child:
            return self.string+'\n'+lisp_repr(self.child)
        else:
            return self.string

class Environment():
    def __init__( self, parent ):
        self.parent = parent
        self.bindings = {}
        if parent==None:
            self.symbols = {}
            self.unique_counter = 0
            self.import_python("builtins")
    def lookup( self, sym ):
        if sym.iskeyword:
            return Exception( "Tried to look up keyword %s"%sym, None )
        elif sym.name in self.bindings:
            return self.bindings[sym.name]
        elif self.parent:
            return self.parent.lookup(sym)
        else:
            return Exception( "Variable not bound: %s"%sym, None )
    def get_sym( self, name ):
        if type(name)!=type(''):
            raise RuntimeError, "Moo."
        elif name[0]==':':
            return Symbol(name) #keywords aren't interned
        elif self.parent:
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
            ret += lisp_repr(tmp.car) + ' '
            tmp = tmp.cdr
        if tmp.cdr==None:  # this handles () within a list. toplevel is handled separately
            ret += lisp_repr(tmp.car)+')'
        else:
            ret += lisp_repr(tmp.car)+' . '+lisp_repr(tmp.cdr)+')'
        return ret
    def py_list( self ):
        ret = []
        tmp = self
        while tmp != None:
            ret.append(tmp.car)
            tmp = tmp.cdr
        return ret

def lisp_repr( expr ):
    if expr==None:
        return '()'
    else:
        return repr(expr)

def list2cons( list ):
    ret = None
    for i in range(len(list)-1,-1,-1):
        ret = Cons(list[i],ret)
    return ret

def isatom(expr):
    return not isinstance(expr,Symbol) and not isinstance(expr,Cons)

def iserror(expr):
    return isinstance(expr,Exception)

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
    def __init__( self, call, name, eval_args=True, eval_ret=False, eval_indices = [] ):
        self.islisp = False
        self.name = name # only used for the initial binding during import
        self.call = call # call must take a specific form. see builtins.
        self.eval_args = eval_args
        self.eval_ret = eval_ret
        self.eval_indices = eval_indices  #allows selective evaluation of arguments (intended for forms)
        #self.env will be set by import_python

class LispCode():
    '''Object representation of Lisp functions and forms.'''
    def __init__( self, arg_syms, body, lexical_env ):
        self.islisp = True
        self.body = body  # a cons list
        self.arg_syms = arg_syms  # another cons list
        if lexical_env!=None:
            self.env = lexical_env
        self.eval_ret = (lexical_env==None)
        self.eval_args = (lexical_env!=None)

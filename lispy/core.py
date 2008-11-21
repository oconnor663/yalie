import string

# A global variable to handle how () is printed
NIL_REPR = 'nil'

class Callstack():
    def __init__( self, expr, parent, env ):
        self.expr = expr # assumed to be an s-expr
        self.parent = parent
        self.env = env
        self.isdone = False
        self.eval_ret = False
        self.has_fn = False
        self.receiving_fn = False
        self.has_args = False
        self.receiving_arg = False
        self.received_args = None
        self.arg_ptr = expr.cdr
        self.arg_index = 0 #for selective evaluation
        self.avoid_arg_check = False #used by call
        self.receiving_body = False
        ## fn, pos_args, kw_args, used_kwds, body_ptr, and eval_ret will be added by lisp_eval

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
    def __init__( self, parent, symbols, bindings ):
        self.parent = parent
        self.symbols = symbols
        self.bindings = bindings
        if parent==None:
            self.unique_counter = 0
            self.import_python("builtins")
    def lookup( self, sym ):
        if type(sym)==type(''):
            return self.lookup(self.get_sym(sym)) # for strings
        elif not issymbol(sym):
            return Exception( "Cannot dereference %s" % sym, None )
        elif sym.name in self.bindings.keys():
            return self.bindings[sym.name]
        elif self.parent:
            return self.parent.lookup(sym)
        elif sym.iskeyword: #keywords always self-evaluate
            if sym.name in self.bindings.keys():
                return self.bindings[sym.name]
            else:
                self.bindings[sym.name] = sym
                return sym
        else:
            return Exception( "Variable not bound: %s"%sym, None )
    def get_sym( self, name ):
        if type(name)!=type(''):
            raise RuntimeError, "Moo."
        elif '' in name.split(':')[1 if name[0]==':' else 0:]:
            return Exception( "Not a legal symbol name: %s" % name, None )
        elif name[0]==':':
            return Symbol(name) #keywords aren't interned
        elif name in self.symbols:
            return self.symbols[name]
        else:
            ret = Symbol(name)
            self.symbols[name] = ret
            return ret
    def bind_sym( self, sym, val ):
        if not issymbol(sym):
            return Exception( "Cannot bind nonsymbol: %s" % sym, None )
        elif sym.iskeyword:
            return Exception( "Cannot bind keyword: %s" % sym, None )
        else:
            self.bindings[sym.name] = val
            return True
    def import_python( self, module_name ):
        if module_name in dir():
            raise RuntimeError, "MOOOOOOOOOOOOOOOO!!!"
        exec "import %s" % module_name
        for i in eval("dir(%s)" % module_name):
            x = eval("%s.%s" % (module_name,i))
            if isinstance(x,PyCode):
                x.env = self
                x.rest_arg = self.get_sym("rest")
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
        return string.upper(self.name)
    def kw2sym( self, env ):
        if not self.iskeyword:
            raise RuntimeError, "Keyword Moo..."
        else:
            return env.get_sym(self.name[1:])

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
        while self != None:
            ret.append(self.car)
            self = self.cdr
        return ret
    def reverse( self, work=None ):
        ret = None
        while self:
            ret = Cons(self.car,ret)
            self = self.cdr
        return ret

def lisp_repr( expr ):
    if expr==None:
        return NIL_REPR
    else:
        return repr(expr)

def list2cons( list ):
    ret = None
    for i in range(len(list)-1,-1,-1):
        ret = Cons(list[i],ret)
    return ret

def isatom(expr):
    return not isinstance(expr,Symbol) and not isinstance(expr,Cons) and not isinstance(expr,Exception)

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
        self.pos_args = None
        self.rest_arg = None # will be set by import_python
        self.kw_args = None
        self.name = name # only used for the initial binding during import
        self.call = call # call must take a specific form. see builtins.
        self.eval_args = eval_args
        self.eval_ret = eval_ret
        self.eval_indices = eval_indices  #allows selective evaluation of arguments (intended for forms)
        self.env = None # will be set by import_python

class LispCode():
    '''Object representation of Lisp functions and forms.'''
    def __init__( self, pos_args, rest_arg, is_body, kw_args, body, lexical_env ):
        self.islisp = True
        self.pos_args = pos_args
        self.rest_arg = rest_arg
        self.is_body = is_body
        self.kw_args = kw_args
        self.body = body
        if lexical_env!=None:
            self.env = lexical_env
        self.eval_ret = (lexical_env==None)
        self.eval_args = (lexical_env!=None)
        self.no_scope = False # for the "do" construct

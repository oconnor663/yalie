def lisp_eval( expr, E ):
    if isinstance(expr,Symbol):
        ret = E.symbol_value(expr)
    elif isinstance(expr,Cons):
        f = lisp_eval(expr.car(),E)
        if isinstance(f,Exception):
            return f #which is an exception
        rest = expr.cdr().python_list()
        if isinstance(rest,Exception):
            return rest #which is an exception
        if (isinstance(f,PyFunction) or
            isinstance(f,LispFunction)):
            rest = [ lisp_eval(i,E) for i in rest ]
            for i in rest:
                if isinstance(i,Exception):
                    return Exception(i,'In "%s":'%tostring(expr.car()))
            ret = f.apply(rest,E)
            if isinstance(ret,Exception):
                ret = Exception(ret, 'In "%s":'% tostring(expr.car()))
        elif (isinstance(f,SpecialForm) or
              isinstance(f,LispMacro)):
            ret = f.apply(rest,E)
            if isinstance(ret,Exception):
                ret = Exception(ret, 'In "%s":'% tostring(expr.car()))
        else:
            ret = Exception( None, '"%s" is not a function' % tostring(expr.car()))
    else:
        ret = expr
    return ret

def tostring( val, in_cons = False ):
    ret = ""
    if isinstance(val,Cons):
        if not in_cons:
            ret += "("
        ret += tostring( val.car() )
        if isinstance(val.cdr(),Nil):
            ret += ")"
        elif isinstance(val.cdr(),Cons):
            ret += " " + tostring(val.cdr(),True)
        else:
            ret += " . " + tostring(val.cdr()) + ")"
    elif isinstance(val,Symbol):
        ret = val.name
    elif isinstance(val,Nil):
        ret = "()"
    elif isinstance(val,Exception):
        ret = val.text
        if val.child:
            ret += '\n' + tostring(val.child)
    elif val==None:
        ret = ''
    else:
        ret = str(val)
    return ret

def is_true(val):
    if isinstance(val,Nil): return False
    elif val==0: return False
    else: return True

class Callstack():
    def __init__( self ):
        self.stack = Nil()

class Block():
    ### Everything with a &body (including a whole code file)
    ### will implicitly drop a block. All blocks can contain
    ### (tag x) and (goto x) forms.
    def __init__( self, body ):
        self.body = body # Py list of lisp expressions
        

class Exception():
    def __init__( self, child, text ):
        self.child = child
        self.text = text

class Environment():
    def __init__( self, parent ):
        self.parent = parent
        self.bindings = {}
        if self.parent==None:
            self.symbols = []
    def get_symbol( self, name ):
        if self.parent: #only the global environ stores Symbol objects
            return self.parent.get_symbol(name)
        else:
            hits = [ sym for sym in self.symbols if sym.name==name ]
            if hits:
                return hits[0]
            else:
                sym = Symbol(name)
                self.symbols.append(sym)
                return sym
    def symbol_value( self, sym ):
        try:
            return self.bindings[sym.name]
        except KeyError:
            if self.parent:
                return self.parent.symbol_value(sym)
            else:
                return Exception(None, 'Symbol "%s" is undefined.'%sym.name)
    def bind_symbol( self, sym, val ):
        self.bindings[sym.name] = val

class Symbol():
    def __init__( self, name ):
        self.name = name
        self.is_global = False

def make_cons_list( py_list ):
    ret = Nil()
    for i in range(len(py_list)-1,-1,-1):
        ret = Cons(py_list[i],ret)
    return ret
        
class Cons():
    def __init__( self, ar, dr ):
        self.ar = ar
        self.dr = dr
    def car( self ): return self.ar
    def cdr( self ): return self.dr
    def python_list( self ):
        ret = [ self.ar ]
        next = self.dr
        while not isinstance(next,Nil):
            if not isinstance(next,Cons):
                return Exception( None, "Improper use of dotted list." )
            ret.append(next.ar)
            next = next.dr
        return ret

class Nil():
    def python_list( self ): return []

class PyFunction():
    def __init__( self, body, E ):
        self.body = body  #a Python function object
        self.E = E
    def apply( self, args, call_E ):
        hung_E = Environment(self.E)
        ## not a recursive function; don't be confused
        for i in args:
            if isinstance(i,Exception):
                return i
        return apply(self.body,[hung_E,args]) #arg evaluation is handled by lisp_eval

def py_eval( E, args ):
    if len(args)!=1:
        return Exception(None, "Expected 1 argument. Got %i."%len(args))
    return lisp_eval(args[0],E)
def py_cons( E, args ):
    if len(args)!=2:
        return Exception(None, "Expected 2 arguments. Received %i." % len(args))
    return Cons(args[0],args[1])
def py_car( E,args ):
    if len(args)!=1:
        return Exception(None, "Expected 1 argument. Received %i." % len(args))
    if not isinstance(args[0],Cons):
        return Exception(None, "Expected a cons cell.")
    return args[0].car()
def py_cdr( E,args ):
    if len(args)!=1:
        return Exception(None, "Expected 1 argument. Received %i." % len(args))
    if not isinstance(args[0],Cons):
        return Exception(None, "Expected a cons cell.")
    return args[0].cdr()
def py_plus( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")
    return sum(args)
def py_minus( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")
    if len(args)<1:
        return Exception(None, "Expected at least one argument.")
    if len(args)==1:
        return -(args[0])
    else:
        return args[0]-sum(args[1:])
def py_times( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")    
    return reduce( lambda x,y:x*y, args, 1 )
def py_divide( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")
    if len(args)!=2:
        return Exception( None, "Expected 2 args. Received %i." % len(args))
    return reduce( lambda x,y:x/y, args )
def py_modulo( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")
    if len(args)!=2:
        return Exception( None, "Expected 2 args. Received %i." % len(args))
    return args[0]%args[1]
def py_equal( E, args ):
    if len(args)!=2:
        return Exception( None, "Expected 2 args. Received %i." % len(args))
    return args[0]==args[1]
def py_less( E, args ):
    for i in args:
        if type(i)!=type(1) and type(i)!=type(1.0):
            return Exception(None, "Expected numbers only.")
    if len(args)!=2:
        return Exception( None, "Expected 2 args. Received %i." % len(args))
    return args[0]<args[1]
def py_and( E, args ):
    if len(args)!=2:
        return Exception( None, "Expected 2 args. Received %i." % len(args))
    return args[0] and args[1]
def py_not( E, args ):
    if is_true(args[0]):
        return Nil()
    else:
        return 1
def py_print( E, args ):
    for i in args:
        print tostring(i),
    print
def py_listp( E, args ):
    return isinstance(args[0],Cons) or isinstance(args[0],Nil)
def py_nullp( E, args ):
    if not isinstance(args[0],Nil) and not isinstance(args[0],Cons):
        return Exception(None,'"null?" expects a list')
    return isinstance(args[0],Nil)


fn_bindings = (("eval",py_eval),
               ("cons",py_cons),
               ("car",py_car),
               ("cdr",py_cdr),
               ("+",py_plus),
               ("-",py_minus),
               ("*",py_times),
               ("/",py_divide),
               ("%",py_modulo),
               ("=",py_equal),
               ("<",py_less),
               ("and", py_and),
               ("not",py_not),
               ("print",py_print),
               ("isls",py_listp),
               ("null",py_nullp))

class LispFunction():
    def __init__( self, arg_list, has_rest, rest_sym, body, E ):
        self.arg_list = arg_list    #a list of Lisp symbols
        self.has_rest = has_rest
        self.rest_sym = rest_sym
        self.body = body            #a list of Lisp expressions
        self.E = E
    def apply( self, args, call_E ):
        if len(args)!=len(self.arg_list) \
                and not (self.has_rest and len(args)>len(self.arg_list)):
            return Exception(None,
                             "Expected %i arguments. Received %i." \
                                 % (len(self.arg_list),len(args)))
        hung_E = Environment(self.E)
        for i,a in enumerate(self.arg_list):
            val = args[i] #evaluation of this is handled by lisp_eval
            if isinstance(val,Exception):
                return val
            hung_E.bind_symbol( a,val )
        if self.has_rest:
            rest = []
            for i,a in enumerate(args[len(self.arg_list):]):
                val = a #as above
                if isinstance(val,Exception):
                    return val
                rest.append(val)
            hung_E.bind_symbol( self.rest_sym, make_cons_list(rest) )
        for expr in self.body:
            ret = lisp_eval( expr, hung_E )
            if isinstance(ret,Exception):
                return ret
        return ret

class LispMacro():
    def __init__( self, arg_list, has_rest, rest_sym, body, E ):
        self.arg_list = arg_list
        self.has_rest = has_rest
        self.rest_sym = rest_sym
        self.body = body
        self.E = E
    def apply( self, args, call_E ):
        if len(args)!=len(self.arg_list) \
                and not (self.has_rest and len(args)>len(self.arg_list)):
            return Exception(None,
                             "Expected %i arguments. Received %i." \
                                 % (len(self.arg_list),len(args)))
        hung_E = Environment(self.E)
        for i,a in enumerate(self.arg_list):
            hung_E.bind_symbol( a,args[i] )
        if self.has_rest:
            hung_E.bind_symbol( self.rest_sym,
                                make_cons_list(args[len(self.arg_list):]))
        for expr in self.body:
            ret = lisp_eval( expr, hung_E )
            if isinstance(ret,Exception):
                return ret
        return lisp_eval(ret,call_E) ## <--- MACRO TIME!!!

class SpecialForm():
    def __init__( self, body ):
        self.body = body
    def apply( self, args, call_E ):
        return apply( self.body, [call_E, args] )

def py_quote( E, args ):
    if len(args)!=1:
        return Exception(None, "Expected 1 argument. Received %i."%len(args))
    arg = args[0]
    if isinstance( arg, Cons ):
        if arg.car() == E.get_symbol("unquote"):
            if isinstance(arg.cdr(),Nil):
                return Exception(None,"unquote needs an argument")
            elif not isinstance(arg.cdr().cdr(),Nil):
                return Exception(None,"unquote received too many arguments")
            else:
                return lisp_eval(arg.cdr().car(),E)
        else:
            arg = arg.python_list()
            for i in range(len(arg)-1,-1,-1):
                if isinstance(arg[i],Cons) and arg[i].car()==E.get_symbol("unquote-splice"):
                    if isinstance(arg[i].cdr(),Nil):
                        return Exception(None,"unquote-splice needs an argument")
                    elif not isinstance(arg[i].cdr().cdr(),Nil):
                        return Exception(None,"unquote-splice received too many arguments")
                    else:
                        lower_level = lisp_eval(arg[i].cdr().car(),E).python_list()
                        arg = arg[:i] + lower_level + arg[i+1:]
                else:
                    arg[i] = py_quote(E,[arg[i]])
            return make_cons_list(arg)
    else:
        return arg
def py_lambda( E, args ):
    if not isinstance(args[0],Cons) and not isinstance(args[0],Nil):
        return Exception(None, "Lambda requires an argument list.")
    lambda_args = args[0].python_list()
    ### hack for &rest
    names = [i.name for i in lambda_args]
    has_rest = False
    rest_sym = Nil()
    if "&rest" in names:
        index = names.index("&rest")
        has_rest = True
        rest_sym = lambda_args[index+1]
        lambda_args = lambda_args[:index]
    # </hack>
    if isinstance(lambda_args,Exception):
        return lambda_args #which is an exception
    body = args[1:]
    return LispFunction( lambda_args, has_rest, rest_sym, body, E )
def py_define( E, args ):
    if len(args)<2:
        return Exception(None, "Expected at least 2 arguments. "
                         "Received %i."%len(args))
    if isinstance(args[0],Symbol):
        if len(args)>2:
            return Exception(None, "Define received too many arguments.")
        val = lisp_eval(args[1],E)
        if isinstance(val,Exception):
            return val #which is an exception
        E.bind_symbol(args[0],val)
    elif isinstance(args[0],Cons):
        lambda_args = args[0].python_list()
        if len(lambda_args)==0:
            return Exception(None, "Empty args list.")
        if isinstance(lambda_args,Exception):
            return Exception(lambda_args, "Couldn't parse args list.")
        ### hack for &rest
        names = [i.name for i in lambda_args]
        has_rest = False
        rest_sym = Nil()
        if "&rest" in names:
            index = names.index("&rest")
            has_rest = True
            rest_sym = lambda_args[index+1]
            lambda_args = lambda_args[:index]
        # </hack>
        fun = LispFunction( lambda_args[1:], has_rest, rest_sym, args[1:], E )
        E.bind_symbol(lambda_args[0],fun)
    else:
        return Exception(None, "Malformed definition.")
def py_defglobal( E, args ):
    bind_E = E.parent
    while bind_E.parent:
        bind_E = bind_E.parent
    if len(args)<2:
        return Exception(None, "Expected at least 2 arguments. "
                         "Received %i."%len(args))
    if isinstance(args[0],Symbol):
        if len(args)>2:
            return Exception(None, "Define received too many arguments.")
        val = lisp_eval(args[1],E)
        if isinstance(val,Exception):
            return val #which is an exception
        bind_E.bind_symbol(args[0],val)
    elif isinstance(args[0],Cons):
        lambda_args = args[0].python_list()
        if len(lambda_args)==0:
            return Exception(None, "Empty args list.")
        if isinstance(lambda_args,Exception):
            return Exception(lambda_args, "Couldn't parse args list.")
        ### hack for &rest
        names = [i.name for i in lambda_args]
        has_rest = False
        rest_sym = Nil()
        if "&rest" in names:
            index = names.index("&rest")
            has_rest = True
            rest_sym = lambda_args[index+1]
            lambda_args = lambda_args[:index]
        # </hack>
        fun = LispFunction( lambda_args[1:], has_rest, rest_sym, args[1:], E )
        bind_E.bind_symbol(lambda_args[0],fun)
    else:
        return Exception(None, "Malformed definition.")
def py_defmacro( E, args ):
    if len(args)<2:
        return Exception(None, "Expected at least 2 arguments. "
                         "Received %i."%len(args))
    if isinstance(args[0],Cons):
        lambda_args = args[0].python_list()
        if len(lambda_args)==0:
            return Exception(None, "Empty args list.")
        if isinstance(lambda_args,Exception):
            return Exception(lambda_args, "Couldn't parse args list.")
        ### hack for &rest
        names = [i.name for i in lambda_args]
        has_rest = False
        rest_sym = Nil()
        if "&rest" in names:
            index = names.index("&rest")
            has_rest = True
            rest_sym = lambda_args[index+1]
            lambda_args = lambda_args[:index]
        # </hack>
        macro = LispMacro( lambda_args[1:], has_rest, rest_sym, args[1:], E )
        E.bind_symbol(lambda_args[0],macro)
    else:
        return Exception(None, "Malformed macro definition.")

def is_true(val):
    if isinstance(val,Nil): return False
    elif val==0: return False
    else: return True
def py_if( E, args ):
    if len(args)!=2 and len(args)!=3:
        return Exception(None, "Expected 2 or 3 arguments. Received %i."\
                             %len(args))
    cond = lisp_eval(args[0],E)
    if isinstance(cond,Exception):
        return cond
    if is_true(cond):
        return lisp_eval(args[1],E)
    else:
        if len(args)==2:
            return Nil()
        else:
            return lisp_eval(args[2],E)

class Break():
    pass

def py_while( E, args ):
    ret = Nil()
    while True:
        cond = lisp_eval(args[0],E)
        if isinstance(cond,Exception): return cond
        if not is_true(cond):
            break
        broken = False
        for i in args[1:]:
            ret = lisp_eval(i,E)
            if isinstance(ret,Exception):
                return ret
            if isinstance(ret,Break):
                broken = True
                break
        if broken:
            return Nil()
    return ret
def py_break( E, args ):
    return Break()
def py_funcall( E, args ):
    new_args = lisp_eval(args[1],E).python_list()
    return lisp_eval(args[0],E).apply(new_args,E) ### NB: this apply circumvents argument evaluation
                                                  ###     that is usually done by lisp_eval
    

sf_bindings = (("quote",py_quote),
               ("fn",py_lambda),
               ("def",py_define),
               ("def-global",py_defglobal),
               ("if",py_if),
               ("while",py_while),
               ("break",py_break),
               ("deform",py_defmacro),
               ("call",py_funcall))

Global_E = Environment(None)
variable_bindings = (("t",Global_E.get_symbol('t')),
                     ("nil",Nil()))

for i in fn_bindings:
    Global_E.bind_symbol(Global_E.get_symbol(i[0]),PyFunction(i[1],Global_E))
for i in sf_bindings:
    Global_E.bind_symbol(Global_E.get_symbol(i[0]),SpecialForm(i[1]))
for i in variable_bindings:
    Global_E.bind_symbol(Global_E.get_symbol(i[0]),i[1])

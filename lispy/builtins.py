from core import *

### NB: PyCode objects are assumed to be functions by default. That
### is, they are assumed to implicitly evaluate their arguments and
### not their returns. Special forms modify one or both of those
### behaviors by explicitly passing third and fourth arguments to the
### PyCode constructor.
###
### NB: All PyCode calls must expect a context tuple (self,callstack)
### as their first argument before any other arguments supplied by the
### call in lisp. This tuple will contain the PyCode object -- which
### itself contains a reference to the lexical environment (defined
### for a function during import) -- and the callstack.
###
### Giving the same name to function declarations and (capitalized) to
### PyCode declarations is just a helpful convention. Only the string
### name will be visible in Lisp. Notice that function definitions
### that would conflict with Python builtins are given names different
### from their lisp names.

######## Special Forms ########

def exposed_eval( context, val ):
    return val
Eval = PyCode(exposed_eval,'eval', True, True)

def quote( context, val ):
    return val
Quote = PyCode(quote,'quote', False, False)

### This function is used by fn and form below to parse their args
def parse_args( args_list ):
    def legal_pair( list ):
        if list.cdr == None:
            return False
        if list.cdr.cdr == None:
            if issymbol(list.car):
                return True
        return False
    def legal_trio( list ):
        if list.cdr == None or list.cdr.cdr==None:
            return False
        if list.cdr.cdr.cdr==None:
            if issymbol(list.car) and issymbol(list.cdr.cdr.car):
                return True
        return False

    used_symbols = []
    normal_args = []
    optional_args = []
    optional_args_trios = []
    rest_arg = None
    is_body = False
    kw_args = []
    kw_def_args = []
    kw_def_arg_trios = []
    while args_list and issymbol(args_list.car) and not args_list.car.iskeyword:
        if args_list.car not in used_symbols:
            normal_args.append(args_list.car)
            used_symbols.append(args_list.car)
        else:
            return "Duplicate symbol"
        args_list = args_list.cdr
    while args_list and iscons(args_list.car):
        if legal_pair(args_list.car):
            if args_list.car.car not in used_symbols:
                optional_args.append(args_list.car)
                used_symbols.append(args_list.car.car)
            else:
                return "Duplicate symbol"
            args_list = args_list.cdr
        elif legal_trio(args_list.car):
            if args_list.car.car not in used_symbols and \
                    args_list.car.cdr.cdr.car not in used_symbols:
                optional_args_trios.append(args_list.car)
                used_symbols.append(args_list.car.car)
                used_symbols.append(args_list.car.cdr.cdr.car)
            else:
                return "Duplicate symbol"
            args_list = args_list.cdr
        else:
            return "Illegal optional tuple %s" % args_list.car
    while args_list:
        if issymbol(args_list.car) and args_list.car.iskeyword:
            if args_list.cdr==None:
                return "Keyword provided without value"
            elif args_list.car.name in (':r',':b'):
                if rest_arg:
                    return "Duplicate rest/body"
                else:
                    is_body = args_list.car.name==':b'
                    if not issymbol(args_list.cdr.car) or args_list.cdr.car.iskeyword:
                        return "%s needs a symbol" % ('Body' if is_body else 'Rest')
                    if args_list.cdr.car not in used_symbols:
                        rest_arg = args_list.cdr.car
                        used_symbols.append(args_list.cdr.car)
                    else:
                        return "Duplicate symbol"
                    args_list = args_list.cdr.cdr
            elif args_list.car.name==':k':
                if kw_args:
                    return "Keywords already provided"
                args_list = args_list.cdr
                while args_list and \
                        ((issymbol(args_list.car) and not args_list.car.iskeyword) \
                             or iscons(args_list.car)):
                    if issymbol(args_list.car):
                        if args_list.car in used_symbols:
                            return "duplicate symbol"
                        else:
                            used_symbols.append(args_list.car)
                            kw_args.append(args_list.car)
                    elif legal_pair(args_list.car):
                        if args_list.car.car not in used_symbols:
                            kw_def_args.append(args_list.car)
                            used_symbols.append(args_list.car.car)
                        else:
                            return "Duplicate symbol"
                    elif legal_trio(args_list.car):
                        if args_list.car.car not in used_symbols and \
                                args_list.car.cdr.cdr.car not in used_symbols:
                            kw_def_arg_trios.append(args_list.car)
                            used_symbols.append(args_list.car.car)
                            used_symbols.append(args_list.car.cdr.cdr.car)
                        else:
                            return "Duplicate symbol"
                    else:
                        return "Malformed kw arg"
                    args_list = args_list.cdr
                if not kw_args:
                    return "No keyword args provided after :k"
            else:
                return "Unknown keyword %s" % args_list.car
            continue #look for further keywords
        else: #stuff left over
            return "Weirdness in args list."
    return (normal_args,optional_args,optional_args_trios,
            rest_arg,is_body,kw_args,kw_def_args,kw_def_arg_trios)
 
def fn( context, *args ):
    print parse_args(args[0])
    return "No value!!!"

    body = list2cons(args[1:])
    if not iscode(body):
        return Exception("fn received malformed body: %s"%body,None)
    return LispCode( args[0], body, context[1].env )
    # Note that it is the callstack's env, not self's env, that is the lexical environment.
Fn = PyCode(fn,'fn', False, False)

def form( context, *args ):
    #
    # Check for well-formedness
    #
    body = list2cons(args[1:])
    if not iscode(body):
        return Exception("fn received malformed body: %s"%body,None)
    return LispCode( args[0], body, None )
    # Note that it is the callstack's env, not self's env, that is the lexical environment.
Form = PyCode(form,'form', False, False)

def set_locally( context, sym, val ):
    context[1].env.bind_sym(sym,val)
    return val
SetLocally = PyCode(set_locally,'set-locally',False,False,[1]) #note the eval-index

########## Functions ##########

def cons_fn( context, car, cdr ):
    return Cons(car,cdr)
ConsFn = PyCode(cons_fn,'cons')

def car( context, cell ):
    return cell.car
Car = PyCode(car,'car')

def cdr( context, cell ):
    return cell.cdr
Cdr = PyCode(cdr,'cdr')

def lisp_not( context, val ):
    return not val
Not = PyCode(lisp_not,'not')

### AND and OR need to be special forms

def equals( context, a, b ):
    return a==b
Equals = PyCode(equals,'=')

def lt( context, a, b ):
    return a < b
Lt = PyCode(lt,'<')

def leq( context, a, b ):
    return a <= b
Leq = PyCode(leq,'<=')

def gt( context, a, b ):
    return a < b
Gt = PyCode(gt,'<')

def geq( context, a, b ):
    return a <= b
Geq = PyCode(geq,'<=')

def plus( context, *args ):
    return sum(args)
Plus = PyCode(plus,'+')

def minus( context, *args ):
    if len(args)<2: return -sum(args)
    else: return args[0] - sum(args[1:])
Minus = PyCode(minus,'-')

def times( context, *args ):
    ret = 1
    for i in args:
        ret *= i
    return ret
Times = PyCode(times,'*')

def divide( context, *args ):
    if len(args)<2: return 1.0/args[0]
    else:
        ret = args[0]
        for i in args[1:]:
            ret /= i
    return ret
Divide = PyCode(divide,'/')

def remainder( context, a, b ):
    return a%b
Remainder = PyCode(remainder,'%')

def put( context, val ):
    print val
    return val
Put = PyCode(put,'put')

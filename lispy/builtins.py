from core import *
from arguments import *

### NB: PyCode objects are assumed to be functions by default. That
### is, they are assumed to implicitly evaluate their arguments and
### not their returns. Special forms modify one or both of those
### behaviors by explicitly passing third and fourth arguments to the
### PyCode constructor.
###
### NB: All PyCode calls must expect "self" and "stack" as their
### first arguments before any other arguments supplied by the call in
### lisp. "Self" is the PyCode object, which itself contains a
### reference to the lexical environment (defined for a function
### during import).
###
### Giving the same name to function declarations and (capitalized) to
### PyCode declarations is just a helpful convention. Only the string
### name will be visible in Lisp. Notice that function definitions
### that would conflict with Python builtins are given names different
### from their lisp names.

######## Special Forms ########

def exposed_eval( self, stack, val ):
    return val
Eval = PyCode(exposed_eval,'eval', True, True)

def quote( self, stack, val ):
    return val
Quote = PyCode(quote,'quote', False, False)

def fn( self, stack, *args ):
    p = parse_args(args[0])
    body = list2cons(args[1:])
    if not iscode(body):
        return Exception("fn received malformed body: %s"%body,None)
    return LispCode( p[0],p[1],p[2],p[3], body, stack.env )
    # Note that it is the callstack's env, not self's env, that is the lexical environment.
Fn = PyCode(fn,'fn', False, False)

def form( self, stack, *args ):
    p = parse_args(args[0])
    body = list2cons(args[1:])
    if not iscode(body):
        return Exception("fn received malformed body: %s"%body,None)
    return LispCode( p[0],p[1],p[2],p[3], body, None )
    # Note that it is the callstack's env, not self's env, that is the lexical environment.
Form = PyCode(form,'form', False, False)

def set_locally( self, stack, sym, val ):
    stack.env.parent.bind_sym(sym,val) # will be in a dropped environment
    return val
SetLocally = PyCode(set_locally,'set-locally',False,False,[1]) #note the eval-index

########## Functions ##########

def cons_fn( self, stack, car, cdr ):
    return Cons(car,cdr)
ConsFn = PyCode(cons_fn,'cons')

def car( self, stack, cell ):
    return cell.car
Car = PyCode(car,'car')

def cdr( self, stack, cell ):
    return cell.cdr
Cdr = PyCode(cdr,'cdr')

def lisp_not( self, stack, val ):
    return not val
Not = PyCode(lisp_not,'not')

### AND and OR need to be special forms

def equals( self, stack, a, b ):
    return a==b
Equals = PyCode(equals,'=')

def lt( self, stack, a, b ):
    return a < b
Lt = PyCode(lt,'<')

def leq( self, stack, a, b ):
    return a <= b
Leq = PyCode(leq,'<=')

def gt( self, stack, a, b ):
    return a < b
Gt = PyCode(gt,'<')

def geq( self, stack, a, b ):
    return a <= b
Geq = PyCode(geq,'<=')

def plus( self, stack, *args ):
    return sum(args)
Plus = PyCode(plus,'+')

def minus( self, stack, *args ):
    if len(args)<2: return -sum(args)
    else: return args[0] - sum(args[1:])
Minus = PyCode(minus,'-')

def times( self, stack, *args ):
    ret = 1
    for i in args:
        ret *= i
    return ret
Times = PyCode(times,'*')

def divide( self, stack, *args ):
    if len(args)<2: return 1.0/args[0]
    else:
        ret = args[0]
        for i in args[1:]:
            ret /= i
    return ret
Divide = PyCode(divide,'/')

def remainder( self, stack, a, b ):
    return a%b
Remainder = PyCode(remainder,'%')

def put( self, stack, val ):
    print val if val!=None else '()'
    return val
Put = PyCode(put,'put')

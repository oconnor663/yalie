from core import *

### NB: PyCode objects are assumed to be functions by default. That
### is, they are assumed to implicitly evaluate their arguments and
### not their returns. Special forms modify one or both of those
### behaviors by explicitly passing third and fourth arguments to the
### PyCode constructor.
###
### NB: All PyCode calls must expect the equivalent of "self" as their
### first argument. Self will be the PyCode object, which notably
### contains a reference to the lexical environment (defined for a
### function during import) and the callstack.
###
### Giving the same name to function declarations and (capitalized) to
### PyCode declarations is just a helpful convention. Only the string
### name will be visible in Lisp. Notice that function definitions
### that would conflict with Python builtins are given names different
### from their lisp names.

######## Special Forms ########

def exposed_eval( self, val ):
    return val
Eval = PyCode(exposed_eval,'eval', True, True)

def quote( self, val ):
    return val
Quote = PyCode(quote,'quote', False, False)


########## Functions ##########

def cons( self, car, cdr ):
    return Cons(car,cdr)
Cons = PyCode(cons,'cons')

def car( self, cell ):
    return cell.car
Car = PyCode(car,'car')

def cdr( self, cell ):
    return cell.cdr
Cdr = PyCode(cdr,'cdr')

def lisp_not( self, val ):
    return not val
Not = PyCode(lisp_not,'not')

### AND and OR need to be special forms

def equals( self, a, b ):
    return a==b
Equals = PyCode(equals,'=')

def lt( self, a, b ):
    return a < b
Lt = PyCode(lt,'<')

def leq( self, a, b ):
    return a <= b
Leq = PyCode(leq,'<=')

def gt( self, a, b ):
    return a < b
Gt = PyCode(gt,'<')

def geq( self, a, b ):
    return a <= b
Geq = PyCode(geq,'<=')

def plus( self, *args ):
    return sum(args)
Plus = PyCode(plus,'+')

def minus( self, *args ):
    if len(args)<2: return -sum(args)
    else: return args[0] - sum(args[1:])
Minus = PyCode(minus,'-')

def times( self, *args ):
    ret = 1
    for i in args:
        ret *= i
    return ret
Times = PyCode(times,'*')

def divide( self, *args ):
    if len(args)<2: return 1.0/args[0]
    else:
        ret = args[0]
        for i in args[1:]:
            ret /= i
    return ret
Divide = PyCode(divide,'/')

def remainder( self, a, b ):
    return a%b
Remainder = PyCode(remainder,'%')

from core import *

### NB: All PyCode declarations for special forms must receive True as
### their third argument to indicate that their arguments (when
### called) should not be evaluated. This argument can be omitted for
### PyCode declarations representing functions, because it defaults to
### False.
###
### Giving the same name to function declarations and (capitalized) to
### PyCode declarations is just a helpful convention. Only the string
### name will be visible in Lisp.

######## Special Forms ########

########## Functions ##########

def eval( val ):
    return val
Eval = PyCode(eval,'eval')

def cons( car, cdr ):
    return Cons(car,cdr)
Cons = PyCode(cons,'cons')

def car( cell ):
    return cell.car
Car = PyCode(car,'car')

def cdr( cell ):
    return cell.cdr
Cdr = PyCode(cdr,'cdr')

def lisp_not( val ):
    return not val
Not = PyCode(lisp_not,'not')

### AND and OR need to be special forms

def equals( a, b ):
    return a==b
Equals = PyCode(equals,'=')

def lt( a, b ):
    return a < b
Lt = PyCode(lt,'<')

def leq( a, b ):
    return a <= b
Leq = PyCode(leq,'<=')

def gt( a, b ):
    return a < b
Gt = PyCode(gt,'<')

def geq( a, b ):
    return a <= b
Geq = PyCode(geq,'<=')

def plus( a, b ):
    return a + b
Plus = PyCode(plus,'+')

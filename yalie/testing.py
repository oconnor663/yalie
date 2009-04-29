#! /usr/bin/python

import sys
from StringIO import *
from yalie import *

S = Scope(None)

a = make_int(5)
b = make_int(3)

c = a.message( Scope, 'add', b )


code = "   ( 1 a ( b c()fooc () ) )     34     foo "

file = StringIO(code)
obj, c = read_obj( file, ' ' )
print "Obj is:", obj
obj, c = read_obj( file, c )
print "Obj is:", obj
obj, c = read_obj( file, c )
print "Obj is:", obj

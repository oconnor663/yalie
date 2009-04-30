#! /usr/bin/python

import sys,os,string,readline
from StringIO import *

class Scope:
    def __init__( self, parent ):
        self.parent = parent
        self.dict = {}
    def ref( self, key ):
        ### returns value on success else raise error
        if key in self.dict:
            return self.dict[key]
        elif self.parent != None:
            return self.parent.ref(key)
        else:
            raise RuntimeError, "Could not ref key: '%s'" % key
    def set( self, key, val ):
        ### Returns True on success else False
        if key in self.dict:
            self.dict[key] = val
        elif self.parent != None:
            self.parent.set(key,val)
        else:
            raise RuntimeError, "Could not set key: '%s'" % key
    def let( self, key,val ):
        ### No return
        if key in self.dict:
            raise RuntimeError, "Variable already exists"
        self.dict[key] = val
    def __setitem__( self, key, val ):
        self.let( key, val )
        

class Object:
    def __init__( self, parent ):
        self.parent = parent
        if parent==None:
            self.methods = Scope(None)
            self.members = {}
            self.data = None
        else:
            self.methods = Scope(parent.methods)
            self.members = parent.members.copy()
            self.data = parent.data
    def inherits( self, ancestor ):
        if ancestor==self:
            return True
        elif self.parent!=None:
            return self.parent.inherits(ancestor)
        else:
            return False
    def message( self, scope, message, *args ):
        return self.methods.ref(message).call(scope,self,*args)

### def method( scope, object, *args )

class PyMethod:
    def __init__( self, fn ):
        self.fn = fn
    def call( self, scope, obj, *args ):
        return self.fn( scope, obj, *args )


###
### Builtins
###


RootObject = Object(None)
RootObject.methods['eval'] = PyMethod( lambda scope, obj : obj )
RootObject.methods['bool'] = PyMethod( lambda scope, obj : make_int(1) )
def print_ret( p, r ):
    sys.stdout.write( str(p) )
    return r
RootObject.methods['print'] = PyMethod( lambda scope, obj: print_ret(obj,obj) )

NilObject = Object(RootObject)
NilObject.methods['bool'] = PyMethod( lambda scope, obj : make_int(0) )
NilObject.methods['print'] = PyMethod( lambda scope, obj: print_ret('()',obj) )

IntObject = Object(RootObject)
def make_int( i ):
    if type(i) not in (type(0),type(10000000000)):
        raise RuntimeError, "OOPS!!!"
    ret = Object( IntObject )
    ret.data = i
    return ret
def int_add( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot add int to non-int."
    return make_int( obj.data + arg.data )
def int_sub( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( obj.data - arg.data )
def int_eq( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot compare int to non-int."
    return make_int( 1 if obj.data==arg.data else 0 )
def int_lt( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot compare int to non-int."
    return make_int( 1 if obj.data<arg.data else 0 )
IntObject.methods['+'] = PyMethod( int_add )
IntObject.methods['-'] = PyMethod( int_sub )
IntObject.methods['='] = PyMethod( int_eq )
IntObject.methods['<'] = PyMethod( int_lt )
IntObject.methods['print'] = PyMethod(lambda scope,obj:print_ret(obj.data,obj))
IntObject.methods['bool'] = PyMethod( lambda scope, obj :
                                          make_int(0) if obj.data==0 \
                                          else make_int(1))

SymbolObject = Object(RootObject)
def make_symbol(name):
    if type(name)!=type('') or name=='':
        raise RuntimeError, "Something fishy"
    ret = Object(SymbolObject)
    ret.data = name
    return ret
SymbolObject.methods['eval'] = PyMethod( lambda scope, obj:scope.ref(obj.data))
SymbolObject.methods['print'] = PyMethod(lambda scope,obj:print_ret(obj.data,obj))


ConsObject = Object(RootObject)
def make_cons( obj1, obj2 ):
    ret = Object(ConsObject)
    ret.data = [ obj1, obj2 ]
    return ret
def make_list( l ):
    if l:
        ret = Object(ConsObject)
        ret.data = [ l[0], make_list(l[1:]) ]
        return ret
    else:
        return NilObject
def cons_print( scope, c ):
    sys.stdout.write( '(' )
    c.data[0].message( scope, 'print' )
    def cons_print_helper( rest ):
        if rest.inherits(ConsObject):
            sys.stdout.write(' ')
            rest.data[0].message( scope, 'print' )
            cons_print_helper( rest.data[1] )
        elif rest.inherits( NilObject ):
            sys.stdout.write( ')' )
        else:
            sys.stdout.write( ' . ' )
            rest.data[1].message( scope, 'print' )
            sys.stdout.write( ')' )
    cons_print_helper( c.data[1] )
    return c
def set_car( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    obj.data[0] = arg
    return arg
def set_cdr( scope, obj, arg ):
    arg = arg.message(scope,'eval')
    obj.data[1] = arg
    return arg
def cons_eval( scope, obj ):
    fn = obj.data[0].message( scope, 'eval' )
    args = []
    obj = obj.data[1]
    while not obj.inherits(NilObject):
        if not obj.inherits(ConsObject):
            raise RuntimeError, "Function called in dotted list"
        args.append( obj.data[0] )
        obj = obj.data[1]
    return fn.message( scope, 'call', *args )
    
ConsObject.methods['car'] = PyMethod( lambda scope,obj: obj.data[0] )
ConsObject.methods['cdr'] = PyMethod( lambda scope,obj: obj.data[1] )
ConsObject.methods['setcar'] = PyMethod( set_car )
ConsObject.methods['setcdr'] = PyMethod( set_cdr )
ConsObject.methods['print'] = PyMethod( cons_print )
ConsObject.methods['eval'] = PyMethod( cons_eval )

MsgObject = Object(RootObject)
def msg_call( scope, obj, recipient, message, *args ):
    #evaluate the recipient
    recipient = recipient.message( scope, 'eval' )
    if not message.inherits( SymbolObject ):
        raise RuntimeError, "'msg' requires a symbol as a message"
    #pass the message
    return recipient.message( scope, message.data, *args )    
MsgObject.methods['call'] = PyMethod( msg_call )


LetObject = Object(RootObject)
def let_call( scope, obj, var, val ):
    if not var.inherits(SymbolObject):
        raise RuntimeError, "'let' requires a symbol!"
    e_val = val.message( scope, 'eval' )
    scope.let( var.data, e_val )
    return e_val
LetObject.methods['call'] = PyMethod( let_call )


SetObject = Object(RootObject)
def set_call( scope, obj, var, val ):
    if not var.inherits(SymbolObject):
        raise RuntimeError, "'set' requires a symbol!"
    e_val = val.message( scope, 'eval' )
    scope.set( var.data, e_val )
    return e_val
SetObject.methods['call'] = PyMethod( set_call )

QuoteObject = Object(RootObject)
QuoteObject.methods['call'] = PyMethod( lambda scope, self, obj: obj)

IfObject = Object(RootObject)
def if_call( scope, obj, cond, conseq, alt=NilObject ):
    bool = cond.message( scope, 'eval' ).message( scope, 'bool' )
    if bool.data:
        return conseq.message( scope, 'eval' )
    else:
        return alt.message( scope, 'eval' )
IfObject.methods['call'] = PyMethod( if_call )

WhileObject = Object(RootObject)
def while_call( scope, obj, cond, *body ):
    ret = NilObject
    while True:
        bool = cond.message(scope,'eval').message(scope,'bool')
        if not bool.data:
            return ret
        for i in body:
            ret = i.message(scope,'eval')
    return ret
WhileObject.methods['call'] = PyMethod( while_call )

###
### Parser!!!
###

class Buffer:
    def __init__( self, file ):
        self.file = file
        self.buf = []
    def getc( self ):
        if self.buf:
            c = self.buf[0]
            self.buf = self.buf[1:]
            return c
        else:
            return self.file.read(1)
    def ungetc( self, c ):
        if len(c)>1:
            raise RuntimeError, "OMG!!!!"
        self.buf = [c] + self.buf if c else self.buf
    def read_obj(self):
        return read_obj(self)

def read_obj( buf ):
    return clear_whitespace( buf )

def clear_whitespace( buf ):
    c = buf.getc()
    while c and c in string.whitespace:
        c = buf.getc()
    if c=='':
        return None
    if c=='#':
        while c not in ('','\n'):
            c = buf.getc()
        return clear_whitespace(buf)
    else:
        buf.ungetc(c)
        return read_list(buf)

def read_list( buf ):
    c = buf.getc()
    if c != '(':
        buf.ungetc(c)
        return read_int(buf)

    def read_rest( buf ):
        c = buf.getc()
        while c and c in string.whitespace:
            c = buf.getc()
        if c=='':
            raise RuntimeError, "unclosed list"
        if c==')':
            return []
        else:
            buf.ungetc(c)
            obj = read_obj( buf )
            rest = read_rest( buf )
            return [ obj ] + rest

    return make_list(read_rest( buf ))

def read_int( buf ):
    c = buf.getc()
    if c not in string.digits:
        buf.ungetc(c)
        return read_symbol( buf )
    chars = [ c ]
    c = buf.getc()
    while c and c in string.digits:
        chars.append(c)
        c = buf.getc()
    if c and c in string.letters:
        raise RuntimeError, "Syntax error reading int"
    buf.ungetc(c)
    return make_int(int(string.join(chars,'')))

def read_symbol( buf ):
    allowed = [i for i in string.letters+string.digits+string.punctuation
               if i not in "#()`:.,;"]
    c = buf.getc()
    if c not in allowed:
        raise RuntimeError, "Unable to parse"
    chars = [c]
    c = buf.getc()
    while c and c in allowed:
        chars.append(c)
        c = buf.getc()
    buf.ungetc(c)
    return make_symbol(string.join(chars,''))


###
### REPL
###

def make_global_scope():
    S = Scope( None )
    S['msg'] = MsgObject
    S['let'] = LetObject
    S['set'] = SetObject
    S['quote'] = QuoteObject
    S['if'] = IfObject
    S['while'] = WhileObject
    return S

def main():
    scope = make_global_scope()

    while True:
        try:
            code = raw_input("yalie: ")
        except EOFError:
            print
            break
        buf = Buffer( StringIO(code) )
        while True:
            obj = buf.read_obj()
            if obj==None:
                break
            ret = obj.message(scope,'eval')
            ret.message(scope,'print')
            print

if __name__=='__main__':
    main()

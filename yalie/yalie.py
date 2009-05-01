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
            raise RuntimeError, "Could not ref key: %s" % key
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
def unmake_list( c ):
    list = []
    while not c.inherits(NilObject):
        if not c.inherits(ConsObject):
            raise RuntimeError, "cannot make python list out of non-list"
        list.append( c.data[0] )
        c = c.data[1]
    return list
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
    return fn.message( scope, 'call', *unmake_list(obj.data[1]) )
    
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
def quote_call( scope, obj, arg ):
    if not arg.inherits( ConsObject ):
        return arg
    list = unmake_list(arg)
    if list[0].inherits(SymbolObject) and list[0].data=='unquote-splice':
        raise RuntimeError, "Can't splice into nothing."
    if list[0].inherits(SymbolObject) and list[0].data=='unquote':
        if len(list)>2:
            raise RuntimeError, "too many to unquote"
        return list[1].message(scope,'eval')
    ## At this point we have a list that is guaranteed quoted

    def quote_list( scope, list ):
        list = unmake_list(list)
        ret = []
        for i in list:
            if not i.inherits(ConsObject):
                ret.append(i)
                continue
            ls = unmake_list(i)
            if ls[0].inherits(SymbolObject) and ls[0].data=='unquote':
                if len(ls)>2:
                    raise RuntimeError, "too many to unquote"
                ret.append( ls[1].message(scope,'eval') )
            elif ls[0].inherits(SymbolObject) and ls[0].data=='unquote-splice':
                if len(ls)>2:
                    raise RuntimeError, "too many to unquote-splice"
                tmp = ls[1].message(scope,'eval')
                if not tmp.inherits(ConsObject):
                    raise RuntimeError, "cannot splice non-list"
                ls2 = unmake_list( tmp )
                ret = ret + ls2
            else:
                ret.append(quote_list(scope,i))
        return make_list(ret)

    ## And now we are ready to return from quote_call
    return quote_list( scope, arg )
        
QuoteObject.methods['call'] = PyMethod( quote_call )
#QuoteObject.methods['call'] = PyMethod( lambda scope,obj,arg: arg )

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
    delimiters = "()"
    prefixes = "`',;"
    infixes = ".:"
    punctuation = delimiters+prefixes+infixes
    def __init__( self, file ):
        self.file = file
        self.buf = []
        self.tokbuf = []
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
    def gettok( self ):
        if self.tokbuf:
            tmp = self.tokbuf[0]
            self.tokbuf = self.tokbuf[1:]
            return tmp
        c = self.getc()
        while c and c in string.whitespace:
            c = self.getc()
        if c=='':
            return None
        if c=='#':
            while c not in '\n': # includes empty
                c = self.getc()
            return self.gettok()
        elif c in self.punctuation:
            return c
        elif c in string.digits:
            chars = [ c ]
            c = self.getc()
            while c and c in string.digits:
                chars.append(c)
                c = self.getc()
            if c not in self.punctuation+string.whitespace:
                raise RuntimeError, "Syntax error reading int"
            self.ungetc(c)
            return make_int(int(string.join(chars,'')))
        else:
            chars = [ c ]
            c = self.getc()
            while c not in self.punctuation+string.whitespace:
                chars.append(c)
                c = self.getc()
            self.ungetc(c)
            return make_symbol( string.join(chars,'') )
    def ungettok( self, tok ):
        self.tokbuf = [tok] + self.tokbuf
    def read_prefixed(self):
        dict = {'`':'quote','\'':'quote',';':'unquote-splice',',':'unquote'}
        tok = self.gettok()
        if tok==None:
            return None
        elif isinstance(tok,Object):
            return tok
        elif tok=='(':
            return self.read_sexpr()
        elif tok in self.prefixes:
            return make_list([make_symbol(dict[tok]),self.read_prefixed()])
        else:
            raise RuntimeError, "read_prefixes could not parse %s" % tok
    
    def read_infixed(self, prefixed=None):
        dict = { '.':'msg', ':':'ref' } ##TWO COPIES
        if prefixed==None:
            prefixed = self.read_prefixed()
        tok = self.gettok()
        if tok==None:
            return prefixed #could be None
        elif isinstance(tok,Object) or tok not in self.infixes:
            self.ungettok(tok)
            return prefixed
        else:
            other = self.read_prefixed()
            list = make_list( [make_symbol(dict[tok]), prefixed, other] )
            return self.read_infixed(list)

    def read_sexpr( self, capture_infix=True ):
        dict = { '.':'msg', ':':'ref' } ##TWO COPIES
        tok = self.gettok()
        if tok==None:
            raise RuntimeError, "Ended in sexpr.0"
        elif tok==')':
            return NilObject
        else:
            self.ungettok(tok)

        if capture_infix:
            first = self.read_prefixed()
            if first==None:
                raise RuntimeError, "Ended in sexpr.1"
            tok = self.gettok()
            if tok==None:
                raise RuntimeError, "Ended in sexpr.2"
            elif isinstance(tok,Object) or tok not in self.infixes:
                self.ungettok(tok)
                return make_cons( first, self.read_sexpr(False) )
            else:
                return make_cons( make_symbol(dict[tok]),
                                  make_cons( first,
                                             self.read_sexpr(False) ))
        else:
            return make_cons(self.read_infixed(),self.read_sexpr(False))

    def read_obj(self):
        return self.read_infixed()

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
    HISTORY_NAME = os.path.expanduser('~/.yalie_history')
    scope = make_global_scope()
    if not os.path.exists(HISTORY_NAME):
        open(HISTORY_NAME,'w').close()
    readline.read_history_file(HISTORY_NAME)
    while True:
        try:
            code = raw_input("yalie: ")
        except EOFError:
            print
            break
        except KeyboardInterrupt:
            print
            continue

        readline.write_history_file(HISTORY_NAME)
        buf = Buffer( StringIO(code) )

        ### Make this false to see Python error traces
        CATCH_ERRORS = 1

        while True:
            if CATCH_ERRORS:
                ### Protected loop for normal use
                try:
                    obj = buf.read_obj()
                    if obj==None:
                        break
                    ret = obj.message(scope,'eval')
                    ret.message(scope,'print')
                    print
                except Exception, e:
                    print "ERROR:", e.args
                except KeyboardInterrupt:
                    print "INTERRUPT"
                    break
            else:
                ### Unprotected loop for debugging
                obj = buf.read_obj()
                if obj==None:
                    break
                ret = obj.message(scope,'eval')
                ret.message(scope,'print')
                print


if __name__=='__main__':
    main()

#! /usr/bin/python

import sys,os,string,readline,copy
from StringIO import *

### Make this false to see Python error traces
CATCH_ERRORS = 1

### Terminal prompts
PROMPT = "yalie: "
REPROMPT = "...      "

### Command history
HISTORY_NAME = os.path.expanduser('~/.yalie_history')

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
            raise RuntimeError, "'let' cannot modify an existing binding"
        self.dict[key] = val
    def __getitem__( self, key ):
        return self.ref( key )
    def __setitem__( self, key, val ):
        self.dict[key] = val
    def list_keys( self ):
        ret = self.dict.keys()
        if self.parent:
            ret += [ i for i in self.parent.list_keys() if i not in ret ]
        ret.sort()
        return ret
    def copy( self ):
        ret = Scope(None)
        ret.dict = self.dict.copy()
        ret.parent = self.parent
        return ret
        

class Object:
    def __repr__( self ):
        ### Note the strangeness of this arrangement. It implies that
        ### the "repr" field will be set to a FUNCTION, not a method.
        ### The function call will appear to be a method call, but the
        ### type difference means that the self will not be implicitly
        ### passed. Thus this little hack.
        return self.repr(self)
    def __init__( self, parent, name=None ):
        self.parent = parent
        self.name = name
        if parent==None:
            self.methods = Scope(None)
            self.members = Scope(None)
            self.data = None
            self.repr = lambda self: "<Object%s>" % (': '+self.name if
                                                     self.name else '')
        else:
            self.methods = Scope(parent.methods)
            self.members = parent.members.copy()
            self.data = copy.copy(parent.data)
            self.repr = parent.repr
    def inherits( self, ancestor ):
        if ancestor==self:
            return True
        elif self.parent!=None:
            return self.parent.inherits(ancestor)
        else:
            return False
    def message( self, scope, message, *args ):
        ret = self.methods.ref(message).call(scope,self,*args)
        if type(ret)==type(True):
            print "message %s to obj %s is returning a bool!" % (message, self )
        return ret
    def copy( self ):
        ret = Object( None )
        ret.parent = self.parent
        ret.methods = self.methods.copy()
        ret.members = self.members.copy()
        ret.data = copy.copy(self.data)
        ret.repr = self.repr
        return ret

class PyFnMethod:
    def __init__( self, fn ):
        self.fn = fn
    def call( self, scope, obj, *args ):
        # implicitly eval's the args
        args = [ i.message(scope,'eval') for i in args ]
        ret = self.fn( scope, obj, *args )
        return ret
    def call_noeval( self, scope, obj, *args ):
        return self.fn( scope, obj, *args )

class PyFormMethod( PyFnMethod ):
    def call( self, scope, obj, *args ):
        return self.fn( scope, obj, *args )
    def call_noeval( self, scope, obj, *args ):
        return self.fn( scope, obj, *args )

class LispFnMethod:
    def __init__( self, scope, args, rest_arg, body ):
        self.scope = scope
        self.args = args                 #list of strings
        self.rest_arg = rest_arg         #string or None
        self.body = body                 #list of objects
    def call( self, call_scope, caller, *call_args ):
        ### binds args and self
        ## first check number of args
        if self.rest_arg==None:
            if len(call_args)>len(self.args):
                raise RuntimeError, "Too many arguments to lisp method."
            if len(call_args)<len(self.args):
                raise RuntimeError, "Too few arguments to lisp method."
        else:
            if len(call_args)<len(self.args):
                raise RuntimeError, "Too few arguments to lisp method."
        new_scope = Scope(self.scope)
        ### NB: the assignment of self before other arguments allows
        ### any user-defined argument named 'self' to take precedence
        ### in binding. This is intended.
        new_scope['self'] = caller
        # pair args off with arg names and chop the list of args
        for i in self.args:
            new_scope[i] = call_args[0].message(call_scope,'eval')
            call_args = call_args[1:]
        # collect any remainder into the final list
        if self.rest_arg:
            rest = [ i.message(call_scope,'eval') for i in call_args ]
            new_scope[self.rest_arg] = make_list(rest)
        ret = make_nil()
        for i in self.body:
            ret = i.message( new_scope, 'eval' )
        return ret
    def call_noeval( self, call_scope, caller, *call_args ):
        ### binds args and self
        ## first check number of args
        if self.rest_arg==None and len(call_args)>len(self.args):
                raise RuntimeError, "Too many arguments to lisp method."
        if len(call_args)<len(self.args):
            raise RuntimeError, "Too few arguments to lisp method."
        new_scope = Scope(self.scope)
        ### NB: the assignment of self before other arguments allows
        ### any user-defined argument named 'self' to take precedence
        ### in binding. This is intended.
        new_scope['self'] = caller
        # pair args off with arg names and chop the list of args
        for i in self.args:
            new_scope[i] = call_args[0]
            call_args = call_args[1:]
        # collect any remainder into the final list
        if self.rest_arg:
            new_scope[self.rest_arg] = make_list(call_args)
        ret = make_nil()
        for i in self.body:
            ret = i.message( new_scope, 'eval' )
        return ret
        
class LispFormMethod( LispFnMethod ):
    def call( self, call_scope, caller, *call_args ):
        ### binds args and self
        ## first check number of args
        if self.rest_arg==None:
            if len(call_args)>len(self.args):
                raise RuntimeError, "Too many arguments to lisp method."
            if len(call_args)<len(self.args):
                raise RuntimeError, "Too few arguments to lisp method."
        else:
            if len(call_args)<len(self.args):
                raise RuntimeError, "Too few arguments to lisp method."
        new_scope = Scope(self.scope)
        ### NB: the assignment of self before other arguments allows
        ### any user-defined argument named 'self' to take precedence
        ### in binding. This is intended.
        new_scope['self'] = caller
        # pair args off with arg names and chop the list of args
        ###### NOTE: NOT EVALUATING ARGUMENTS
        for i in self.args:
            new_scope[i] = call_args[0]
            call_args = call_args[1:]
        # collect any remainder into the final list
        if self.rest_arg:
            new_scope[self.rest_arg] = make_list(call_args)
        ret = make_nil()
        for i in self.body:
            ret = i.message( new_scope, 'eval' )
        return ret.message( call_scope, 'eval' )
    def call_noeval( self, call_scope, caller, *call_args ):
        return self.call(call_args,caller,*call_args)
        
###
### Builtins
###
Builtins = {}

RootObject = Object(None, "Root")
def print_ret( obj ):
    print repr(obj)
    return obj
def def_method_or_form( is_function, scope, obj, name, args, *body ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of method must be a symbol"
    if not args.inherits(ConsObject) and not args.inherits(NilObject):
        raise RuntimeError, "Args must be a list"
    if not well_formed(args):
        raise RuntimeError, "Args list must be well-formed"
    args_ls = unmake_list(args)
    ## Look for a rest arg
    rest_arg = None
    if args_ls and args_ls[-1].inherits(ConsObject):
        last_ls = unmake_list(args_ls[-1])
        if len(last_ls)>2:
            raise RuntimeError, "Too many items in a method def rest list"
        for i in last_ls:
            if not i.inherits(SymbolObject):
                raise RuntimeError, "non-symbol in args sublist"
        if last_ls[0].data != "rest":
            raise RuntimeError, "Unknown argument tag: %s" % last_ls[0].data
        ## with tests passed, strip rest arg
        rest_arg = last_ls[1].data
        args_ls = args_ls[:-1]
    ## Check rest of args
    for i in args_ls:
        if not i.inherits(SymbolObject):
            raise RuntimeError, "non-symbol in args list"
    arg_names = [ i.data for i in args_ls ]
    if is_function:
        obj.methods[name.data] = LispFnMethod( scope, arg_names, rest_arg, body )
    else:
        obj.methods[name.data] = LispFormMethod( scope, arg_names, rest_arg, body )
    return obj
def object_def( scope, obj, name, args, *body ):
    return def_method_or_form( True, scope, obj, name, args, *body )
def object_deform( scope, obj, name, args, *body ):
    return def_method_or_form( False, scope, obj, name, args, *body )
def object_dup( scope, obj, name, new_name ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of method must be a symbol."
    if not new_name.inherits(SymbolObject):
        raise RuntimeError, "New name of method must be a symbol."
    obj.methods[new_name.data] = obj.methods[name.data]
    return new_name
def object_set( scope, obj, name, val ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of member must be a symbol."
    ret = val.message(scope,'eval')
    obj.members[name.data] = ret
    return ret
def object_get( scope, obj, name ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of member must be a symbol."
    return obj.members[name.data]
def isa( scope, obj, arg ):
    return make_bool( obj.inherits(arg) )
def object_eq( scope, obj, arg ):
    return make_bool(obj==arg)
def object_parent( scope, obj ):
    if obj.parent:
        return obj.parent
    else:
        raise RuntimeError, "Root object has no parent to return."

RootObject.methods['eval'] = PyFnMethod( lambda scope, obj : obj )
RootObject.methods['='] = PyFnMethod( object_eq )
RootObject.methods['is'] = PyFnMethod( object_eq )
RootObject.methods['bool'] = PyFnMethod( lambda scope, obj : make_int(1) )
RootObject.methods['print'] = PyFnMethod( lambda scope, obj: print_ret(obj) )
RootObject.methods['def'] = PyFormMethod( object_def )
RootObject.methods['deform'] = PyFormMethod( object_deform )
RootObject.methods['dup'] = PyFormMethod( object_dup )
RootObject.methods['set'] = PyFormMethod( object_set )
RootObject.methods['get'] = PyFormMethod( object_get )
RootObject.methods['parent'] = PyFnMethod( object_parent )
RootObject.methods['isa'] = PyFnMethod( isa )
RootObject.methods['copy'] = PyFnMethod( lambda scope,obj: obj.copy() )
RootObject.methods['child'] = PyFnMethod( lambda scope,obj: Object(obj) )
RootObject.methods['methods'] = PyFnMethod( lambda scope,obj:
                                                make_list( [make_symbol(i) for i in
                                                            obj.methods.list_keys()]))
RootObject.methods['members'] = PyFnMethod( lambda scope,obj:
                                                make_list( [make_symbol(i) for i in
                                                            obj.members.list_keys()]))
Builtins['Root'] = RootObject

NilObject = Object(RootObject, "Nil")
def make_nil():
    return Object(NilObject)
NilObject.repr = lambda self: "<Object: Nil>" if self==NilObject else "()"
NilObject.methods['bool'] = PyFnMethod( lambda scope, obj : make_int(0) )
NilObject.methods['='] = PyFnMethod( lambda scope,obj,arg: make_bool(arg.inherits(NilObject)) )
Builtins['Nil'] = NilObject

IntObject = Object(RootObject, "Int")
IntObject.data = 1
IntObject.repr = lambda self: "<Object: Int>" if self==IntObject \
    else str(self.data)
def make_int( i ):
    if type(i) not in (type(0),type(0L)):
        raise RuntimeError, "OOPS!!!"
    ret = Object( IntObject )
    ret.data = i
    return ret
def make_bool( val ):
    return make_int(1 if val else 0)
def int_add( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot add int to non-int."
    return make_int( obj.data + arg.data )
def int_sub( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( obj.data - arg.data )
def int_mul( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( obj.data * arg.data )
def int_div( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( obj.data // arg.data )
def int_mod( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( obj.data % arg.data )
def int_lt( scope, obj, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot compare int to non-int."
    return make_bool( obj.data < arg.data )
IntObject.methods['+'] = PyFnMethod( int_add )
IntObject.methods['-'] = PyFnMethod( int_sub )
IntObject.methods['*'] = PyFnMethod( int_mul )
IntObject.methods['/'] = PyFnMethod( int_div )
IntObject.methods['%'] = PyFnMethod( int_mod )
IntObject.methods['='] = PyFnMethod( lambda scope,obj,arg: make_bool(arg.inherits(IntObject) and
                                     arg.data == obj.data) )
IntObject.methods['<'] = PyFnMethod( int_lt )
IntObject.methods['bool'] = PyFnMethod( lambda scope, obj : make_bool(obj.data) )
Builtins['Int'] = IntObject

SymbolObject = Object(RootObject, "Symbol")
SymbolObject.data = "<Symbol object>"
SymbolObject.repr = lambda self: self.data
def make_symbol(name):
    if type(name)!=type('') or name=='':
        raise RuntimeError, "Something fishy"
    ret = Object(SymbolObject)
    ret.data = name
    return ret
SymbolObject.methods['eval'] = PyFnMethod( lambda scope, obj:scope.ref(obj.data))
SymbolObject.methods['='] = PyFnMethod( lambda scope,obj,arg: make_bool(arg.inherits(SymbolObject) and
                                     arg.data == obj.data) )
Builtins['Symbol'] = SymbolObject

ConsObject = Object(RootObject, "Cons")
ConsObject.data = [ make_nil(), make_nil() ]
def cons_repr( self ):
    if self==ConsObject:
        return "<Object: Cons>"
    ret = "("
    ret += repr(self.data[0])
    def cons_repr_helper( rest ):
        ret = ''
        if rest.inherits(ConsObject):
            ret += ' ' + repr(rest.data[0])
            ret += cons_repr_helper( rest.data[1] )
        elif rest.inherits( NilObject ):
            ret += ')'
        else:
            ret += ' . ' + repr(rest) + ')'
        return ret
    return ret + cons_repr_helper( self.data[1] )
ConsObject.repr = cons_repr
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
        return make_nil()
def well_formed( c ):
    if not (c.inherits(ConsObject) or c.inherits(NilObject)):
        raise RuntimeError, "Cannot check for well-formedness of nonlist"
    while not c.inherits(NilObject):
        if not c.inherits(ConsObject):
            return False
        c = c.data[1]
    return True
def unmake_list( c ):
    if not well_formed(c):
        raise RuntimeError, "Cannot make python list from non-well-formed list"
    list = []
    while not c.inherits(NilObject):
        list.append( c.data[0] )
        c = c.data[1]
    return list
def set_car( scope, obj, arg ):
    obj.data[0] = arg
    return arg
def set_cdr( scope, obj, arg ):
    obj.data[1] = arg
    return arg
def cons_eval( scope, obj ):
    if not well_formed(obj):
        raise RuntimeError, "Cannot evaluate non-well-formed list."
    fn = obj.data[0].message( scope, 'eval' )
    return fn.message( scope, 'call', *unmake_list(obj.data[1]) )
def cons_eq( scope, obj, arg ):
    if not arg.inherits(ConsObject):
        return False
    b1 = obj.data[0].message(scope,'=',arg.data[0])
    b2 = obj.data[1].message(scope,'=',arg.data[1])
    return make_bool( b1.data and b2.data )
ConsObject.methods['car'] = PyFnMethod( lambda scope,obj: obj.data[0] )
ConsObject.methods['cdr'] = PyFnMethod( lambda scope,obj: obj.data[1] )
ConsObject.methods['setcar'] = PyFnMethod( set_car )
ConsObject.methods['setcdr'] = PyFnMethod( set_cdr )
ConsObject.methods['eval'] = PyFnMethod( cons_eval )
ConsObject.methods['='] = PyFnMethod( cons_eq )
Builtins['Cons'] = ConsObject

# This is the general parent of all callables
def operator_call( scope, obj ):
    raise RuntimeError, "This is not a working function"
OperatorObject = Object(RootObject, "Operator")
OperatorObject.repr = lambda self: "<Operator%s>" % (': '+self.name if
                                                     self.name else '')
OperatorObject.call = PyFnMethod( operator_call )
Builtins['Operator'] = OperatorObject
FunctionObject = Object(OperatorObject, "Function")
FunctionObject.repr = lambda self: "<Function%s>" % (': '+self.name if
                                                     self.name else '')
FunctionObject.call = PyFnMethod( operator_call )
Builtins['Function'] = FunctionObject
SpecialFormObject = Object(OperatorObject, "Form")
SpecialFormObject.repr = lambda self: "<Form%s>" % (': '+self.name if 
                                                    self.name else '')
SpecialFormObject.call = PyFormMethod( operator_call )
Builtins['Form'] = SpecialFormObject

CallObject = Object(FunctionObject,"call")
def call_call( scope, obj, fn, *args ):
    if args[-1].inherits(ConsObject) or args[-1].inherits(NilObject):
        args = list(args[:-1]) + unmake_list(args[-1])
    f = fn.message(scope,'eval')
    if not f.inherits(OperatorObject):
        raise RuntimeError, "'call' expects to receive an operator"
    return f.methods['call'].call_noeval( scope, obj, *args )
CallObject.methods['call'] = PyFnMethod(call_call)
Builtins['call'] = CallObject

MsgObject = Object(SpecialFormObject, "msg")
def msg_call( scope, obj, recipient, message, *args ):
    #evaluate the recipient
    recipient = recipient.message( scope, 'eval' )
    if not message.inherits( SymbolObject ):
        raise RuntimeError, "'msg' requires a symbol as a message"
    #pass the message
    return recipient.message( scope, message.data, *args )    
MsgObject.methods['call'] = PyFormMethod( msg_call )
Builtins['msg'] = MsgObject

LetObject = Object(SpecialFormObject, "let")
def let_call( scope, obj, *body ):
    if body[0].inherits(ConsObject) or body[0].inherits(NilObject):
        new_scope = Scope(scope)
        bindings = unmake_list(body[0])
        if len(bindings)%2!=0:
            raise RuntimeError, "'let' requires an even number of initial args"
        for i in [bindings[i] for i in range(len(bindings)) if i%2==0]:
            if not i.inherits(SymbolObject):
                raise RuntimeError, "'let' cannot bind a non-symbol"
        while bindings:
            new_scope.let(bindings[0].data,
                          bindings[1].message(new_scope,'eval'))
            bindings = bindings[2:]
        ret = make_nil()
        for i in body[1:]:
            ret = i.message(new_scope,'eval')
        return ret
    elif len(body)==2:
        if not body[0].inherits(SymbolObject):
            raise RuntimeError, "'let' requires a symbol!"
        val = body[1].message( scope, 'eval' )
        scope.let( body[0].data, val )
        return val
    else:
        raise RuntimeError, "'let' not formatted properly"
LetObject.methods['call'] = PyFormMethod( let_call )
Builtins['let'] = LetObject

SetObject = Object(SpecialFormObject, "set")
def set_call( scope, obj, var, val ):
    if not var.inherits(SymbolObject):
        raise RuntimeError, "'set' requires a symbol!"
    e_val = val.message( scope, 'eval' )
    scope.set( var.data, e_val )
    return e_val
SetObject.methods['call'] = PyFormMethod( set_call )
Builtins['set'] = SetObject

QuoteObject = Object(SpecialFormObject, "quote")
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
        
QuoteObject.methods['call'] = PyFormMethod( quote_call )
Builtins['quote'] = QuoteObject

IfObject = Object(SpecialFormObject, "if")
def if_call( scope, obj, cond, conseq, *rest):
    bool = cond.message( scope, 'eval' ).message( scope, 'bool' )
    if bool.data:
        return conseq.message( scope, 'eval' )
    elif len(rest)==0:
        return make_nil()
    elif len(rest)==1:
        return rest[0].message( scope, 'eval' )
    else:
        return if_call( scope, obj, rest[0], rest[1], *rest[2:] )
IfObject.methods['call'] = PyFormMethod( if_call )
Builtins['if'] = IfObject

WhileObject = Object(SpecialFormObject, "while")
BreakObject = Object(FunctionObject, "break")
ContinueObject = Object(FunctionObject, "continue")
class BreakException(Exception): pass
class ContinueException(Exception): pass
def while_call( scope, obj, cond, *body ):
    ret = make_nil()
    while True:
        bool = cond.message(scope,'eval').message(scope,'bool')
        if not bool.data:
            return ret
        try:
            for i in body:
                ret = i.message(scope,'eval')
        except BreakException:
            ret = make_nil()
            break
        except ContinueException:
            continue
    return ret
def break_call( scope, obj ):
    raise BreakException, "break called outside of a while loop"
def continue_call( scope, obj ):
    raise ContinueException, "continue called outside of a while loop"
WhileObject.methods['call'] = PyFormMethod( while_call )
Builtins['while'] = WhileObject
BreakObject.methods['call'] = PyFnMethod( break_call )
Builtins['break'] = BreakObject
ContinueObject.methods['call'] = PyFnMethod( continue_call )
Builtins['continue'] = ContinueObject

DirObject = Object(FunctionObject, "dir")
DirObject.methods['call'] = PyFnMethod( lambda scope,obj:
                                            make_list( [ make_symbol(i) for i in
                                                         scope.list_keys() ]))
Builtins['dir'] = DirObject

ConsFnObject = Object(FunctionObject, "cons")
def makecons_call( scope, obj, a, b ):
    return make_cons(a,b)
ConsFnObject.methods['call'] = PyFnMethod( makecons_call )
Builtins['cons'] = ConsFnObject

DefObject = Object( SpecialFormObject, "def" )
def def_call( scope, obj, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Function declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Function name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( FunctionObject, name.data )
    object_def( scope, ret, make_symbol('call'), args, *body )
    scope[name.data] = ret
    return ret
DefObject.methods['call'] = PyFormMethod( def_call )
Builtins['def'] = DefObject

FnObject = Object( SpecialFormObject, "fn" )
def fn_call( scope, obj, args, *body ):
    if not well_formed( args ):
        raise RuntimeError, "Function args must be a list"
    ret = Object( FunctionObject )
    object_def( scope, ret, make_symbol('call'), args, *body )
    return ret
FnObject.methods['call'] = PyFormMethod( fn_call )
Builtins['fn'] = FnObject

DeformObject = Object( SpecialFormObject, "deform" )
def deform_call( scope, obj, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Form declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Form name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( SpecialFormObject, name.data )
    object_deform( scope, ret, make_symbol('call'), args, *body )
    scope[name.data] = ret
    return ret
DeformObject.methods['call'] = PyFormMethod( deform_call )
Builtins['deform'] = DeformObject

FormObject = Object( SpecialFormObject, "form" )
def form_call( scope, obj, args, *body ):
    if not well_formed( args ):
        raise RuntimeError, "Form arguments must be a list."
    ret = Object( SpecialFormObject )
    object_deform( scope, ret, make_symbol('call'), args, *body )
    return ret
FormObject.methods['call'] = PyFormMethod( form_call )
Builtins['form'] = FormObject

AndObject = Object( SpecialFormObject, "and" )
def and_call( scope, obj, *body ):
    for i in body:
        val = i.message(scope,'eval')
        bool = val.message(scope,'bool')
        if bool.data==0:
            return bool
    return make_int(1)
AndObject.methods['call'] = PyFormMethod( and_call )
Builtins['and'] = AndObject

OrObject = Object( SpecialFormObject, "or" )
def or_call( scope, obj, *body ):
    for i in body:
        val = i.message(scope,'eval')
        bool = val.message(scope,'bool')
        if bool.data==1:
            return bool
    return make_int(0)
OrObject.methods['call'] = PyFormMethod( or_call )
Builtins['or'] = OrObject

NotObject = Object( SpecialFormObject, "not" )
def not_call( scope, obj, arg, *rest ):
    if rest:
        command = make_list([arg]+list(rest))
        tmp = command.message(scope,'eval')
    else:
        tmp = arg.message(scope,'eval')
    bool = tmp.message(scope,'bool')
    return make_bool( not bool.data )
NotObject.methods['call'] = PyFormMethod( not_call )
Builtins['not'] = NotObject

ErrorObject = Object( FunctionObject, "error" )
def error_call( scope, obj ):
    raise RuntimeError, "(error) called"
ErrorObject.methods['call'] = PyFnMethod( error_call )
Builtins['error'] = ErrorObject

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
        if self.file.isatty():
            if not os.path.exists(HISTORY_NAME):
                open(HISTORY_NAME,'w').close()
            readline.read_history_file(HISTORY_NAME)
    def getc( self, start=False, gentle=False ):
        if self.buf:
            c = self.buf[0]
            self.buf = self.buf[1:]
            return c
        elif self.file.isatty():
            if gentle:
                return ''
            try:
                self.buf = list(raw_input(PROMPT if start else REPROMPT)+'\n')
                readline.write_history_file(HISTORY_NAME)
                return self.getc( start )
            except EOFError:
                return ''
        else:
            return self.file.read(1)
    def ungetc( self, c ):
        if len(c)>1:
            raise RuntimeError, "OMG!!!!"
        self.buf = [c] + self.buf if c else self.buf
    def gettok( self, start=False, gentle=False ):
        if self.tokbuf:
            tmp = self.tokbuf[0]
            self.tokbuf = self.tokbuf[1:]
            return tmp
        c = self.getc(start,gentle)
        while c and c in string.whitespace:
            c = self.getc(start,gentle)
        if c=='':
            return None
        if c=='#':
            while c not in '\n': # includes empty
                c = self.getc()
            return self.gettok()
        elif c in self.punctuation:
            return c
        elif c not in self.punctuation+string.whitespace:
            chars = [ c ]
            c = self.getc()
            while c not in self.punctuation + string.whitespace:
                chars.append(c)
                c = self.getc()
            self.ungetc(c)
            try:
                return make_int(int(string.join(chars,'')))
            except ValueError:
                return make_symbol( string.join(chars,'') )
    def ungettok( self, tok ):
        self.tokbuf = [tok] + self.tokbuf
    def read_prefixed(self, start=False):
        dict = {'`':'quote','\'':'quote',';':'unquote-splice',',':'unquote'}
        tok = self.gettok(start)
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
    
    def read_infixed(self, prefixed=None, start=False, captured_ptr=None):
        dict = { '.':'msg', ':':'ref' } ##TWO COPIES
        ### The first element of captured_ptr will be set to True
        ### if any infix punctuation was encountered during the call.
        if captured_ptr: captured_ptr[0] = False
        if prefixed==None:
            prefixed = self.read_prefixed(start)
        tok = self.gettok(False,True)
        if tok==None:
            return prefixed #could be None
        elif isinstance(tok,Object) or tok not in self.infixes:
            self.ungettok(tok)
            return prefixed
        else:
            if captured_ptr: captured_ptr[0] = True
            other = self.read_prefixed()
            list = make_list( [make_symbol(dict[tok]), prefixed, other] )
            return self.read_infixed(list)

    def read_sexpr( self, capture_infix=True ):
        dict = { '.':'msg', ':':'ref' } ##TWO COPIES
        tok = self.gettok()
        if tok==None:
            raise RuntimeError, "Ended in sexpr.0"
        elif tok==')':
            return make_nil()
        else:
            self.ungettok(tok)

        captured_ptr = [False]
        first = self.read_infixed( None, False, captured_ptr )
        if first==None:
            raise RuntimeError, "Ended in sexpr.1"
        rest = self.read_sexpr(False)
        
        if capture_infix and captured_ptr[0]:
            return make_list(unmake_list(first)+unmake_list(rest))
        else:
            return make_cons( first, rest )

    def read_obj(self):
        return self.read_infixed(None,True)

###
### REPL
###

def make_global_scope():
    S = Scope( None )
    S.dict = Builtins.copy()
    return S

def run_string( scope, string ):
    buf = Buffer( StringIO(string) )
    obj = buf.read_obj()
    return obj.message(scope,'eval')

def run_file( scope, file ):
    buf = Buffer(file)
    obj = buf.read_obj()
    ret = make_nil()
    while obj:
        ret = obj.message( scope, 'eval' )
        obj = buf.read_obj()
    return ret

def main():
    scope = make_global_scope()

    BUILTINS_PATH = './builtins.y'
    if os.path.isfile(BUILTINS_PATH):
        builtins = open(BUILTINS_PATH)
        run_file( scope, builtins )
        builtins.close()

    buf = Buffer( sys.stdin )
    while True:
        if CATCH_ERRORS:
            ### Protected loop for normal use
            try:
                obj = buf.read_obj()
                if obj==None:
                    print
                    break
            except KeyboardInterrupt:
                print
                continue
            except Exception, e:
                print "ERROR:", e.args
                continue
            try:
                ret = obj.message(scope,'eval')
                ret.message(scope,'print')
            except Exception, e:
                print "ERROR:", e.args
            except KeyboardInterrupt:
                print "INTERRUPT"
                continue
        else:
            ### Unprotected loop for debugging
            obj = buf.read_obj()
            if obj==None:
                print
                break
            ret = obj.message(scope,'eval')
            ret.message(scope,'print')


if __name__=='__main__':
    main()

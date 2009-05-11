#! /usr/bin/python

import sys,os,string,readline,copy
from StringIO import *

### Make this false to see Python error traces
### Will, however, kill the REPL on an error
CATCH_ERRORS = 1

### Terminal prompts
PROMPT = "yalie: "
REPROMPT = "...      "

### Command history
HISTORY_NAME = os.path.expanduser('~/.yalie_history')

### Call stack. Used only for helpful error messages.
CALLSTACK = []

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
            raise RuntimeError, "Could not find a binding for: %s" % key
    def set( self, key, val ):
        ### Returns True on success else False
        if key in self.dict:
            self.dict[key] = val
        elif self.parent != None:
            self.parent.set(key,val)
        else:
            raise RuntimeError, "Could not find a binding for: '%s'" % key
    def let( self, key,val ):
        ### No return
        if key in self.dict:
            raise RuntimeError, "Cannot modify an existing binding"
        self.dict[key] = val
    def __getitem__( self, key ):
        return self.ref( key )
    def __setitem__( self, key, val ):
        self.dict[key] = val
    def all_keys( self ):
        ret = self.dict.keys()
        if self.parent:
            ret += [ i for i in self.parent.all_keys() if i not in ret ]
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
    ###
    ### This is used for passing messages as though they were
    ### passed from userspace, with implicit evaluation and all.
    ### Within Python, this should really only be used by "msg"
    ### and the call method of S-expressions
    ###
    def message( self, message, scope, *args ):
        global CALLSTACK
        params = MethodParams( scope, self, False, False )
        CALLSTACK.append(self)
        ret = self.methods.ref(message).call(params,*args)
        tmp = CALLSTACK.pop(-1)
        # The following is necessary becase "break" and
        # "continue" can jump up in the call stack
        while tmp!=self:
            tmp = CALLSTACK.pop(-1)
        if not isinstance(ret,Object):
            raise TypeError, "Message returning a non-object!!!"
        return ret
    ###
    ### This is usually used for passing messages within Python.
    ### It suppresses implicit evaluation of arguments, which is
    ### important since things aren't getting rebound to variables.
    ###
    def call( self, message, scope, *args ):
        global CALLSTACK
        params = MethodParams( scope, self, True, False )
        CALLSTACK.append(self)
        ret = self.methods.ref(message).call(params,*args)
        tmp = CALLSTACK.pop(-1)
        # The following is necessary becase "break" and
        # "continue" can jump up in the call stack
        while tmp!=self:
            tmp = CALLSTACK.pop(-1)
        if not isinstance(ret,Object):
            raise TypeError, "Call returning a non-object!!!"
        return ret
    ###
    ### This is used for passing messages within Python and specifically
    ### suppressing the evaluation of a macro form. Really only used by
    ### "expand" method of forms.
    ###
    def macroexpand( self, message, scope, *args ):
        global CALLSTACK
        params = MethodParams( scope, self, False, True )
        CALLSTACK.append(self)
        ret = self.methods.ref(message).call(params,*args)
        tmp = CALLSTACK.pop(-1)
        # The following is necessary becase "break" and
        # "continue" can jump up in the call stack
        while tmp!=self:
            tmp = CALLSTACK.pop(-1)
        if not isinstance(ret,Object):
            raise TypeError, "Macroexpand returning a non-object!!!"
        return ret
    def copy( self ):
        ret = Object( None )
        ret.parent = self.parent
        ret.methods = self.methods.copy()
        ret.members = self.members.copy()
        ret.data = copy.copy(self.data)
        ret.repr = self.repr
        return ret

class MethodParams:
    def __init__( self, scope, obj, noeval_args, noeval_ret ):
        self.scope = scope
        self.obj = obj
        self.noeval_args = noeval_args
        self.noeval_ret = noeval_ret

class PyMethod:
    def __init__( self, fn ):
        self.fn = fn
    def call( self, params, *args ):
        # implicitly eval's the args
        if not params.noeval_args:
            args = [ i.call('eval',params.scope) for i in args ]
        ret = self.fn( params, *args )
        return ret

class PyMethodForm( PyMethod ):
    def call( self, params, *args ):
        return self.fn( params, *args )

class LispFnMethod:
    def __init__( self, scope, args, rest_arg, body ):
        self.scope = scope
        self.args = args                 #list of strings
        self.rest_arg = rest_arg         #string or None
        self.body = body                 #list of objects
    def call( self, params, *call_args ):
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
        new_scope['self'] = params.obj
        # pair args off with arg names and chop the list of args
        for i in self.args:
            if params.noeval_args:
                new_scope[i] = call_args[0]
            else:
                new_scope[i] = call_args[0].call('eval',params.scope)
            call_args = call_args[1:]
        # collect any remainder into the final list
        if self.rest_arg:
            if params.noeval_args:
                rest = call_args
            else:
                rest = [ i.call('eval',params.scope) for i in call_args ]
            new_scope[self.rest_arg] = make_list(rest)
        ret = make_nil()
        for i in self.body:
            ret = i.call( 'eval', new_scope )
        return ret
        
class LispFormMethod( LispFnMethod ):
   def call( self, params, *call_args ):
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
        new_scope['self'] = params.obj
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
            ret = i.call( 'eval', new_scope )
        if params.noeval_ret:
            return ret
        else:
            return ret.call( 'eval', params.scope )
        
###
### Builtins
###
Builtins = {}

RootObject = Object(None, "Root")
def print_ret( obj ):
    print repr(obj)
    return obj
def def_method_or_form( is_function, bang, params, shape, *body ):
    if not shape.inherits(ConsObject):
        raise RuntimeError, "Shape must be a list of at least len 1"
    if not well_formed(shape):
        raise RuntimeError, "Shape list must be well-formed"
    shape = unmake_list(shape)
    name = shape[0]
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of method must be a symbol"
    args = shape [1:]
    ## Look for a rest arg
    rest_arg = None
    if args and args[-1].inherits(ConsObject):
        last_ls = unmake_list(args[-1])
        if len(last_ls)>2:
            raise RuntimeError, "Too many items in a method def rest list"
        for i in last_ls:
            if not i.inherits(SymbolObject):
                raise RuntimeError, "non-symbol in args sublist"
        if last_ls[0].data != "rest":
            raise RuntimeError, "Unknown argument tag: %s" % last_ls[0].data
        ## with tests passed, strip rest arg
        rest_arg = last_ls[1].data
        args = args[:-1]
    ## Check rest of args
    for i in args:
        if not i.inherits(SymbolObject):
            raise RuntimeError, "non-symbol in args list"
    arg_names = []
    for i in args:
        if i.data in arg_names:
            raise RuntimeError, "Two arguments can't have the same name."
        arg_names.append(i.data)
    if rest_arg!=None and rest_arg in arg_names:
        raise RuntimeError, "Two arguments can't have the same name."
    
    if is_function:
        if bang:
            params.obj.methods[name.data] = \
                LispFnMethod( params.scope, arg_names, rest_arg, body )
        else:
            params.obj.methods.let( name.data,
                             LispFnMethod(params.scope,arg_names,rest_arg,body))
    else:
        if bang:
            params.obj.methods[name.data] = \
                LispFormMethod( params.scope, arg_names, rest_arg, body )
        else:
            params.obj.methods.let(name.data,
                       LispFormMethod(params.scope,arg_names,rest_arg,body))
    return params.obj
def object_def( params, shape, *body ):
    return def_method_or_form( True, False, params, shape, *body )
def object_defbang( params, shape, *body ):
    return def_method_or_form( True, True, params, shape, *body )
def object_deform( params, shape, *body ):
    return def_method_or_form( False, False, params, shape, *body )
def object_deformbang( params, shape, *body ):
    return def_method_or_form( False, True, params, shape, *body )
def object_dup( params, name, new_name ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of method must be a symbol."
    if not new_name.inherits(SymbolObject):
        raise RuntimeError, "New name of method must be a symbol."
    params.obj.methods.let(new_name.data, params.obj.methods[name.data])
    return params.obj
def object_dupbang( params, name, new_name ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of method must be a symbol."
    if not new_name.inherits(SymbolObject):
        raise RuntimeError, "New name of method must be a symbol."
    params.obj.methods[new_name.data] = params.obj.methods[name.data]
    return params.obj
def object_set( params, name, val ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of member must be a symbol."
    ret = val.call('eval',params.scope) if not params.noeval_args else val
    params.obj.members.set(name.data,ret)
    return ret
def object_let( params, name, val ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of member must be a symbol."
    ret = val.call('eval',params.scope) if not params.noeval_args else val
    params.obj.members.let(name.data,ret)
    return ret
def object_get( params, name ):
    if not name.inherits(SymbolObject):
        raise RuntimeError, "Name of member must be a symbol."
    return params.obj.members[name.data]
def object_isa( params, arg ):
    return make_bool( params.obj.inherits(arg) )
def object_eq( params, arg ):
    return make_bool(params.obj==arg)
def object_parent( params ):
    if params.obj.parent:
        return params.obj.parent
    else:
        raise RuntimeError, "Root object has no parent to return."

RootObject.methods['eval'] = PyMethod( lambda params : params.obj )
RootObject.methods['eq'] = PyMethod( object_eq )
RootObject.methods['is'] = PyMethod( object_eq )
RootObject.methods['bool'] = PyMethod( lambda params : make_int(1) )
RootObject.methods['print'] = PyMethod( lambda params: print_ret(params.obj) )
RootObject.methods['def'] = PyMethodForm( object_def )
RootObject.methods['def!'] = PyMethodForm( object_defbang )
RootObject.methods['deform'] = PyMethodForm( object_deform )
RootObject.methods['deform!'] = PyMethodForm( object_deformbang )
RootObject.methods['dup'] = PyMethodForm( object_dup )
RootObject.methods['dup!'] = PyMethodForm( object_dupbang )
RootObject.methods['set'] = PyMethodForm( object_set )
RootObject.methods['let'] = PyMethodForm( object_let )
RootObject.methods['get'] = PyMethodForm( object_get )
RootObject.methods['parent'] = PyMethod( object_parent )
RootObject.methods['isa'] = PyMethod( object_isa )
RootObject.methods['copy'] = PyMethod( lambda params: params.obj.copy() )
RootObject.methods['child'] = PyMethod( lambda params: Object(params.obj) )
RootObject.methods['methods'] = PyMethod( lambda params:
                                            make_list( [make_symbol(i) for i in
                                              params.obj.methods.all_keys()]))
RootObject.methods['methods*'] = PyMethod( lambda params:
                                             make_list( [make_symbol(i) for i in
                                               params.obj.methods.dict.keys()]))
RootObject.methods['members'] = PyMethod( lambda params:
                                            make_list( [make_symbol(i) for i in
                                              params.obj.members.all_keys()]))
Builtins['Root'] = RootObject

NilObject = Object(RootObject, "Nil")
def make_nil():
    return Object(NilObject)
NilObject.repr = lambda self: "<Object: Nil>" if self==NilObject else "()"
NilObject.methods['bool'] = PyMethod( lambda params : make_int(0) )
NilObject.methods['='] = PyMethod( lambda params,arg:
                                         make_bool(arg.inherits(NilObject)) )
Builtins['Nil'] = NilObject

IntObject = Object(RootObject, "Int")
IntObject.data = 1
IntObject.repr = (lambda self: 
                  "<Object: Int>" if self==IntObject else str(self.data))
def make_int( i ):
    if type(i) not in (type(0),type(0L)):
        raise RuntimeError, "OOPS!!!"
    ret = Object( IntObject )
    ret.data = i
    return ret
def make_bool( val ):
    return make_int(1 if val else 0)
def int_add( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot add int to non-int."
    return make_int( params.obj.data + arg.data )
def int_sub( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( params.obj.data - arg.data )
def int_mul( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( params.obj.data * arg.data )
def int_div( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( params.obj.data // arg.data )
def int_mod( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot subtract int from non-int."
    return make_int( params.obj.data % arg.data )
def int_eq( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot compare int to non-int."
    return make_bool( params.obj.data == arg.data )
def int_lt( params, arg ):
    if not arg.inherits( IntObject ):
        raise RuntimeError, "Cannot compare int to non-int."
    return make_bool( params.obj.data < arg.data )
IntObject.methods['+'] = PyMethod( int_add )
IntObject.methods['-'] = PyMethod( int_sub )
IntObject.methods['*'] = PyMethod( int_mul )
IntObject.methods['/'] = PyMethod( int_div )
IntObject.methods['%'] = PyMethod( int_mod )
IntObject.methods['='] = PyMethod( int_eq )
IntObject.methods['<'] = PyMethod( int_lt )
IntObject.methods['bool'] = PyMethod( lambda params:
                                            make_bool(params.obj.data) )
IntObject.methods['eq'] = PyMethod( lambda params, arg:
                                          make_bool( arg.inherits(IntObject)
                                               and params.obj.data==arg.data ))
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
SymbolObject.methods['eval'] = PyMethod( lambda params:
                                            params.scope.ref(params.obj.data))
SymbolObject.methods['='] = PyMethod( lambda params,arg:
                                            make_bool(arg.inherits(SymbolObject)
                                              and arg.data == params.obj.data))
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
def set_car( params, arg ):
    params.obj.data[0] = arg
    return arg
def set_cdr( params, arg ):
    params.obj.data[1] = arg
    return arg
def cons_eval( params ):
    if not well_formed(params.obj):
        raise RuntimeError, "Cannot evaluate non-well-formed list."
    fn = params.obj.data[0].call('eval',params.scope)
    return fn.message( 'call', params.scope, *unmake_list(params.obj.data[1]) )
def cons_eq( params, arg ):
    if not arg.inherits(ConsObject):
        return make_bool(0)
    b1 = params.obj.data[0].call('=',params.scope,arg.data[0])
    b2 = params.obj.data[1].call('=',params.scope,arg.data[1])
    return make_bool( b1.data and b2.data )
ConsObject.methods['car'] = PyMethod( lambda params: params.obj.data[0] )
ConsObject.methods['cdr'] = PyMethod( lambda params: params.obj.data[1] )
ConsObject.methods['setcar'] = PyMethod( set_car )
ConsObject.methods['setcdr'] = PyMethod( set_cdr )
ConsObject.methods['eval'] = PyMethod( cons_eval )
ConsObject.methods['='] = PyMethod( cons_eq )
Builtins['Cons'] = ConsObject

# This is the general parent of all callables
def operator_call( params, *args):
    raise RuntimeError, "This is not a working function"
OperatorObject = Object(RootObject, "Operator")
OperatorObject.repr = lambda self: "<Operator%s>" % (': '+self.name if
                                                     self.name else '')
OperatorObject.methods['call'] = PyMethod( operator_call )
Builtins['Operator'] = OperatorObject

FunctionObject = Object(OperatorObject, "Function")
FunctionObject.repr = lambda self: "<Function%s>" % (': '+self.name if
                                                     self.name else '')
FunctionObject.methods['call'] = PyMethod( operator_call )
Builtins['Function'] = FunctionObject

SpecialFormObject = Object(OperatorObject, "Form")
SpecialFormObject.repr = lambda self: "<Form%s>" % (': '+self.name if 
                                                    self.name else '')
SpecialFormObject.methods['call'] = PyMethodForm( operator_call )
Builtins['Form'] = SpecialFormObject

CallObject = Object(FunctionObject,"call")
def call_call( params, fn, *args ):
    if args[-1].inherits(ConsObject) or args[-1].inherits(NilObject):
        args = list(args[:-1]) + unmake_list(args[-1])
    if not fn.inherits(OperatorObject):
        raise RuntimeError, "'call' expects to receive an operator"
    # note that fn.call is used here to suppress evaluation
    return fn.call('call', params.scope, *args )
CallObject.methods['call'] = PyMethod(call_call)
Builtins['call'] = CallObject

MsgObject = Object(SpecialFormObject, "msg")
def msg_call( params, recipient, message, *args ):
    if not message.inherits( SymbolObject ):
        raise RuntimeError, "'msg' requires a symbol as a message"
    #evaluate the recipient
    _recipient = recipient.call('eval',params.scope) if not params.noeval_args\
        else recipient
    #pass the message
    # Note that ".message" is used here, instead of .call
    return _recipient.message( message.data, params.scope, *args )    
MsgObject.methods['call'] = PyMethodForm( msg_call )
Builtins['msg'] = MsgObject

ExpandObject = Object(SpecialFormObject, "msg")
def expand_call( params, recipient, message, *args ):
    if not message.inherits( SymbolObject ):
        raise RuntimeError, "'expand' requires a symbol as a message"
    #evaluate the recipient
    _recipient = recipient.call('eval',params.scope) if not params.noeval_args\
        else recipient
    if not isinstance(_recipient.methods['call'], LispFormMethod):
        raise RuntimeError, "Only forms defined in Yalie can be expanded"
    #pass the message
    return _recipient.macroexpand( message.data, params.scope, *args )    
ExpandObject.methods['call'] = PyMethodForm( expand_call )
Builtins['expand'] = ExpandObject

LetObject = Object(SpecialFormObject, "let")
def let_call( params, *body ):
    if body[0].inherits(ConsObject) or body[0].inherits(NilObject):
        new_scope = Scope(params.scope)
        bindings = unmake_list(body[0])
        if len(bindings)%2!=0:
            raise RuntimeError, "'let' requires an even number of initial args"
        for i in [bindings[i] for i in range(len(bindings)) if i%2==0]:
            if not i.inherits(SymbolObject):
                raise RuntimeError, "'let' cannot bind a non-symbol"
        while bindings:
            if params.noeval_args:
                new_scope.let(bindings[0].data, bindings[1])
            else:
                new_scope.let(bindings[0].data,
                              bindings[1].call('eval',params.scope))
            bindings = bindings[2:]
        ret = make_nil()
        for i in body[1:]:
            ret = i.call('eval',new_scope)
        return ret
    elif len(body)==2:
        if not body[0].inherits(SymbolObject):
            raise RuntimeError, "'let' requires a symbol!"
        val = body[1].call('eval',params.scope) if not params.noeval_args \
            else body[1]
        params.scope.let( body[0].data, val )
        return val
    else:
        raise RuntimeError, "'let' not formatted properly"
LetObject.methods['call'] = PyMethodForm( let_call )
Builtins['let'] = LetObject

SetObject = Object(SpecialFormObject, "set")
def set_call( params, var, val ):
    if not var.inherits(SymbolObject):
        raise RuntimeError, "'set' requires a symbol!"
    _val = val.call('eval',params.scope) if not params.noeval_args\
        else val
    params.scope.set( var.data, _val )
    return _val
SetObject.methods['call'] = PyMethodForm( set_call )
Builtins['set'] = SetObject

QuoteObject = Object(SpecialFormObject, "quote")
def quote_call( params, arg ):
    if not arg.inherits( ConsObject ):
        return arg
    list = unmake_list(arg)
    if list[0].inherits(SymbolObject) and list[0].data=='unquote-splice':
        raise RuntimeError, "Can't splice into nothing."
    if list[0].inherits(SymbolObject) and list[0].data=='unquote':
        if len(list)>2:
            raise RuntimeError, "too many to unquote"
        return list[1].call('eval',params.scope)
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
                    raise RuntimeError, "too many args to unquote"
                ret.append( ls[1].call('eval',scope) )
            elif ls[0].inherits(SymbolObject) and ls[0].data=='unquote-splice':
                if len(ls)>2:
                    raise RuntimeError, "too many args to unquote-splice"
                tmp = ls[1].call('eval',scope)
                if not tmp.inherits(ConsObject) and not tmp.inherits(NilObject):
                    raise RuntimeError, "cannot splice non-list"
                ls2 = unmake_list( tmp )
                ret = ret + ls2
            else:
                ret.append(quote_list(scope,i))
        return make_list(ret)

    ## And now we are ready to return from quote_call
    return quote_list( params.scope, arg )
        
QuoteObject.methods['call'] = PyMethodForm( quote_call )
Builtins['quote'] = QuoteObject

IfObject = Object(SpecialFormObject, "if")
def if_call( params, cond, conseq, *rest):
    _cond = cond.call('eval', params.scope) if not params.noeval_args else cond
    bool = _cond.call( 'bool', params.scope )
    if bool.data:
        return conseq.call('eval',params.scope) if not params.noeval_args \
            else conseq
    elif len(rest)==0:
        return make_nil()
    elif len(rest)==1:
        return rest[0].call('eval',params.scope) if not params.noeval_args \
            else rest[0]
    else:
        return if_call( params, rest[0], rest[1], *rest[2:] )
IfObject.methods['call'] = PyMethodForm( if_call )
Builtins['if'] = IfObject

WhileObject = Object(SpecialFormObject, "while")
BreakObject = Object(FunctionObject, "break")
ContinueObject = Object(FunctionObject, "continue")
class BreakException(Exception): pass
class ContinueException(Exception): pass
def while_call( params, cond, *body ):
    ret = make_nil()
    while True:
        bool = cond.call('eval',params.scope).call('bool',params.scope)
        if not bool.data:
            return ret
        try:
            for i in body:
                ret = i.call('eval',params.scope)
        except BreakException:
            ret = make_nil()
            break
        except ContinueException:
            continue
    return ret
def break_call( params ):
    raise BreakException, "break called outside of a while loop"
def continue_call( params ):
    raise ContinueException, "continue called outside of a while loop"
WhileObject.methods['call'] = PyMethodForm( while_call )
Builtins['while'] = WhileObject
BreakObject.methods['call'] = PyMethod( break_call )
Builtins['break'] = BreakObject
ContinueObject.methods['call'] = PyMethod( continue_call )
Builtins['continue'] = ContinueObject

DirObject = Object(FunctionObject, "dir")
DirObject.methods['call'] = PyMethod( lambda params:
                                            make_list( [ make_symbol(i) for i in
                                                    params.scope.all_keys() ]))
Builtins['dir'] = DirObject

ConsFnObject = Object(FunctionObject, "cons")
def makecons_call( params, a, b ):
    return make_cons(a,b)
ConsFnObject.methods['call'] = PyMethod( makecons_call )
Builtins['cons'] = ConsFnObject

DefObject = Object( SpecialFormObject, "def" )
def def_call( params, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Function declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Function name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( FunctionObject, name.data )
    ret.call( 'def', params.scope, make_cons(make_symbol('call'),args), *body )
    params.scope.let(name.data,ret)
    return ret
DefObject.methods['call'] = PyMethodForm( def_call )
Builtins['def'] = DefObject

DefbangObject = Object( SpecialFormObject, "def" )
def defbang_call( params, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Function declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Function name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( FunctionObject, name.data )
    ret.call( 'def', params.scope, make_cons(make_symbol('call'),args), *body )
    params.scope[name.data] = ret
    return ret
DefbangObject.methods['call'] = PyMethodForm( defbang_call )
Builtins['def!'] = DefbangObject

DeformObject = Object( SpecialFormObject, "deform" )
def deform_call( params, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Form declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Form name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( SpecialFormObject, name.data )
    ret.call('deform',params.scope,make_cons(make_symbol('call'),args), *body )
    params.scope.let(name.data, ret)
    return ret
DeformObject.methods['call'] = PyMethodForm( deform_call )
Builtins['deform'] = DeformObject

DeformbangObject = Object( SpecialFormObject, "deform" )
def deformbang_call( params, shape, *body ):
    if not well_formed( shape ) or shape.inherits(NilObject):
        raise RuntimeError, "Form declaration must be of form (f ...)"
    if not shape.data[0].inherits(SymbolObject):
        raise RuntimeError, "Form name must be a symbol"
    name = shape.data[0]
    args = shape.data[1]
    ret = Object( SpecialFormObject, name.data )
    ret.call('deform',params.scope,make_cons(make_symbol('call'),args), *body )
    params.scope[name.data] = ret
    return ret
DeformbangObject.methods['call'] = PyMethodForm( deformbang_call )
Builtins['deform!'] = DeformbangObject

AndObject = Object( SpecialFormObject, "and" )
def and_call( params, *body ):
    for i in body:
        val = i.call('eval',params.scope) if not params.noeval_args else i
        bool = val.call('bool',params.scope)
        if bool.data==0:
            return bool
    return make_int(1)
AndObject.methods['call'] = PyMethodForm( and_call )
Builtins['and'] = AndObject

OrObject = Object( SpecialFormObject, "or" )
def or_call( params, *body ):
    for i in body:
        val = i.call('eval',params.scope) if not params.noeval_args else i
        bool = val.call('bool',params.scope)
        if bool.data==1:
            return bool
    return make_int(0)
OrObject.methods['call'] = PyMethodForm( or_call )
Builtins['or'] = OrObject

NotObject = Object( SpecialFormObject, "not" )
def not_call( params, arg, *rest ):
    if rest:
        command = make_list([arg]+list(rest))
        tmp = command.call('eval',params.scope)
    else:
        tmp = arg.call('eval',params.scope) if not params.noeval_args else arg
    bool = tmp.call('bool',params.scope)
    return make_bool( not bool.data )
NotObject.methods['call'] = PyMethodForm( not_call )
Builtins['not'] = NotObject

ErrorObject = Object( FunctionObject, "error" )
def error_call( params, *args ):
    ### Takes arguments essentially for comments
    raise RuntimeError, "(error) called"
ErrorObject.methods['call'] = PyMethodForm( error_call )
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

def error_report( exception_args ):
    # clears the call stack
    global CALLSTACK
    print "ERROR CONTEXT (most recent call last)"
    count = 0
    for i in CALLSTACK:
        if not i.inherits(ConsObject):
            continue
        count += 1
        print "%i:" % count,
        i.call('print',None)
    CALLSTACK = []
    if len(exception_args)>=1:
        print "ERROR:",
        print exception_args[0]

def make_global_scope():
    S = Scope( None )
    S.dict = Builtins.copy()
    return S

def run_string( scope, string ):
    buf = Buffer( StringIO(string) )
    obj = buf.read_obj()
    return obj.call('eval',scope)

def run_file( scope, file ):
    buf = Buffer(file)
    obj = buf.read_obj()
    ret = make_nil()
    while obj:
        ret = obj.call('eval',scope)
        obj = buf.read_obj()
    return ret

def main():
    scope = make_global_scope()

    BUILTINS_NAME = 'builtins.y'
    if os.path.isfile('./' + BUILTINS_NAME):
        builtins = open('./' + BUILTINS_NAME)
    elif os.path.isfile( os.path.dirname(sys.argv[0]) + '/' + BUILTINS_NAME ):
        builtins = open( os.path.dirname(sys.argv[0]) + '/' + BUILTINS_NAME )
    else:
        raise RuntimeError, "Cannot find file 'builtins.y' Yalie dir " + \
            "or current dir."
    run_file( scope, builtins )
    builtins.close()

    if len(sys.argv)>2:
        sys.stderr.write( "Too many arguments. Zero or one please.\n" )
        return 1
    elif len(sys.argv)==2:
        file = open(sys.argv[1])
        run_file( scope, file )
        file.close()
        return 0

    buf = Buffer( sys.stdin )
    while True:
        if CATCH_ERRORS:
            ### Protected loop for normal use
            try:
                obj = buf.read_obj()
                if obj==None:
                    if sys.stdin.isatty():
                        print
                    break
            except KeyboardInterrupt:
                print
                continue
            except Exception, e:
                error_report(e.args)
                continue
            try:
                ret = obj.call('eval',scope)
                if sys.stdin.isatty():
                    ret.call('print',scope)
            except Exception, e:
                error_report(e.args)
            except KeyboardInterrupt, e:
                print "INTERRUPT"
                error_report(e.args)
                continue
        else:
            ### Unprotected loop for debugging
            try:
                obj = buf.read_obj()
                if obj==None:
                    if sys.stdin.isatty():
                        print
                    break
                ret = obj.call('eval',scope)
                if sys.stdin.isatty():
                    ret.call('print',scope)
            except Exception, e:
                error_report(e.args)
                raise e
            except Exception, e:
                error_report(e.args)
                raise e
            except KeyboardInterrupt, e:
                print "INTERRUPT"
                error_report(e.args)
                raise e

if __name__=='__main__':
    main()

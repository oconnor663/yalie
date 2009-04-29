#! /usr/bin/python

import sys,os,string

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


RootObject = Object(None)
RootObject.methods['eval'] = PyMethod( lambda scope, obj : obj )


IntObject = Object(RootObject)
def make_int( i ):
    if type(i)!=type(0):
        raise RuntimeError, "OOPS!!!"
    ret = Object( IntObject )
    ret.data = i
    return ret
def int_add( scope, obj, other_obj ):
    if not other_obj.inherits( IntObject ):
        raise RuntimeError, "Cannot add int to non-int."
    return make_int( obj.data + other_obj.data )
IntObject.methods['add'] = PyMethod( int_add )


def read_obj( file, c ):
    return clear_whitespace( file, c )

def white(c):
    return c!='' and c in string.whitespace

def clear_whitespace( file, c ):
    while white(c):
        c = file.read(1)
    if c=='':
        return None
    else:
        return read_list(file,c)

def read_list( file, c ):
    if c != '(':
        return read_int(file,c)

    def read_rest( file, c ):
        while white(c):
            c = file.read(1)
        if c=='':
            raise RuntimeError, "unclosed list"
        if c==')':
            return []
        else:
            obj, c = read_obj( file,c )
            rest = read_rest( file, c )
            return [ obj ] + rest

    return (read_rest( file, ' ' ), ' ')

def read_int( file, c ):
    if c not in string.digits:
        return read_symbol( file, c )
    buf = [ c ]
    c = file.read(1)
    while c in string.digits:
        buf.append(c)
        c = file.read(1)
    if c in string.letters:
        raise RuntimeError, "Syntax error reading int"
    return ( int(string.join(buf,'')), c )

def read_symbol( file, c ):
    if c not in string.letters:
        raise RuntimeError, "Not done yet"
    buf = [c]
    c = file.read(1)
    while c in string.letters + string.digits:
        buf.append(c)
        c = file.read(1)
    return ( string.join(buf,''), c )

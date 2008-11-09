from core import *

def parse_args( args_list ):
    def legal_tuple( list ):
        if list.cdr == None:
            return False
        elif list.cdr.cdr and list.cdr.cdr.cdr:
            return False # too long
        elif issymbol(list.car):
            if list.cdr.cdr and not issymbol(list.cdr.cdr.car):
                return False
            else:
                return True
        else:
            return False

    used_symbols = []
    pos_args = None
    rest_arg = None
    is_body = False
    kw_args = None
 
    while args_list and issymbol(args_list.car) and not args_list.car.iskeyword:
        if args_list.car not in used_symbols:
            pos_args = Cons( args_list.car, pos_args )
            used_symbols.append(args_list.car)
        else:
            return Exception( "Duplicate symbol", None )
        args_list = args_list.cdr
    while args_list and iscons(args_list.car):
        if legal_tuple(args_list.car):
            if args_list.car.car not in used_symbols and \
                    (not args_list.car.cdr.cdr or args_list.car.cdr.cdr.car not in used_symbols):
                pos_args = Cons( args_list.car, pos_args )
                used_symbols.append(args_list.car.car)
                if args_list.car.cdr.cdr:
                    used_symbols.append(args_list.car.cdr.cdr.car)
            else:
                return Exception( "Duplicate symbol", None )
            args_list = args_list.cdr
        else:
            return Exception( "Illegal optional tuple %s" % args_list.car, None )
    while args_list:
        if issymbol(args_list.car) and args_list.car.iskeyword:
            if args_list.cdr==None:
                return Exception( "Keyword provided without value", None )
            elif args_list.car.name in (':r',':b'):
                if rest_arg:
                    return Exception( "Duplicate rest/body", None )
                else:
                    is_body = args_list.car.name==':b'
                    if not issymbol(args_list.cdr.car) or args_list.cdr.car.iskeyword:
                        return Exception( "%s needs a symbol" % ('Body' if is_body else 'Rest'), None )
                    if args_list.cdr.car not in used_symbols:
                        rest_arg = args_list.cdr.car
                        used_symbols.append(args_list.cdr.car)
                    else:
                        return Exception( "Duplicate symbol", None )
                    args_list = args_list.cdr.cdr
            elif args_list.car.name==':k':
                if kw_args:
                    return Exception( "Keywords already provided", None )
                args_list = args_list.cdr
                while args_list and \
                        ((issymbol(args_list.car) and not args_list.car.iskeyword) \
                             or iscons(args_list.car)):
                    if issymbol(args_list.car):
                        if args_list.car in used_symbols:
                            return Exception( "duplicate symbol", None )
                        else:
                            used_symbols.append(args_list.car)
                            kw_args = Cons( args_list.car, kw_args )
                    elif legal_tuple(args_list.car):
                        if args_list.car.car not in used_symbols and \
                                (not args_list.car.cdr.cdr or args_list.car.cdr.cdr.car not in used_symbols):
                            kw_args = Cons( args_list.car, kw_args )
                            used_symbols.append(args_list.car.car)
                            if args_list.car.cdr.cdr:
                                used_symbols.append(args_list.car.cdr.cdr.car)
                        else:
                            return Exception( "Duplicate symbol", None )
                    else:
                        return Exception( "Malformed kw arg", None )
                    args_list = args_list.cdr
                if not kw_args:
                    return Exception( "No keyword args provided after :k", None )
            else:
                return Exception( "Unknown keyword %s" % args_list.car, None )
            continue #look for further keywords
        else: #stuff left over
            return Exception( "Weirdness in args list.", None )
    return (pos_args.reverse() if pos_args else None,rest_arg,is_body,kw_args.reverse() if kw_args else None)

def legal_args( args_list, fn ):

    if not isinstance(fn,LispCode) and not isinstance(fn,PyCode):
        return Exception("%s is not a function." % fn, None)

    pos_args = fn.pos_args
    rest_arg = fn.rest_arg
    kw_args = fn.kw_args
    
    min = 0; max = 0
    while pos_args and issymbol(pos_args.car):
        min+=1; max+=1
        pos_args = pos_args.cdr
    if rest_arg:
        max = -1
    else:
        while pos_args:
            max+=1
            pos_args = pos_args.cdr

    kwds = []
    while kw_args:
        if issymbol(kw_args.car):
            kwds.append(kw_args.car.name)
        else:
            kwds.append(kw_args.car.car.name)

    length = 0
    while args_list:
        if issymbol(args_list.car) and args_list.car.iskeyword:
            if args_list.car.name[1:] not in kwds:
                return Exception( "Undefined keyword: %s" % args_list.car.name, None )
            elif not args_list.cdr:
                return Exception( "No argument supplied for keyword", None )
            else:
                kwds.pop(kwds.index(args_list.car.name[1:]))
                args_list = args_list.cdr.cdr
        else:
            length += 1
            args_list = args_list.cdr
    
    if length < min or (max!=-1 and length>max):
        return Exception( "Wrong number of args", None )
    else:
        return True

def make_bindings( vals, fn, env ):
    #returns a dictionary with bindings. assumes correctness.

    def first( tuple ):
        if issymbol(tuple):
            return tuple
        else:
            return tuple.car
    
    def third( tuple ):
        if iscons(tuple) and tuple.cdr and tuple.cdr.cdr:
            return tuple.cdr.cdr.car
        else:
            return False

    if not legal_args(vals,fn):
        raise RuntimeError, "MOOOOOOOOOO!!!!!!!!!!!!!!!!!!!!!"

    pos_args = fn.pos_args
    rest_arg = fn.rest_arg
    rest_bound = False
    kw_args = fn.kw_args
    used_kwds = []
    ret = {}
    
    while vals:
        if issymbol(vals.car) and vals.car.iskeyword:
            ret[vals.car.kw2sym(env).name] = vals.cdr.car
            used_kwds.append(vals.car)
            vals = vals.cdr.cdr
        else:
            if pos_args:
                ret[first(pos_args.car).name] = vals.car
                if third(pos_args.car):
                    ret[third(pos_args.car).name] = True
                vals = vals.cdr
                pos_args = pos_args.cdr
            else:
                if rest_bound:
                    ret[rest_arg.name] = Cons(vals.car,ret[rest_arg.name])
                else:
                    rest_bound = True
                    ret[rest_arg.name] = Cons(vals.car,None)
                vals = vals.cdr
    
    if rest_bound:
        ret[rest_arg.name] = ret[rest_arg.name].reverse()
    else:
        ret[rest_arg.name] = None
                
    while pos_args:
        ret[first(pos_args.car).name] = pos_args.car.cdr.car
        if third(pos_args.car):
            ret[third(pos_args.car).name] = False
        pos_args = pos_args.cdr

    while kw_args:
        if first(kw_args.car) not in used_kwds:
            ret[first(kw_args.car).name] = kw_args.car.cdr.car
            if third(kw_args.car):
                ret[third(kw_args.car).name] = False
        kw_args = kw_args.cdr

    return ret

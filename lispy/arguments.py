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


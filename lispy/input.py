import sys,readline,string,os
from core import *

PREFIX = ( '`', ',', ';' )
BINARY = ( '@', )
DELIMITERS = ('(',')')
TOKENS = PREFIX + BINARY + DELIMITERS

SYNTAX = { '`':"semiquote",
           ',':"unquote",
           ';':"unquote-splice",
           '@':"ref" }

HISTORY = os.path.expanduser('~/.lispyhistory')

class Input():
    def __init__( self, input, env ):
        self.input = input
        if input.isatty():
            if not os.path.exists( HISTORY ):
                open(HISTORY,'w').close()
            readline.read_history_file( HISTORY )
        self.env = env
        self.line = []
        self.linenum = 0
        self.prompt = '>>> '
        self.reprompt = '... '

    def close( self ):
        if self.input.isatty():
            readline.write_history_file(HISTORY)
        else:
            self.input.close()
        self.input = None

    def get_token( self, in_sexp ):
        if self.line:
            if iserror(self.line):
                err = self.line
                self.line = []
                return err
            tmp = self.line[0]
            self.line = self.line[1:]
            return tmp
        else:
            if self.input.isatty():
                try:
                    self.line = tokenize(raw_input(self.reprompt if in_sexp else self.prompt))
                    self.linenum += 1
                except EOFError:
                    return None
            else:
                tmp = self.input.readline()
                if not tmp:
                    return None
                self.line = tokenize(tmp)
                self.linenum += 1
            return self.get_token(in_sexp)

    def peek_token( self ):
        # Intended for implementing syntax. Will NOT read a new line from input.
        if self.line:
            return self.line[0]

        else:
            return None

    def read( self, in_sexp=False ):
        t = self.get_token(in_sexp)
        if iserror(t):
            ret = t
        elif t=='(':
            if in_sexp:
                ret = Cons(self.read(True),self.read(True))
            else:
                ret = self.read(True)
        elif t==')':
            if in_sexp:
                ret = None
            else:
                ret = Exception( "Mismatched paren.", None )
        elif t in PREFIX:
            peek = self.peek_token()
            if peek in (None, ')', '@'):
                ret = Exception( "Misplaced syntax.", None )
            else:
                ret = Cons( self.env.get_sym(SYNTAX[t]), Cons( self.read(True), None ) )
        else:
            val = triage(t,self.env)
            if in_sexp:
                ret = Cons( val, self.read(True) )
            else:
                ret = val
        return ret


def tokenize( line ):  # please do not pass newlines to this function
    chars = list(line)
    ret = []
    while chars:
        current = []
        # clear the whitespace
        while chars and chars[0] in string.whitespace:
            chars = chars[1:]
        if not chars:
            return ret
        # parse strings
        if chars[0] in ('"',"'"):
            current.append(chars[0])
            chars = chars[1:]
            escaped = False
            if not chars:
                    return Exception("Unterminated string.", None)
            while chars[0]!=current[0] or escaped:
                if chars[0]=='\\':
                    escaped = not escaped
                else:
                    escaped = False
                if not escaped: current.append(chars[0]) #to avoid the \
                chars = chars[1:]
                if not chars:
                    return Exception("Unterminated string.", None)
            current.append(chars[0])
            chars = chars[1:]
        # parse tokens
        elif chars[0] in TOKENS:
            current.append(chars[0])
            chars = chars[1:]
        # parse numbers and symbols
        else:
            while chars and chars[0] not in string.whitespace and chars[0] not in TOKENS:
                current.append(chars[0])
                chars = chars[1:]

        ret.append(string.join(current,''))
    return ret

def triage( token, env ):
    if token==None:
        return Exception("EOF",None)
    elif token in TOKENS:
        return token
    elif token[0]=='"':
        return eval(token)
    elif token[0]=="'":
        return eval('r'+token)
    else:
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return env.get_sym(token)

def desyntax( expr ):
    pass

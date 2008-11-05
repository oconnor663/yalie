import sys,readline,string
from core import *

TOKENS = ( '"', "'", '`', '.', ',', '(', ')', '[', ']' )

class TtyInput():
    def __init__( self, file ):
        self.file = file
        self.interactive = file.isatty()
        self.line = None

    def read_char( self ):
        tmp = self.line[0]
        self.line = self.line[1:]
        return tmp

    def read( self ):
        if self.line == None:
            self.line = raw_input('> ')

def tokenize( s ):
    chars = list(s)
    ret = []
    while chars:
        current = []
        # clear the whitespace
        while chars and chars[0] in string.whitespace:
            chars = chars[1:]
        if not chars:
            return ret
        # parse strings
        if chars[0] in ('"',"'"):  # NOTE that this comes before TOKENS, which quotes also are
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
        # parse numbers
        elif chars[0] in string.digits or (chars[0]=='.' and len(chars)>1 and chars[1] in string.digits):
            if chars[0]=='.':
                current.append(chars[0]) #these two lines clear the '.' if there is one
                chars = chars[1:]
            while chars and chars[0] not in string.whitespace and chars[0] not in TOKENS:
                current.append(chars[0])
                chars=chars[1:]
        # parse tokens
        elif chars[0] in TOKENS:
            current.append(chars[0])
            chars = chars[1:]
        # parse symbols
        else:
            while chars and chars[0] not in string.whitespace and chars[0] not in TOKENS:
                current.append(chars[0])
                chars = chars[1:]

        ret.append(string.join(current,''))

    return ret



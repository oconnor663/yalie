import sys,string,readline
from core import *

TOKENS = ( "'", "'", '`', '.', ',', '(', ')', '[', ']' )

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
        if self.line = None:
            self.line = raw_input('> ')



def tokenize( line, env ):
    chars = list(line)
    ret = []
    while chars:
        current = []
        while chars[0] in string.whitespace:
            chars = chars[1:]
        if chars[0] in TOKENS:
            current.append(chars[0])
            chars = chars[1:]
            if current[0] in ('"',"'"):
                current.append(chars[0])
                chars = chars[1:]
                escaped = False
                while chars[0]!=current[0] or escaped:
                    if chars[0]=='\\':
                        escaped = not escaped
                    else:
                        escaped = False
                    current.append(chars[0])
                    chars = chars[1:]
                    if not chars:
                        return Exception("Unterminated string.", None)
                current.append(chars[0])
                chars = chars[1:]
        else:
            while chars[0] not in string.whitespace and chars[0] not in 

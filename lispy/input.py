import sys,string,readline
from core import *

class Input():
    def __init__( self, file ):
        self.file = file
        self.interactive = file.isatty()
        self.buffer = []
    
    def read( self ):
        

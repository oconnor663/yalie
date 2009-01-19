FILES = ../objects/string.c ../objects/num.c ../objects/object.c ../objects/scope.c ../objects/cons_obj.c ../objects/exception_obj.c ../objects/symbol_obj.c ../objects/function.c ../guts/*.c ../repr.c

parser:
	cc -g parser.c lexer.c -lgmp -lreadline ${FILES}

lexer:
	cc -g lexer.c -lgmp ${FILES}

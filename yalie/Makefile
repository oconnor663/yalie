GUTS = guts/cons.c guts/symbol.c guts/table.c guts/array.c guts/exception.c

OBJECTS = objects/object.c objects/cons_obj.c objects/symbol_obj.c \
	  objects/scope.c objects/num.c objects/exception_obj.c \
	  objects/eval.c objects/function.c objects/string.c

PARSER = parser/lexer.c parser/parser.c

FILES =	${GUTS} ${OBJECTS} ${PARSER} main.c repr.c

yalie: ${FILES}
	cc -g -o yalie ${FILES} -lreadline -lgmp

clean:
	rm yalie
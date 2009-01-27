CFLAGS = -g

GUTS = guts/cons.o guts/symbol.o guts/table.o guts/array.o guts/exception.o

OBJECTS = objects/object.o objects/cons_obj.o objects/symbol_obj.o \
	  objects/scope.o objects/num.o objects/exception_obj.o \
	  objects/eval.o objects/function.o objects/string.o

PARSER = parser/lexer.o parser/parser.o

FILES =	${GUTS} ${OBJECTS} ${PARSER} main.o repr.o

yalie: ${FILES}
	cc -g -o yalie ${FILES} -lgmp -lreadline

clean:
	rm yalie ${FILES}

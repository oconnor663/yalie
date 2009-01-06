FILES =	guts/cons.c guts/symbol.c guts/table.c guts/array.c guts/exception.c \
	objects/object.c objects/cons_obj.c objects/symbol_obj.c \
	objects/scope.c objects/num.c objects/parse.c \
	objects/exception_obj.c objects/eval.c objects/function.c \
	objects/string.c

yalie: main.c input.lex input.y ${FILES}
	bison -d input.y
	flex input.lex
	cc -g -o yalie main.c lex.yy.c input.tab.c ${FILES} -lreadline -lgmp

clean:
	rm yalie lex.yy.c input.tab.*
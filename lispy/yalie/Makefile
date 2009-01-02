FILES =	guts/cons.c guts/symbol.c guts/table.c guts/array.c \
	objects/object.c objects/cons_class.c objects/symbol_class.c objects/scope.c

yalie: input.lex input.y ${FILES}
	bison -d input.y
	flex input.lex
	cc -g -o yalie lex.yy.c input.tab.c ${FILES} -lreadline -ll

clean:
	rm yalie lex.yy.c input.tab.*
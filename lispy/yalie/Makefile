yalie: input.tab.c input.tab.h lex.yy.c
	cc -o yalie lex.yy.c input.tab.c -lreadline -ll

input.tab.h: input.y
	bison -d input.y

input.tab.c: input.y
	bison -d input.y

lex.yy.c:
	flex input.lex

clean:
	rm yalie lex.yy.c input.tab.*
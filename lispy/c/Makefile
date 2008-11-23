FILES = main.c core.c input.c
HEADERS = core.h input.h

parser:
	bison -d test.y
	flex test.lex
	cc lex.yy.c test.tab.c core.c repr.c

readline:
	gcc ${FILES} -lreadline


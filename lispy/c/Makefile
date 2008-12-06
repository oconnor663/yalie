test:
	cc test.c hash.c types.c types/*.c -lgmp

parser:
	bison -d input.y && \
	flex input.lex && \
	cc lex.yy.c input.tab.c core.c repr.c -lgmp -lreadline

edit:
	gcc input.c edit.c -lreadline

clean:
	rm a.out lex.yy.c input.tab.h input.tab.c
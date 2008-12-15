parser:
	bison -d input.y && \
	flex input.lex && \
	cc lex.yy.c input.tab.c types.c types/*.c -lgmp -lreadline -g

test:
	cc test.c hash.c types.c types/*.c -lgmp

clean:
	rm a.out lex.yy.c input.tab.h input.tab.c
%{
	#include "core.h"
	#define YYSTYPE val_t
	#include "input.tab.h"
%}

white [ \t\n]
punct [`,;~(){}]

%%

[ \t\n]+     ; //skip whitespace

\(          return *yytext;

\)          return *yytext;

\{          return *yytext;

\}          return *yytext;

[^(){} \t\n]+	 {
                   yylval = new_val( new_sym(yytext), Symbol );
		   return SYMBOL;
		 }

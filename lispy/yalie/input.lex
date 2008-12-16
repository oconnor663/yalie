%{
  #include "types.h"
  #define YYSTYPE val_t
  #include "input.tab.h"
  
  int yynesting = 0;
%}

white [ \t\n]
punct [`,;~(){}]

%%

[ \t\n]+     ; //skip whitespace

\(          { yynesting++; return *yytext; }

\)          { yynesting--; return *yytext; }

\{          { yynesting++; return *yytext; }

\}          { yynesting--; return *yytext; }

[^(){} \t\n]+	 {
                   yylval = new_val( new_sym(yytext), Symbol );
		   return SYMBOL;
		 }

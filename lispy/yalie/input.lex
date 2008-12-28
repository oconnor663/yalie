%{
  #define YYSTYPE val_t
  #include "input.tab.h"
  
  int yynesting = 0;
%}

white [ \t\n]
delim [)(}{]
punct [`,;~(){}]

%%

{white}+     ; //skip whitespace

\(          { yynesting++; return *yytext; }
\)          { yynesting--; return *yytext; }
\{          { yynesting++; return *yytext; }
\}          { yynesting--; return *yytext; }

[^{white}{delim}]+	 {
                            yylval = new_val( new_sym(yytext), Symbol );
			    return SYMBOL;
                         }

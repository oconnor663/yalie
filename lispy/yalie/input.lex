%{
  #define YYSTYPE obj_t
  #include "objects/object.h"
  #include "objects/cons_class.h"
  #include "objects/symbol_class.h"

  #include "input.tab.h"
  
  YYSTYPE yylval;

  int yynesting = 0;
%}

white [ \t\n]
delim [)(}{]
punct [`,;~(){}]

%%

[ \t\n]+     ; //skip whitespace

\(          { yynesting++; return *yytext; }
\)          { yynesting--; return *yytext; }
\{          { yynesting++; return *yytext; }
\}          { yynesting--; return *yytext; }

[^ \t\n(){}]+	 {
                            printf( "found: \"%s\"\n", yytext );
                            yylval = new_symbol_obj(yytext);
			    return SYMBOL;
                         }

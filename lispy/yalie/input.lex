%{
  #define YYSTYPE obj_t
  #include "objects/object.h"
  #include "objects/cons_class.h"
  #include "objects/symbol_class.h"
  #include "objects/num.h"

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

-?[0-9]*    { printf( "integer: %s\n", yytext );
	      yylval = new_int_s(yytext);
	      return OBJECT;
	    }
	      

[^ \t\n(){}]+		 {
                            printf( "symbol: %s\n", yytext );
                            yylval = new_symbol_obj(yytext);
			    return OBJECT;
                         }

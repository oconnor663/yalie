%{
  #define YYSTYPE obj_t
  #include "objects/object.h"
  #include "objects/cons_obj.h"
  #include "objects/symbol_obj.h"
  #include "objects/num.h"
  #include "objects/string.h"

  #include "input.tab.h"
  
  YYSTYPE yylval;

  int yynesting = 0;

  void strip_quotes( char* str );
%}

white [ \t\n]
delim [)(}{]
punct [`,;~(){}]

%%

\"a\"        { yylval = new_string(yytext);
     	       return OBJECT;
	     }

[ \t\n]+     ; //skip whitespace

\(          { yynesting++; return *yytext; }
\)          { yynesting--; return *yytext; }
\{          { yynesting++; return *yytext; }
\}          { yynesting--; return *yytext; }

-?[0-9]+    {
	      printf( "yytext: '%s'\n", yytext );
 	      yylval = new_int_s(yytext);
	      printf( "yytext: '%s'\n", yytext );
	      return OBJECT;
	    }
	      

[^ \t\n(){}\"]+		 {
                            yylval = new_sym_obj(yytext);
			    return OBJECT;
                         }

[^ \t\n]		 {
			   return ERROR;
			 }

%%

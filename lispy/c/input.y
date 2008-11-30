%{
#include <stdio.h>
#include <readline/readline.h>
#include <stdbool.h>
#include "core.h"
#include "repr.h"
 
#define YYSTYPE val_t

void yyerror(const char *str)
{
  fprintf(stderr,"Parse error: %s\n",str);
}
 
int yywrap()
{
  return 1;
} 

#define PROMPT ">>> "
#define REPROMPT "... "

char* getline( bool new_expr )
{
  char* line = readline( new_expr?PROMPT:REPROMPT );
  if (line && line[0]!='\0')
    add_history(line);
  return line;
}

main()
{
  extern FILE* yyin;
  yyparse();
}

%}

%token SYMBOL

%%

program:
	program expr		{ printf("%s\n", repr($2)); }
	|
	;

expr:
	paren_s_expr		{ $$ = $1; }
	| brace_s_expr		{ $$ = $1; }
	| SYMBOL		{ $$ = $1; }
	;

paren_s_expr:
	'(' paren_s_expr_rest	{ $$ = $2; }
	;

paren_s_expr_rest:
	expr paren_s_expr_rest	{ $$ = new_val( new_cons($1,$2), Cons ); }
	| ')'  			{ $$ = new_val( NULL, Nil ); }
	;

brace_s_expr:
	'{' brace_s_expr_rest	{ $$ = $2; }
	;

brace_s_expr_rest:
	expr brace_s_expr_rest	{ $$ = new_val( new_cons($1,$2), Cons ); }
	| '}'  			{ $$ = new_val( NULL, Nil); }
	;

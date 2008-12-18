%{
#include <stdio.h>
#include <stdlib.h>
#include <readline/readline.h>
#include <stdbool.h>
  
#define YYSTYPE val_t
  
  void yyerror( const char* str );
  
  extern yynesting;
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

%%

#define PROMPT ">>> "
#define REPROMPT "... "

char* getline( bool new_expr )
{
  char* line = readline( new_expr?PROMPT:REPROMPT );
  if (line && line[0]!='\0')
    add_history(line);
  return line;
}

char* yyline;
FILE* yystream;
bool yyabort = false;

void yyerror(const char *str)
{
  if (!yyabort)
    fprintf(stderr,"Parse error: %s\n",str);
  yynesting = 0;
}
 
int yywrap()
{
  extern FILE* yyin;

  if (yynesting>0) {
    free(yyline);
    fclose(yystream);
    yyline = getline(false);
    if (yyline==NULL) {
      printf("\n");
      yyabort = true;
      return 1;
    }
    while (yyline[0]=='\0') {
      yyline = getline(false);
      if (yyline==NULL) {
	printf("\n");
	yyabort = true;
	return 1;
      }
    }
    yystream = (FILE*)fmemopen( yyline, strlen(yyline), "r" ); //WHY THIS CAST?
    yyin = yystream;
    return 0;
  }
  return 1;
} 

main()
{
  extern FILE* yyin;
  
  while (true) {
    yyline = getline(true);
    if (yyline==NULL) {
      printf("\n");
      break;
    }
    while (yyline[0]=='\0') {
      yyline = getline(true);
      if (yyline==NULL) {
	printf( "\n" );
	break;
      }
    }
    yystream = (FILE*)fmemopen( yyline, strlen(yyline), "r" ); //WHY THIS CAST?
    yyin = yystream;
    yyparse();
    if (yyabort)
      break;
    free(yyline);
    fclose(yystream);
  }
}

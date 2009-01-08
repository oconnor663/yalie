%{
#include <stdio.h>
#include <stdlib.h>
#include <readline/readline.h>
#include <stdbool.h>

#include "objects/object.h"
#include "objects/cons_obj.h"
#include "objects/symbol_obj.h"
#include "objects/num.h"
#include "guts/cons.h"
#include "objects/parse.h"
#include "guts/array.h"
  
#define YYSTYPE obj_t
  
  void yyerror( const char* str );
  
  extern int yynesting;
  char* yyline;
  FILE* yystream;
  bool yydorepl = false;
  extern FILE* yyin;
  array_t yyret;
  bool yyfailed;
%}

%token OBJECT
%token ERROR

%%

program:
        program expr		{ array_push_back(yyret, $2); }
	|
	;

expr:
	paren_s_expr		{ $$ = $1; }
	| brace_s_expr		{ $$ = $1; }
	| OBJECT		{ $$ = $1; }
	| ERROR			{ yyerror( "Lex error." ); }
	;

paren_s_expr:
	'(' paren_s_expr_rest	{ $$ = $2; }
	;

paren_s_expr_rest:
	expr paren_s_expr_rest	{ $$ = new_cons_obj($1,$2); }
        | ')'  			{ $$ = new_nil_obj(); }
	;

brace_s_expr:
	'{' brace_s_expr_rest	{ $$ = $2; }
	;

brace_s_expr_rest:
	expr brace_s_expr_rest	{ $$ = new_cons_obj($1,$2); }
	| '}'  			{ $$ = new_nil_obj(); }
	;

%%

static char* PROMPT = ">>> ";
static char* REPROMPT = "... ";

void yyerror(const char *str)
{
  fprintf(stderr,"Parse error: %s\n",str);
  yynesting = 0;
  yyfailed = true;
}

int yywrap()
{
  if (yydorepl && yynesting>0) {
    free(yyline);
    fclose(yystream);
    yyline = getline(false);
    if (yyline==NULL) {
      printf("\n");
      return 1;
    }
    while (yyline[0]=='\0') {
      yyline = getline(false);
      if (yyline==NULL) {
	printf("\n");
	return 1;
      }
    }
    yystream = (FILE*)fmemopen( yyline, strlen(yyline), "r" ); //WHY THIS CAST?
    yyin = yystream;
    return 0;
  }
  return 1;
} 

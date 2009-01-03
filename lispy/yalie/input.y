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
%}

%token OBJECT

%%

program:
        program expr		{ array_push(yyret, array_len(yyret), $2); }
	|
	;

expr:
	paren_s_expr		{ $$ = $1; }
	| brace_s_expr		{ $$ = $1; }
	| OBJECT		{ $$ = $1; }
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

/*
static char* getline( bool new_expr )
{
  char* line = readline( new_expr?PROMPT:REPROMPT );
  
  if (line && line[0]!='\0')
    add_history(line);
  return line;
}
*/

void yyerror(const char *str)
{
  fprintf(stderr,"Parse error: %s\n",str);
  yynesting = 0;
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

/*
void repr_cons( obj_t cons, bool at_start )
{
  if (at_start) {
    printf( "(" );
    repr( car(obj_guts(cons)), false );
    repr_cons( cdr(obj_guts(cons)), false );
  }
  else if (is_instance(cons, NilClass))
    printf( ")" );
  else {
    printf( " " );
    repr( car(obj_guts(cons)), false );
    repr_cons( cdr(obj_guts(cons)), false );
  }
}

obj_t repr( obj_t obj, bool at_start )
{
  if (is_instance(obj, IntClass))
    printf( int_repr(obj) );
  else if (is_instance(obj, SymClass))
    printf( obj_guts(obj) );
  else if (is_instance(obj, NilClass))
    printf( "()" );
  else if (is_instance(obj, ConsClass))
    repr_cons( obj, true );
  else
    fprintf( stderr, "Weird object?\n" );
  if (at_start)
    printf( "\n" );

  return obj;
}

main()
{
  init_base_classes();

  while (true) {
    yyline = getline(true);
    if (yyline==NULL) {
      printf("\n");
      yyabort = true;
      break;
    }
    while (yyline[0]=='\0') {
      free(yyline);
      yyline = getline(true);
      if (yyline==NULL) {
	printf( "\n" );
	yyabort = true;
	break;
      }
    }
    if (yyabort)
      break;
    yystream = (FILE*)fmemopen( yyline, strlen(yyline), "r" ); //WHY THIS CAST?
    yyin = yystream;
    yyparse();
    if (yyabort)
      break;
    free(yyline);
    fclose(yystream);
  }
}
*/

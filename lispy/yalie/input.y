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
  
#define YYSTYPE obj_t
  
  void yyerror( const char* str );
  
  extern yynesting;
  
  void repr( obj_t obj, bool at_start );
%}

%token OBJECT

%%

program:
        program expr		{ repr($2, true); }
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

char* PROMPT = ">>> ";
char* REPROMPT = "... ";

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
extern FILE* yyin;

void yyerror(const char *str)
{
  if (!yyabort)
    fprintf(stderr,"Parse error: %s\n",str);
  yynesting = 0;

}
 
int yywrap()
{
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

void repr_cons( obj_t cons, bool at_start )
{
  if (at_start) {
    printf( "(" );
    repr( car(obj_guts(cons)), false );
    repr_cons( cdr(obj_guts(cons)), false );
  }
  else if (is_nil_p(cons))
    printf( ")" );
  else {
    printf( " " );
    repr( car(obj_guts(cons)), false );
    repr_cons( cdr(obj_guts(cons)), false );
  }
}

void repr( obj_t obj, bool at_start )
{
  if (is_int_p(obj))
    printf( int_repr(obj) );
  else if (is_symbol_p(obj))
    printf( obj_guts(obj) );
  else if (is_nil_p(obj))
    printf( "()" );
  else if (is_cons_p(obj))
    repr_cons( obj, true );
  else
    fprintf( stderr, "Weird object?\n" );
  if (at_start)
    printf( "\n" );
}

main()
{
  Init_Base_Classes();
  Init_Symbol_Class();
  Init_Nil_Class();
  Init_Cons_Class();
  Init_Int_Class();

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

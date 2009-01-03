#include <string.h>
#include <readline/readline.h>
#include <assert.h>
#include "parse.h"
#include "../guts/array.h"

extern int yynesting;
extern FILE* yyin;
extern array_t yyret;
extern bool yydorepl;
extern char* yyline;
extern FILE* yystream;
bool yyeof;

static char* PROMPT = ">>> ";
static char* REPROMPT = "... ";

char* getline( bool new_expr )
{
  char* line = readline( new_expr?PROMPT:REPROMPT );
  
  if (line==NULL)
    yyeof = true;

  if (line!=NULL && line[0]!='\0')
    add_history(line);
  return line;
}

obj_t parse_string( char* str )
{
  yydorepl = false;
  yyin = (FILE*)fmemopen( str, strlen(str), "r" ); //why cast?!?!
  yyret = new_array(0,0);
  yyparse();
  fclose(yyin);

  if (array_len(yyret)!=1) {
    if (array_len(yyret) > 1)
      fprintf( stderr, "Too many objects\n" );
    return NULL;
  }

  obj_t ret = array_ref( yyret, 0 );
  free_array( yyret );
  return ret;
}

obj_t parse_file( FILE* file )
{
  yydorepl = false;
  yyin = file;
  yyret = new_array(0,0);
  yyparse();

  if (array_len(yyret)!=1) {
    if (array_len(yyret) > 1)
      fprintf( stderr, "Too many objects\n" );
    return NULL;
  }
  
  obj_t ret = array_ref( yyret, 0 );
  free_array( yyret );
  return ret;
}

obj_t parse_repl()
{
  yyret = new_array(0,0);
  yydorepl = true;
  yyeof = false;
  assert (yynesting==0);

  yyline = getline(true);
  if (yyline==NULL) {
    printf("\n");
    free_array(yyret);
    return NULL;
  }
  while (yyline[0]=='\0') {
    free(yyline);
    yyline = getline(true);
    if (yyline==NULL) {
      printf( "\n" );
      free_array(yyret);
      return NULL;
    }
  }
  yystream = (FILE*)fmemopen( yyline, strlen(yyline), "r" ); //WHY THIS CAST?
  yyin = yystream;
  yyparse();

  free(yyline);
  fclose(yystream);

  if (array_len(yyret)!=1) {
    if (array_len(yyret) > 1)
      fprintf( stderr, "Too many objects\n" );
    return NULL;
  }
  
  obj_t ret = array_ref( yyret, 0 );
  free_array( yyret );
  return ret;
}

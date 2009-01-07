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
extern bool yyfailed;
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
  int yynesting2=yynesting;
  bool yydorepl2=yydorepl, yyfailed2=yyfailed;
  FILE* yyin2=yyin;
  array_t yyret2=yyret;
  
  obj_t ret = NULL;
  yydorepl = false;
  yyfailed = false;
  yyin = (FILE*)fmemopen( str, strlen(str), "r" ); //why cast?!?!
  yyret = new_array(0,0);
  yyparse();
  fclose(yyin);

  if (yyfailed) {
    while (yylex()); // clears the buffer, very important
    goto cleanup;
  }

  if (array_len(yyret)!=1) {
    if (array_len(yyret) > 1)
      fprintf( stderr, "Too many objects\n" );
    goto cleanup;
  }

  ret = array_ref( yyret, 0 );
  free_array( yyret );

 cleanup:
  yynesting=yynesting2;
  yydorepl=yydorepl2;
  yyfailed=yyfailed2;
  yyin=yyin2;
  yyret=yyret2;
  return ret;
}

obj_t parse_file( FILE* file )
{
  yyfailed = false;
  yydorepl = false;
  yyin = file;
  yyret = new_array(0,0);
  yyparse();

  if (yyfailed) {
    while (yylex()); // clears the buffer, very important
    return NULL;
  }

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
  yyfailed = false;
  yynesting = 0;
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

  /*
  yyfailed = true;
  int c;
  while ((c=fgetc(yyin))!=EOF)
    fputc(c,stdout);
  printf( "DONE!\n" );
  */

  free(yyline);
  fclose(yystream);

  if (yyfailed) {
    while (yylex()); // clears the buffer, very important
    return NULL;
  }

  if (array_len(yyret)!=1) {
    if (array_len(yyret) > 1)
      fprintf( stderr, "Too many objects\n" );
    return NULL;
  }
  
  obj_t ret = array_ref( yyret, 0 );
  free_array( yyret );
  return ret;
}

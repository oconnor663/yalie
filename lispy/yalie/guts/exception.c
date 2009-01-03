#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "exception.h"
#include "cons.h"

struct Exception {
  char* error;
  cons_t context; //linked list of char*'s
};

excep_t new_excep( char* error )
{
  excep_t ret = malloc( sizeof(struct Exception) );
  ret->error = strdup(error);
  ret->context = NULL;
  return ret;
}

void free_excep( excep_t excep )
{
  free( excep->error );
  while ( excep->context != NULL ) {
    cons_t tmp = excep->context;
    excep->context = cdr(excep->context);
    free( car(tmp) );
    free_cons( tmp );
  }
  free(excep);
}

void excep_add_context( excep_t excep, char* context )
{
  excep->context = new_cons( strdup(context), excep->context );
}

char* excep_repr( excep_t excep )
{
  char* ret;
  size_t tmp;
  FILE* stream = (FILE*) open_memstream( &ret, &tmp ); //why cast?

  cons_t tmp_context = excep->context;
  while ( tmp_context != NULL ) {
    fprintf( stream, "%s\n", car(tmp_context) );
    tmp_context = cdr(tmp_context);
  }
  fprintf( stream, "%s\n", excep->error );
  
  fclose(stream);
  return ret;
}


// TESTING
/*
main()
{
  excep_t e = new_excep( "MASSIVE ERROR!!!" );
  excep_add_context( e, "In problem:" );
  excep_add_context( e, "In broader problem:" );
  
  char* repr = excep_repr( e );
  printf( "%s", repr );
  free(repr);

  free_excep(e);
}
*/

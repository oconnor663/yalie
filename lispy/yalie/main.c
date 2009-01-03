#include <stdio.h>
#include <stdbool.h>

#include "objects/object.h"
#include "objects/cons_obj.h"
#include "objects/symbol_obj.h"
#include "objects/num.h"
#include "guts/cons.h"
#include "objects/parse.h"

void repr( obj_t obj );

void repr_cons( obj_t cons, bool at_start )
{
  if (at_start) {
    printf( "(" );
    repr( car(obj_guts(cons)) );
    repr_cons( cdr(obj_guts(cons)), false );
  }
  else if (is_instance(cons, NilClass))
    printf( ")" );
  else {
    printf( " " );
    repr( car(obj_guts(cons)) );
    repr_cons( cdr(obj_guts(cons)), false );
  }
}

void repr( obj_t obj )
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
}

void put( obj_t obj )
{
  repr(obj);
  printf( "\n" );
}

int main( int argv, char** argc )
{
  init_base_classes();
  
  while (true) {
    obj_t ret = parse_repl();
    if (yyeof)
      break;
    if (ret==NULL)
      continue;
    put(ret);
  }
}

#include <stdio.h>
#include <stdbool.h>

#include "objects/builtins.h"
#include "guts/guts.h"

#include "repr.c"

void put( obj_t obj )
{
  repr(obj);
  printf( "\n" );
}

obj_t test_fn( int argc, obj_t* argv )
{
  printf( "THIS IS ONLY A TEST\n" );
  return new_nil_obj();
}


int main( int argv, char** argc )
{
  printf( "Yalie v0.3\nPress Ctrl-D to exit.\n" );

  scope_t global_scope = new_scope( NULL );
  
  scope_add( global_scope, get_sym("tfn"), new_func( test_fn, "()") );

  while (true) {
    obj_t ret = parse_repl();
    if (yyeof)
      break;
    if (ret==NULL)
      continue;

    // Let there be light...
    put( eval(global_scope,ret) );
  }
}

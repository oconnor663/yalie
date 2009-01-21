#include <stdio.h>
#include <stdbool.h>

#include "objects/builtins.h"
#include "guts/guts.h"
#include "parser/parser.h"

#include "repr.h"

obj_t test_fn( int argc, obj_t* argv )
{
  printf( "THIS IS ONLY A TEST\n" );
  return new_nil_obj();
}


int main( int argv, char** argc )
{
  printf( "Yalie v0.4\nPress Ctrl-D to exit.\n" );

  scope_t global_scope = new_scope( NULL );
  
  scope_add( global_scope, get_sym("tfn"), new_func( test_fn, "()") );

  parse_t repl = new_repl();

  while (true) {
    bool is_eof;
    obj_t o = read_repl( repl, &is_eof );
    if (is_eof) {
      printf("\n");
      break;
    }
    if (o!=NULL) {
      if (is_excep(o))
	repr(o);
      else
	repr( eval(global_scope,o) );
      printf( "\n" );
    }
  }
}

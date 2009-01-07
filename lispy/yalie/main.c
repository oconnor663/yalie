#include <stdio.h>
#include <stdbool.h>

#include "objects/object.h"
#include "objects/cons_obj.h"
#include "objects/symbol_obj.h"
#include "objects/num.h"
#include "guts/cons.h"
#include "guts/symbol.h"
#include "objects/parse.h"
#include "objects/eval.h"
#include "objects/scope.h"
#include "objects/exception_obj.h"
#include "objects/function.h"
#include "objects/string.h"

void repr( obj_t obj );

void repr_cons( obj_t cons, bool at_start )
{
  if (at_start) {
    printf( "(" );
    repr( cons_car(obj_guts(cons)) );
    repr_cons( cons_cdr(obj_guts(cons)), false );
  }
  else if (is_cons(cons))
    printf( ")" );
  else {  // the null terminator
    printf( " " );
    repr( cons_car(obj_guts(cons)) );
    repr_cons( cons_cdr(obj_guts(cons)), false );
  }
}

void repr( obj_t obj )
{
  if (is_int(obj))
    printf( int_repr(obj) );
  else if (is_sym(obj))
    printf( obj_guts(obj) );
  else if (is_nil(obj))
    printf( "()" );
  else if (is_cons(obj))
    repr_cons( obj, true );
  else if (is_excep(obj))
    printf( excep_obj_repr(obj) );
  else if (is_func(obj))
    printf( func_repr(obj) );
  else if (is_string(obj))
    printf( string_repr(obj) );
  else
    printf( "Weird object?" );
}

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

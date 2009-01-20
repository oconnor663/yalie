#include "objects/builtins.h"
#include "repr.h"

void repr_cons( obj_t cons, bool at_start )
{
  if (at_start) {
    printf( "(" );
    repr( cons_obj_car(cons) );
  repr_cons( cons_obj_cdr(cons), false );
  }
  else if (is_nil(cons))
    printf( ")" );
  else {  // the null terminator
    printf( " " );
    repr( cons_obj_car(cons) );
    repr_cons( cons_obj_cdr(cons), false );
  }
}

void repr( obj_t obj )
{
  char* r;
  if (is_int(obj)) {
    r = int_repr(obj);
    printf( "%s", r );
    free(r);
  }
  else if (is_sym(obj)) {
    r = sym_obj_repr(obj);
    printf( "%s", r );
    free(r);
  }
  else if (is_nil(obj))
    printf( "()" );
  else if (is_cons(obj))
    repr_cons( obj, true );
  else if (is_excep(obj)) {
    r = excep_obj_repr(obj);
    printf( "%s", r );
    free(r);
  }
  else if (is_func(obj)) {
    r = func_repr(obj);
    printf( "%s", r );
    free(r);
  }
  else if (is_string(obj)) {
    r = string_repr(obj);
    printf( "%s", r );
    free(r);
  }
  else
    printf( "Weird object?" );
}


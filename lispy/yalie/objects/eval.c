#include <stdio.h>

#include "builtins.h"
#include "../guts/array.h"

static obj_t error( char* message )
{
  return new_excep_obj( message );
}

obj_t eval( scope_t scope, obj_t code )
{
  // Self-evaluating objects
  // ------------------------
  if ( ! (is_cons(code) || is_sym(code) ) ) {
    return code;
  }

  // Symbols
  // -------
  else if ( is_sym(code) ) {
    obj_t ret = scope_ref( scope, obj_guts(code) );
    if (ret==NULL) {
      char* message;
      char* name = sym_obj_repr(code);
      asprintf( &message, "Lookup failure: %s", name );
      obj_t ret = error(message);
      free(name);
      free(message);
      return ret;
    }
    return ret;
  }

  // S-expressions
  // -------------
  else {
    obj_t head = eval( scope, cons_obj_car(code) );

    // Functions
    // ---------
    if (is_func(head)) {
      array_t evald_args = new_array(0,0);
      obj_t passed_args = cons_obj_cdr(code);
      while (!is_nil(passed_args)) {
	array_push_back(evald_args, eval( scope, cons_obj_car(passed_args) ));
	passed_args = cons_obj_cdr(passed_args);
      }
      int argc = array_len(evald_args);
      obj_t* argv = malloc( sizeof(obj_t)*argc );
      int i;
      for (i=0; i<argc; i++)
	argv[i] = array_ref( evald_args, i );
      return func_apply( head, argc, argv );
    }

    // Everything else
    // ---------------
    return error( "Don't know how to do that yet..." );
  }
}

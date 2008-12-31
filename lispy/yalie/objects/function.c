#include <stdlib.h>
#include <stdbool.h>
#include "function.h"
#include "parse.h"

/*
 *  All C functions intended for exposure into userspace should be of
 *  the form obj_t f( obj_t context, int argc, obj_t* argv ). For
 *  function calls, the lexical scope will be passed in an object
 *  wrapper. For special forms, the dynamic scope will be passed. For
 *  method calls, the calling object will be passed. These functions
 *  can signal an error by returning an exception object.
 */

struct CallParams {
  obj_t args; //a lisp list of the function parameters
              //provided in userspace or generated from
              //a char* string representation
  
  bool eval_args;  //generally true
  bool eval_ret;   //generally false
};

struct CFunction {
  struct CallParams params;
  body_ptr_t body;
};

c_func_t new_c_func( body_ptr_t body, char* args )
{
  c_func_t ret = malloc( sizeof(struct CFunction) );
  ret->params.eval_args = true;
  ret->params.eval_ret = false;
  ret->params.args = parse_string( args ); //already has one reference count
  ret->body = body;
}

void free_c_func( c_func_t f )
{
  obj_del_ref( f->params.args );
  free(f);
}

obj_t apply_c_func( c_func_t f, obj_t context, int argc, obj_t* argv )
{
  return f->body( context, argc, argv );
}

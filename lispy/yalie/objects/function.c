#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include "function.h"
#include "parse.h"

typedef struct Function {
  obj_t args;
  func_ptr_t body;
} * func_s;

obj_t GlobalFuncClass = NULL;

static void init_func_class()
{
  GlobalFuncClass = new_class_obj();
}

obj_t FuncClass()
{
  if (GlobalFuncClass==NULL)
    init_func_class();

  return GlobalFuncClass;
}

obj_t new_func( func_ptr_t body, char* args )
{
  obj_t ret = new_obj( FuncClass() );
  func_s ret_guts = malloc(sizeof(struct Function));
  ret_guts->args = parse_string(args);
  ret_guts->body = body;
  obj_set_guts( ret, ret_guts );
  return ret;
}

obj_t func_apply( obj_t func, int argc, obj_t* argv )
{
  return ((func_s)obj_guts(func))->body( argc, argv );
}

char* func_repr( obj_t func )
{
  char* ret;
  asprintf( &ret, "<function %p>", func );
  return ret;
}

bool is_func( obj_t obj )
{
  return is_instance( obj, FuncClass() );
}

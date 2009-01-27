#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include "function.h"
#include "../parser/parser.h"

/*
 * FUNCTION implementation
 */

typedef struct Function {
  obj_t args;
  func_ptr_t body;
} * func_t;

obj_t new_func( func_ptr_t body, char* args )
{
  obj_t ret = new_obj( FuncClass() );
  func_t ret_guts = malloc(sizeof(struct Function));
  //ret_guts->args = read_string(args); //has a ref count of 1 already
  ret_guts->body = body;
  obj_set_guts( ret, ret_guts );
  return ret;
}

static void del_func( obj_t func )
{
  //obj_del_ref( ((func_t)obj_guts(func))->args );
  free( obj_guts(func) );
}

obj_t func_apply( obj_t func, int argc, obj_t* argv )
{
  return ((func_t)obj_guts(func))->body( argc, argv );
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

obj_t GlobalFuncClass = NULL;

static void init_func_class()
{
  GlobalFuncClass = new_class_obj( del_func );
}

obj_t FuncClass()
{
  if (GlobalFuncClass==NULL)
    init_func_class();

  return GlobalFuncClass;
}

/*
 * METHOD implementation
 */

typedef struct Method {
  obj_t args;
  method_ptr_t body;
} * method_t;

obj_t new_method( method_ptr_t body, char* args )
{
  obj_t ret = new_obj( MethodClass() );
  method_t ret_guts = malloc(sizeof(struct Method));
  //ret_guts->args = parse_string(args);
  ret_guts->body = body;
  obj_set_guts( ret, ret_guts );
  return ret;
}

static void del_method( obj_t method )
{
  //obj_del_ref( ((method_t)obj_guts(method))->args );
  free( obj_guts(method) );
}

obj_t method_apply( obj_t method, obj_t obj, int argc, obj_t* argv )
{
  return ((method_t)obj_guts(method))->body( obj, argc, argv );
}

char* method_repr( obj_t method )
{
  char* ret;
  asprintf( &ret, "<method %p>", method );
  return ret;
}

bool is_method( obj_t obj )
{
  return is_instance( obj, MethodClass() );
}

obj_t GlobalMethodClass = NULL;

static void init_method_class()
{
  GlobalMethodClass = new_class_obj( del_method );
}

obj_t MethodClass()
{
  if (GlobalMethodClass==NULL)
    init_method_class();

  return GlobalMethodClass;
}


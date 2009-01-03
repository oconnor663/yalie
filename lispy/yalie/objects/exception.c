#include "exception.h"
#include "../guts/cons.h"
#include <string.h>
#include <stdlib.h>

typedef struct Exception {
  char* message;
  cons_t context;
} * exception_t;

obj_t Exception_Class;

void Init_Exception_Class()
{
  class_t exception_class = new_class( Object_Class );
  Exception_Class = new_class_obj( exception_class );
}

obj_t new_exception_obj( char* message )
{
  obj_t ret = new_obj( Exception_Class );
  exception_t guts = malloc( sizeof(struct Exception) );
  guts->message = strdup(message);
  guts->context = NULL;
  obj_set_guts( ret, (void*)guts );
  return ret;
}

void append_exception( obj_t exception, char* func_name )
{
  exception_t tmp = obj_guts(exception);
  tmp->context = new_cons( strdup(func_name), tmp->context );
}

char* exception_repr( obj_t exception )
{
  return strdup( "EXCEPTION!!!!" );
}

bool is_exception_p( obj_t obj )
{
  return inherits_p( obj_class(obj), obj_guts(Exception_Class) );
}

#include "exception_obj.h"

obj_t GlobalExcepClass = NULL;

void init_excep_class()
{
  GlobalExcepClass = new_class_obj();
}

obj_t ExcepClass()
{
  if (GlobalExcepClass==NULL)
    init_excep_class();
  return GlobalExcepClass;
}

obj_t new_excep_obj( char* error )
{
  obj_t ret = new_obj( ExcepClass() );
  obj_set_guts( ret, new_excep(error) );
  return ret;
}

void excep_obj_add( obj_t excep, char* context )
{
  excep_add( obj_guts(excep), context );
}

char* excep_obj_repr( obj_t excep )
{
  return excep_repr( obj_guts(excep) );
}

bool is_excep( obj_t obj )
{
  return is_instance( obj, ExcepClass() );
}

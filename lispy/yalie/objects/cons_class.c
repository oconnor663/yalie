#include "object.h"
#include "cons_class.h"
#include "../guts/cons.h"

obj_t Cons_Class;

void Init_Cons_Class()
{
  class_t cons_class = new_class( Object_Class );
  Cons_Class = new_class_obj(cons_class);
}

obj_t new_cons_obj( obj_t a, obj_t b )
{
  obj_t ret = new_obj( Cons_Class );
  obj_set_guts( ret, new_cons( a, b ) );
  obj_add_ref(a);
  obj_add_ref(b);
  return ret;
}

bool is_cons_p( obj_t obj )
{
  return inherits_p( obj_class(obj), obj_guts(Cons_Class) );
}

obj_t Nil_Class;

void Init_Nil_Class()
{
  class_t nil_class = new_class( Object_Class );
  Nil_Class = new_class_obj(nil_class);
}

obj_t new_nil_obj()
{
  obj_t ret = new_obj( Nil_Class );
  return ret;
}

bool is_nil_p( obj_t obj )
{
  return inherits_p( obj_class(obj), obj_guts(Nil_Class) );
}

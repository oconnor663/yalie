#include "object.h"
#include "cons_obj.h"
#include "../guts/cons.h"

obj_t ConsClass;

void init_cons_class()
{
  ConsClass = new_class_obj();
}

obj_t new_cons_obj( obj_t a, obj_t b )
{
  obj_t ret = new_obj( ConsClass );
  obj_set_guts( ret, new_cons( a, b ) );
  obj_add_ref(a);
  obj_add_ref(b);
  return ret;
}

obj_t NilClass;

void init_nil_class()
{
  NilClass = new_class_obj();
}

obj_t new_nil_obj()
{
  obj_t ret = new_obj( NilClass );
  return ret;
}

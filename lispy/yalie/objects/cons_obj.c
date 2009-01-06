#include "object.h"
#include "cons_obj.h"
#include "../guts/cons.h"

obj_t GlobalConsClass = NULL;

static void init_cons_class()
{
  GlobalConsClass = new_class_obj();
}

obj_t ConsClass()
{
  if (GlobalConsClass==NULL)
    init_cons_class();
  return GlobalConsClass;
}

obj_t new_cons_obj( obj_t a, obj_t b )
{
  obj_t ret = new_obj( ConsClass() );
  obj_set_guts( ret, new_cons( a, b ) );
  obj_add_ref(a);
  obj_add_ref(b);
  return ret;
}

obj_t cons_obj_car( obj_t cell )
{
  return cons_car( obj_guts(cell) );
}

obj_t cons_obj_cdr( obj_t cell )
{
  return cons_cdr( obj_guts(cell) );
}

void cons_obj_set_car( obj_t cell, obj_t val )
{
  cons_obj_set_car( obj_guts(cell), (void*)val );
}

void cons_obj_set_cdr( obj_t cell, obj_t val )
{
  cons_obj_set_cdr( obj_guts(cell), (void*)val );
}

bool is_cons( obj_t obj )
{
  return is_instance( obj, ConsClass() );
}

obj_t GlobalNilClass = NULL;

static void init_nil_class()
{
  GlobalNilClass = new_class_obj();
}

obj_t NilClass()
{
  if (GlobalNilClass==NULL)
    init_nil_class();
  return GlobalNilClass;
}

obj_t new_nil_obj()
{
  if (GlobalNilClass==NULL)
    init_nil_class();
  
  obj_t ret = new_obj( NilClass() );
  return ret;
}

bool is_nil( obj_t obj )
{
  return is_instance( obj, NilClass() );
}

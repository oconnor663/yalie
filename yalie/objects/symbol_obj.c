#include "object.h"
#include "symbol_obj.h"
#include "../guts/symbol.h"

obj_t GlobalSymClass = NULL;

static void init_sym_class()
{
  GlobalSymClass = new_class_obj();
}

obj_t SymClass()
{
  if (GlobalSymClass==NULL)
    init_sym_class();
  return GlobalSymClass;
}

obj_t new_sym_obj( char* name )
{
  obj_t ret = new_obj( SymClass() );
  obj_set_guts( ret, get_sym(name) );
  return ret;
}

char* sym_obj_repr( obj_t sym )
{
  return sym_repr( obj_guts(sym) );
}

bool is_sym( obj_t obj )
{
  return is_instance( obj, SymClass() );
}

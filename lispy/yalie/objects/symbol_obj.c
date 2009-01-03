#include "object.h"
#include "symbol_obj.h"
#include "../guts/symbol.h"

obj_t SymClass;

void init_sym_class()
{
  SymClass = new_class_obj();
}

obj_t new_sym_obj( char* name )
{
  obj_t ret = new_obj( SymClass );
  obj_set_guts( ret, get_sym(name) );
  return ret;
}

char* sym_obj_repr( obj_t sym )
{
  return sym_repr( obj_guts(sym) );
}

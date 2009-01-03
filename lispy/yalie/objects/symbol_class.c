#include "object.h"
#include "symbol_class.h"
#include "../guts/symbol.h"

table_t Global_Symbol_Table;

void Init_Global_Symbol_Table()
{
  Global_Symbol_Table = new_sym_table();
}

obj_t Symbol_Class;

void Init_Symbol_Class()
{
  class_t symbol_class = new_class( Object_Class );
  Symbol_Class = new_class_obj( symbol_class );
}

obj_t new_symbol_obj( char* name )
{
  obj_t ret = new_obj( Symbol_Class );
  obj_set_guts( ret, get_sym(Global_Symbol_Table,name) );
  return ret;
}

char* symbol_obj_repr( obj_t sym )
{
  return sym_repr( obj_guts(sym) );
}

bool is_symbol_p( obj_t obj )
{
  return inherits_p( obj_class(obj), obj_guts(Symbol_Class) );
}

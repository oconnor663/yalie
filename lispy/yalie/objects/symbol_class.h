#ifndef symbol_class_h_
#define symbol_class_h_

#include <stdbool.h>
#include "object.h"

extern table_t Global_Symbol_Table;

void Init_Global_Symbol_Table();

extern obj_t Symbol_Class;

void Init_Symbol_Class();
obj_t new_symbol_obj( char* name );

char* symbol_obj_repr( obj_t sym );

bool is_symbol_p( obj_t obj );

#endif

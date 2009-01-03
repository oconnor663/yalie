#ifndef symbol_obj_h_
#define symbol_obj_h_

#include <stdbool.h>
#include "object.h"

extern obj_t SymClass;

void init_sym_class();
obj_t new_sym_obj( char* name );

char* sym_obj_repr( obj_t sym );

#endif

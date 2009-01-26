#ifndef symbol_obj_h_
#define symbol_obj_h_

#include<stdbool.h>
#include "object.h"

obj_t SymClass();

obj_t new_sym_obj( char* name );

char* sym_obj_repr( obj_t sym );

bool is_sym( obj_t obj );

#endif

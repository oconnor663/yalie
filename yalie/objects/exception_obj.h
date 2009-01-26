#ifndef excep_obj_h_
#define excep_obj_h_

#include<stdbool.h>
#include "object.h"
#include "../guts/exception.h"

obj_t ExcepClass();

obj_t new_excep_obj( char* error );

void excep_obj_add( obj_t excep, char* context );

char* excep_obj_repr( obj_t excep );

bool is_excep( obj_t obj );

#endif

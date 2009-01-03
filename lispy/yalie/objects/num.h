#ifndef int_h_
#define int_h_

#include <stdbool.h>
#include "object.h"

extern obj_t IntClass;

void init_int_class();

obj_t new_int_z( long int i );
obj_t new_int_s( char* i );

char* int_repr( obj_t i );

/*
extern obj_t FloatClass;

void init_float_class();

obj_t new_float_f( double x );
obj_t new_float_s( char* x );

char* float_repr( obj_t x );
*/

#endif

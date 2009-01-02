#ifndef int_h_
#define int_h_

#include "object.h"

extern obj_t Integer_Class;

void Init_Integer_Class();

obj_t new_int_z( long int i );
obj_t new_int_s( char* i );

char* int_repr( obj_t i );

/*
extern obj_t Float_Class;

void Init_Float_Class();

obj_t new_float_f( double x );
obj_t new_float_s( char* x );

char* float_repr( obj_t x );
*/

#endif

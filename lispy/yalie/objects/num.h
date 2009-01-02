#ifndef int_h_
#define int_h_

#include <stdbool.h>
#include "object.h"

extern obj_t Integer_Class;

void Init_Int_Class();

obj_t new_int_z( long int i );
obj_t new_int_s( char* i );

char* int_repr( obj_t i );

bool is_int_p( obj_t obj );

/*
extern obj_t Float_Class;

void Init_Float_Class();

obj_t new_float_f( double x );
obj_t new_float_s( char* x );

char* float_repr( obj_t x );
*/

#endif

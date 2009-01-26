#ifndef cons_obj_h_
#define cons_obj_h_

#include<stdbool.h>
#include "object.h"
#include "../guts/cons.h"

obj_t ConsClass();

obj_t new_cons_obj( obj_t a, obj_t b );

obj_t cons_obj_car( obj_t cons );
obj_t cons_obj_cdr( obj_t cons );
void cons_obj_set_cdr( obj_t cons, obj_t val );
void cons_obj_set_cdr( obj_t cons, obj_t val );

bool is_cons( obj_t );

obj_t NilClass();

obj_t new_nil_obj();

bool is_nil( obj_t );

#endif

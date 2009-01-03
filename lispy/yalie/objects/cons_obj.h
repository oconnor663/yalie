#ifndef cons_obj_h_
#define cons_obj_h_

#include <stdbool.h>
#include "object.h"
#include "../guts/cons.h"

extern obj_t Cons_Class;

void Init_Cons_Class();
obj_t new_cons_obj( obj_t a, obj_t b );

bool is_cons_p( obj_t obj );

extern obj_t Nil_Class;

void Init_Nil_Class();
obj_t new_nil_obj();

bool is_nil_p( obj_t obj );

#endif

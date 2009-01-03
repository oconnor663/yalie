#ifndef cons_obj_h_
#define cons_obj_h_

#include <stdbool.h>
#include "object.h"
#include "../guts/cons.h"

extern obj_t ConsClass;

void init_cons_class();
obj_t new_cons_obj( obj_t a, obj_t b );

extern obj_t NilClass;

void init_nil_class();
obj_t new_nil_obj();

#endif

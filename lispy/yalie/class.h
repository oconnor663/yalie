#ifndef class_h_
#define class_h_

#include "object.h"

typedef struct Class * class_t;

class_t new_class();
void free_class( class_t class );

const char* class_type( class_t class );

void class_add_method( class_t class, sym_t name );
something_t class_lookup_method( class_t class, sym_t name );
void class_del_method( class_t class, sym_t name );

#endif

#ifndef class_h_
#define class_h_

#include <stdbool.h>
#include "object.h"

typedef struct Class * class_t;

// The "type" argument should usually be NULL,
// in which case the type of the parent is used.
class_t new_class( class_t parent, sym_t type );
void free_class( class_t class );

bool inherits_p( class_t a, class_t b ); // does a inherit from b?

void class_add_method( class_t class, sym_t name );
something_t class_ref_method( class_t class, sym_t name );
void class_del_method( class_t class, sym_t name );

#endif

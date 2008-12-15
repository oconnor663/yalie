#ifndef class_h_
#define class_h_

#include "object.h"

typedef struct Class * class_t;

class_t new_class();
void free_class( class_t class );

void add_member( class_t class, 

#endif

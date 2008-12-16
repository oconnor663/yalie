#ifndef class_h_
#define class_h_

#include "object.h"

enum Type {
  Nil,
  Symbol,
  Int,
  Float,
  Cons,
  Array,
  Dict,
  Method,
  Class,
  Instance
};

typedef struct Class * class_t;

class_t new_class();
void free_class( class_t class );

void class_add_method( class_t class, 

#endif

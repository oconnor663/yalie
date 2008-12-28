#include "class.h"
#include "symbol.h"

struct Class {
  /*
   *  Class types are strings, but they will be compared by
   *  pointer. This makes it easier to add user-defined types
   *  in C code, but it also requires that we keep track of
   *  pointer and avoid modifying its contents.
   */
  table_t methods;
  class_t parent;
  obj_t parent_obj; // allows the class to hold a reference
};                  // with respect to garbage collection

class_t new_class( class_t parent, obj_t parent_obj );
{
  class_t ret = malloc(sizeof(struct Class));
  ret->parent = parent;
  ret->parent_obj = parent_obj;
  obj_add_ref(parent_obj);
  return ret;
}

void free_class( class_t class )
{
  obj_del_ref(class->parent_obj);
  free(class);
}

bool inherits_p( class_t a, class_t b )
{
  while (b!=NULL) {
    if (a==b)
      return true;
    b = b->parent;
  }
  return false;
}


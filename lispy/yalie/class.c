#include "class.h"
#include "symbol.h"

struct Class {
  /*
   *  Class types are strings, but they will be compared by
   *  pointer. This makes it easier to add user-defined types
   *  in C code, but it also requires that we keep track of
   *  pointer and avoid modifying its contents.
   */
  sym_t type;
  obj_t methods; //will be a dict
};

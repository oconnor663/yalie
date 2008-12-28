#include "object.h"

struct Obj {
  obj_t class;
  void* guts;
  table_t members;
  table_t methods;
  unsigned long int ref_count;
};

#include "object.h"
#include "hash.h"

struct Obj {
  class_t class;
  void* guts;
  table_t members;
  table_t methods;
  int ref_count;
};

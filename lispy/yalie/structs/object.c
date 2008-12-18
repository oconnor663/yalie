#include "object.h"
#include "hash.h"

struct Obj {
  enum Type type;
  obj_t class;
  void* guts;
  obj_t members; //two dicts
  obj_t methods; //
  unsigned long int ref_count;
};

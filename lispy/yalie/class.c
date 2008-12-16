#include "class.h"
#include "hash.h"

struct Class {
  enum Type type;
  table_t methods;
};

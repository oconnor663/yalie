#include <stdlib.h>
#include "cons.h"

struct Cons {
  void* ar;
  void* dr;
};

cons_t new_cons( void* ar, void* dr )
{
  cons_t ret = malloc(sizeof(struct Cons));
  ret->ar = ar;
  ret->dr = dr;
  return ret;
}

void free_cons( cons_t cell )
{
  free(cell);
}

void* cons_car( cons_t cell )
{
  return cell->ar;
}

void* cons_cdr( cons_t cell )
{
  return cell->dr;
}

void cons_set_car( cons_t cell, void* val )
{
  cell->ar = val;
}

void cons_set_cdr( cons_t cell, void* val )
{
  cell->dr = val;
}

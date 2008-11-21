#include <stdio.h>
#include <stdlib.h>
#include "core.h"

val_t new_val( void* obj, enum type type )
{
  val_t ret = malloc(sizeof(struct Val));
  ret->obj = obj;
  ret->type = type;
  ret->ref_count = 1;
  return ret;
}

void add_reference( val_t val )
{
  val->ref_count++;
}

void del_reference( val_t val )
{
  val->ref_count--;
  if (val->ref_count==0)
    fprintf( stderr, "Deleting!\n" );
}


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

void* car( cons_t cell )
{
  return cell->ar;
}

void* cdr( cons_t cell )
{
  return cell->dr;
}


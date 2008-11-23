#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "core.h"

val_t new_val( void* obj, enum type type )
{
  val_t ret = malloc(sizeof(struct Val));
  ret->obj = obj;
  ret->type = type;
  ret->ref_count = 1;
  return ret;
}

void add_ref( val_t val )
{
  val->ref_count++;
}

void del_ref( val_t val )
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


struct Symbol {
  char* name;
};

sym_t new_sym( char* name )
{
  sym_t ret = malloc(sizeof(struct Symbol));
  ret->name = strdup(name);
  return ret;
}

void free_sym( sym_t sym )
{
  free(sym->name);
  free(sym);
}

char* sym_name( sym_t sym )
{
  return strdup(sym->name);
}

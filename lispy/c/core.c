#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>
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

void set_car( cons_t cell, val_t val )
{
  cell->ar = val;
}

void set_cdr( cons_t cell, val_t val )
{
  cell->dr = val;
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

char* repr_sym( sym_t sym )
{
  return strdup(sym->name);
}

struct Int {
  mpz_t integer;
};

int_t new_int_z( long int i )
{
  int_t ret = malloc(sizeof(struct Int));
  mpz_init_set_si(ret->integer,i);
  return ret;
}

int_t new_int_s( char* str, int base )
{
  int_t ret = malloc(sizeof(struct Int));
  mpz_init_set_str( ret->integer, str, base );
  return ret;
}

void free_int( int_t i )
{
  mpz_clear(i->integer);
  free(i);
}

char* repr_int( int_t i )
{
  char* ret;
  int size;
  FILE* stream;
  stream = (FILE*)open_memstream(&ret,&size);
  //WHY DO I NEED TO MAKE THAT CAST???
  mpz_out_str( stream, 10, i->integer );
  fclose(stream);
  return ret;
}

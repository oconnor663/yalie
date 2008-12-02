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
    switch (val->type) {

    case Nil:
      free(val);
      break;

    case Cons:
      del_ref(car(val->obj));
      del_ref(cdr(val->obj));
      free_cons(val->obj);
      free(val);
      break;

    case Symbol:
      free_sym(val->obj);
      free(val);
      break;

    case Int:
      free_int(val->obj);
      free(val);
      break;

    default:
      fprintf( stderr, "del_ref() encountered unknown type.\n" );
      free(val);
      break;
    }
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

void set_car( cons_t cell, void* val )
{
  cell->ar = val;
}

void set_cdr( cons_t cell, void* val )
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
  mpz_t bignum;
};

int_t new_int_z( long int i )
{
  int_t ret = malloc(sizeof(struct Int));
  mpz_init_set_si(ret->bignum,i);
  return ret;
}

int_t new_int_s( char* str, int base )
{
  int_t ret = malloc(sizeof(struct Int));
  mpz_init_set_str( ret->bignum, str, base );
  return ret;
}

void free_int( int_t i )
{
  mpz_clear(i->bignum);
  free(i);
}

char* repr_int( int_t i )
{
  char* ret;
  gmp_asprintf( &ret, "%Zd", i->bignum );
  return ret;
}

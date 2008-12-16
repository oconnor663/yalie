#include <stdlib.h>
#include <gmp.h>
#include "int.h"

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

char* int_repr( int_t i )
{
  char* ret;
  gmp_asprintf( &ret, "%Zd", i->bignum );
  return ret;
}

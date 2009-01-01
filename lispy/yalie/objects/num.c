#include <stdlib.h>
#include <gmp.h>
#include "num.h"

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

static int_t new_int_mpz( mpz_t bignum )
{
  ret = malloc(sizeof(struct Int));
  ret->bignum = bignum;
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

int_t int_add( int_t a, int_t b )
{
  mpz_t c;
  mpz_init(c);
  mpz_add( c, a, b );
  return new_int_mpz(c);
}

int_t int_sub( int_t a, int_t b )
{
  mpz_t c;
  mpz_init(c);
  mpz_sub( c, a, b );
  return new_int_mpz(c);
}

int_t int_neg( int_t i )
{
  mpz_t j;
  mpz_init(j);
  mpz_neg( j, i );
  return new_int_mpz(j);
}

int_t int_abs( int_t i )
{
  mpz_t j;
  mpz_init(j);
  mpz_abs( j, i );
  return new_int_mpz(j);
}

int_t int_mul( int_t a, int_t b )
{
  mpz_t c;
  mpz_init(c);
  mpz_mul( c, a, b );
  return new_int_mpz(c);
}

int_t int_div( int_t a, int_t b )
{
  mpz_t c;
  mpz_init(c);
  mpz_fdiv( c, a, b );
  return new_int_mpz(c);
}

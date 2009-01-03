#include <stdlib.h>
#include <gmp.h>
#include "num.h"

obj_t IntClass;

void init_int_class()
{
  IntClass = new_class_obj();
}

obj_t new_int_z( long int i )
{
  obj_t ret = new_obj( IntClass );
  obj_set_guts( ret, malloc(sizeof(mpz_t)) );
  mpz_init_set_si( *(mpz_t*)obj_guts(ret), i );
  return ret;
}

obj_t new_int_s( char* str )
{
  obj_t ret = new_obj( IntClass );
  obj_set_guts( ret, malloc(sizeof(mpz_t)) );
  mpz_init_set_str( *(mpz_t*)obj_guts(ret), str, 10 );
  return ret;
}

char* int_repr( obj_t i )
{
  char* ret;
  gmp_asprintf( &ret, "%Zd", *(mpz_t*)obj_guts(i) );
  return ret;
}

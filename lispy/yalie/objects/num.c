#include <stdlib.h>
#include <gmp.h>
#include "num.h"

obj_t Int_Class;

void Init_Int_Class()
{
  class_t int_class = new_class( Object_Class );
  Int_Class = new_class_obj( int_class );
}

obj_t new_int_z( long int i )
{
  obj_t ret = new_obj( Int_Class );
  obj_set_guts( ret, malloc(sizeof(mpz_t)) );
  mpz_init_set_si( *(mpz_t*)obj_guts(ret), i );
  return ret;
}

obj_t new_int_s( char* str )
{
  obj_t ret = new_obj( Int_Class );
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

bool is_int_p( obj_t obj )
{
  return inherits_p( obj_class(obj), obj_guts(Int_Class) );
}

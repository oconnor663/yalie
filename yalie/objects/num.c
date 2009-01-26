#include <string.h>
#include <stdlib.h>
#include <gmp.h>
#include "num.h"
#include "function.h"
#include "exception_obj.h"
#include "../guts/symbol.h"

obj_t new_int_z( long int i )
{
  obj_t ret = new_obj( IntClass() );
  obj_set_guts( ret, malloc(sizeof(mpz_t)) );
  mpz_init_set_si( *(mpz_t*)obj_guts(ret), i );
  return ret;
}

obj_t new_int_s( char* str )
{
  obj_t ret = new_obj( IntClass() );
  obj_set_guts( ret, malloc(sizeof(mpz_t)) );
  mpz_init_set_str( *(mpz_t*)obj_guts(ret), str, 10 );
  return ret;
}

static obj_t new_int_mpz( mpz_t* i )
{
  obj_t ret = new_obj( IntClass() );
  obj_set_guts( ret, i );
  return ret;
}

char* int_repr( obj_t i )
{
  char* ret;
  gmp_asprintf( &ret, "%Zd", *(mpz_t*)obj_guts(i) );
  return ret;
}

bool is_int( obj_t obj )
{
  return is_instance( obj, IntClass() );
}

/*
 * Method definitions
 */

static obj_t plus_method( obj_t obj, int argc, obj_t* argv )
{
  // will expect single argument "(i)"
  if (is_int(argv[0])) {
    obj_t arg = argv[0];
    mpz_t* ret_guts = malloc(sizeof(mpz_t));
    mpz_init(*ret_guts);
    mpz_add( *ret_guts, *((mpz_t*)obj_guts(obj)),
	     *((mpz_t*)obj_guts(argv[0])) );
    return new_int_mpz(ret_guts);
  }
  else
    return new_excep_obj( "+ expected integer" );
}

obj_t GlobalIntClass = NULL;

static void init_int_class()
{
  GlobalIntClass = new_class_obj();
  class_add_method( GlobalIntClass, get_sym("+"),
		    new_method(plus_method,"(i)") );
}

obj_t IntClass()
{
  if (GlobalIntClass==NULL)
    init_int_class();
  return GlobalIntClass;
}

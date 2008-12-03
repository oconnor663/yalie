#include <stdlib.h>
#include <stdio.h>
#include "types.h"

main()
{
  sym_t sym = new_sym("SyM");
  val_t s = new_val( sym, Symbol );
  int_t bigint = new_int_z( 554 );
  val_t i = new_val(bigint,Int);
  val_t nil = new_val( NULL, Nil );
  cons_t c1 = new_cons(s,nil);
  val_t C1 = new_val(c1,Cons);
  cons_t c2 = new_cons(i, C1);
  val_t val = new_val( c2, Cons );
  char* ret = repr(val);
  printf( "%s\n", ret );
  del_ref(val);
  free(ret);
}

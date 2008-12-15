#include <stdlib.h>
#include <stdio.h>
#include "types.h"
#include "hash.h"

int hash( void* val, int size )
{
  return 0;
}

bool eq_p( void* a, void* b )
{
  return a==b;
}

void test_hash()
{
  sym_t sa = new_sym("a");
  sym_t sb = new_sym("b");
  sym_t sc = new_sym("c");
  int_t i = new_int_z(1);
  int_t j = new_int_z(2);

  val_t a = new_val(sa, Symbol);
  val_t b = new_val(sb, Symbol);
  val_t c = new_val(i, Int );
  val_t d = new_val(j, Int );
  val_t e = new_val(sc, Symbol );

  char* astr;

  table_t t = new_table( hash, eq_p );
  val_t tmp;

  table_insert(t,a,c,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,b,d,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,a,d,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,e,c,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  table_remove(t,b,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  table_remove(t,e,(void*)&tmp);
  print_table(t);
  table_lookup(t,a,(void*)&tmp);
  astr = repr(tmp);
  printf( "a is: %s\n", astr );
  free(astr);
  free_table(t);
  
  del_ref(a);
  del_ref(b);
  del_ref(c);
  del_ref(d);
  del_ref(e);
}


void test_repr()
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

int main()
{
  test_hash();
  test_repr();
}

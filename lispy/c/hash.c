#include <stdbool.h>
#include <stdlib.h>
#include "hash.h"

int hash( val_t val, int size )
{
  return 0;
}

bool equal_p( val_t a, val_t b )
{
  return a==b;
}

struct Table {
  int size;
  int num_vals;
  cons_t * values;
  //a null terminated cons list whose car elements are themselves cons
  //pairs (key . val)
};

table_t new_table()
{
  table_t ret = malloc( sizeof(struct Table) );
  ret->size = 16;
  ret->num_vals = 0;
  ret->values = malloc( ret->size * sizeof(cons_t) );
  int i;
  for (i=0; i<ret->size; i++)
    ret->values[i] = NULL;
  return ret;
}

void free_table( table_t table )
{
  int i;
  cons_t tmp1, tmp2;
  for (i=0; i<table->size; i++) {
    tmp1 = table->values[i];
    while (tmp1!=NULL) {
      tmp2 = tmp1;
      tmp1 = cdr(tmp1);
      del_ref(car(car(tmp2))); //the key
      del_ref(cdr(car(tmp2))); //the val
      free_cons(car(tmp2)); //the (key.val) pair
      free_cons(tmp2); //the linked list link
    }
  }
  free(table->values);
  free(table);
}

void table_insert( table_t table, val_t key, val_t val )
{
  int h = hash( key, table->size );
  cons_t tmp = table->values[h];
  while (tmp!=NULL) {
    if ( equal_p( key, car(car(tmp)) ) )
      break;
    else
      tmp = cdr(tmp);
  }
  if (tmp==NULL) {
    add_ref(key);
    add_ref(val);
    table->values[h] = new_cons( new_cons(key,val), table->values[h] );
  }
  else {
    del_ref( cdr(car(tmp)) );
    add_ref( val );
    set_cdr( car(tmp), val );
  }
}

#include <stdio.h>
#include "repr.h"

void print_table( table_t table )
{
  int i;
  printf( "Table:\n" );
  for (i=0; i<table->size; i++) {
    printf( "%2i:", i );
    cons_t tmp = table->values[i];
    while(tmp) {
      char* s1 = repr(car(car(tmp)));
      char* s2 = repr(cdr(car(tmp)));
      printf( " %s:%s", s1, s2 );
      free(s1); free(s2);
      tmp = cdr(tmp);
    }
    printf( "\n" );
  }
}

main()
{
  sym_t sa = new_sym("a");
  sym_t sb = new_sym("b");
  int_t i = new_int_z(1);
  int_t j = new_int_z(2);

  val_t a = new_val(sa, Symbol);
  val_t b = new_val(i, Int );
  val_t c = new_val(j, Int );

  table_t t = new_table();
  print_table(t);
  table_insert(t,a,b);
  free_table(t);

  free_sym(sa);
  free_sym(sb);
  free_int(i);
  free_int(j);
  free(a);
  free(b);
  free(c);
}

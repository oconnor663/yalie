#include <stdbool.h>
#include <stdlib.h>
#include <assert.h>
#include "hash.h"

int hash( void* val, int size )
{
  return 0;
}

bool is_p( void* a, void* b )
{
  return a==b;
}

struct Table {
  int size;
  int num_vals;
  cons_t * values;
  // each element of values is a null(not nil)-terminated cons list.
  // the contents of these lists are (key.val) cons pairs
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
      free_cons(car(tmp2)); //the (key.val) pair
      free_cons(tmp2); //the linked list link
    }
  }
  free(table->values);
  free(table);
}

void resize_table( table_t table, int new_size )
{
  int i;
  cons_t* new_values = malloc( new_size*sizeof(cons_t) );
  for (i=0; i<new_size; i++)
    new_values[i] = NULL;

  cons_t tmp1, tmp2;
  for (i=0; i<table->size; i++) {
    tmp1 = table->values[i];
    while (tmp1!=NULL) {
      int new_hash = hash( car(car(tmp1)), new_size );
      tmp2 = tmp1;
      tmp1 = cdr(tmp1);
      set_cdr(tmp2,new_values[new_hash]);
      new_values[new_hash] = tmp2;
    }
  }
  cons_t* tmp = table->values;
  table->values = new_values;
  table->size = new_size;
  free(tmp);
}

void* table_insert( table_t table,
		    int (*hash)(void*, int),
		    bool (*is_p)(void*,void*),
		    void* key,
		    void* val )
// Returns the old value if one existed, or NULL if key is new.
{
  assert( key!=NULL && val != NULL );
  int h = hash( key, table->size );
  cons_t tmp = table->values[h];
  while (tmp!=NULL) {
    if ( is_p( key, car(car(tmp)) ) )
      break;
    else
      tmp = cdr(tmp);
  }
  if (tmp==NULL) {
    table->values[h] = new_cons( new_cons(key,val), table->values[h] );
    table->num_vals++;
    if (table->num_vals > table->size/2)
      resize_table(table,2*table->size);
    return NULL;
  }
  else {
    void* ret = cdr(car(tmp));
    set_cdr( car(tmp), val );
    return ret;
  }
}

void* table_lookup( table_t table,
		    int (*hash)(void*, int),
		    bool (*is_p)(void*,void*),
		    void* key )
// Returns NULL on a failed lookup
{
  int h = hash( key, table->size );
  cons_t tmp = table->values[h];
  while (tmp!=NULL) {
    if ( is_p( key, car(car(tmp)) ) )
      break;
    else
      tmp = cdr(tmp);
  }
  if (tmp==NULL)
    return NULL;
  else
    return cdr(car(tmp));
}


#include <stdio.h>
void print_table( table_t table )
{
  int i;
  printf( "\nTable:\n" );
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
  val_t b = new_val(sb, Symbol);
  val_t c = new_val(i, Int );
  val_t d = new_val(j, Int );

  char* astr;

  table_t t = new_table();
  print_table(t);
  astr = repr(table_lookup(t,hash,is_p,a)?table_lookup(t,hash,is_p,a):"None");
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,hash,is_p,a,c);
  print_table(t);
  astr = repr(table_lookup(t,hash,is_p,a)?table_lookup(t,hash,is_p,a):"None");
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,hash,is_p,b,d);
  print_table(t);
  astr = repr(table_lookup(t,hash,is_p,a)?table_lookup(t,hash,is_p,a):"None");
  printf( "a is: %s\n", astr );
  free(astr);
  table_insert(t,hash,is_p,a,d);
  print_table(t);
  astr = repr(table_lookup(t,hash,is_p,a)?table_lookup(t,hash,is_p,a):"None");
  printf( "a is: %s\n", astr );
  free(astr);
  free_table(t);
  
  del_ref(a);
  del_ref(b);
  del_ref(c);
  del_ref(d);
}


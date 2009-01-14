#include <stdbool.h>
#include <assert.h>
#include "table.h"
#include "cons.h"

struct Table {
  size_t size;
  size_t num_vals;
  cons_t * values;
  // each element of values is a null(not nil)-terminated cons list.
  // the contents of these lists are (key.val) cons pairs
  size_t (*hash)(void*,size_t);
  bool (*eq_p)(void*,void*);
};

table_t new_table( size_t (*hash)(void*, size_t), bool (*eq_p)(void*,void*) )
{
  table_t ret = malloc( sizeof(struct Table) );
  ret->size = 4;
  ret->num_vals = 0;
  ret->values = malloc( ret->size * sizeof(cons_t) );
  size_t i;
  for (i=0; i<ret->size; i++)
    ret->values[i] = NULL;
  ret->hash = hash;
  ret->eq_p = eq_p;
  return ret;
}

void free_table( table_t table )
{
  size_t i;
  cons_t tmp1, tmp2;
  for (i=0; i<table->size; i++) {
    tmp1 = table->values[i];
    while (tmp1!=NULL) {
      tmp2 = tmp1;
      tmp1 = cons_cdr(tmp1);
      free_cons(cons_car(tmp2)); //the (key.val) pair
      free_cons(tmp2); //the linked list link
    }
  }
  free(table->values);
  free(table);
}

size_t pointer_hash( void* ptr, size_t size )
{
  return ((size_t)ptr / sizeof(void*)) % size;
}

bool pointer_eq( void* a, void* b )
{
  return a==b;
}

size_t table_len( table_t table )
{
  return table->num_vals;
}

static void resize_table( table_t table, size_t new_size )
{
  size_t i;
  cons_t* new_values = malloc( new_size*sizeof(cons_t) );
  for (i=0; i<new_size; i++)
    new_values[i] = NULL;

  cons_t tmp1, tmp2;
  for (i=0; i<table->size; i++) {
    tmp1 = table->values[i];
    while (tmp1!=NULL) {
      size_t new_hash = table->hash( cons_car(cons_car(tmp1)), new_size );
      tmp2 = tmp1;
      tmp1 = cons_cdr(tmp1);
      cons_set_cdr(tmp2,new_values[new_hash]);
      new_values[new_hash] = tmp2;
    }
  }
  cons_t* tmp = table->values;
  table->values = new_values;
  table->size = new_size;
  free(tmp);
}

bool table_set( table_t table, void* key, void* val, void** ret )
// Returns 0 if key is new, or 1 if key was old (and sets ret to
// previous value)
{
  assert( key!=NULL && val != NULL );
  size_t h = table->hash( key, table->size );
  cons_t tmp = table->values[h];
  while (tmp!=NULL) {
    if ( table->eq_p( key, cons_car(cons_car(tmp)) ) )
      break;
    else
      tmp = cons_cdr(tmp);
  }
  if (tmp==NULL) {
    table->values[h] = new_cons( new_cons(key,val), table->values[h] );
    table->num_vals++;
    if (table->num_vals > table->size/2)
      resize_table(table,2*table->size);
    return 0;
  }
  else {
    *ret = cons_cdr(cons_car(tmp));
    cons_set_cdr( cons_car(tmp), val );
    return 1;
  }
}

bool table_ref( table_t table, void* key, void** ret )
// Returns 0 on a failed lookup, 1 and sets ret on success
{
  size_t h = table->hash( key, table->size );
  cons_t tmp = table->values[h];
  while (tmp!=NULL) {
    if ( table->eq_p( key, cons_car(cons_car(tmp)) ) )
      break;
    else
      tmp = cons_cdr(tmp);
  }
  if (tmp==NULL)
    return 0;
  else {
    *ret = cons_cdr(cons_car(tmp));
    return 1;
  }
}

bool table_del( table_t table, void* key, void** ret )
// Returns 0 on failure, 1 and sets ret to old val on success
{
  size_t h = table->hash( key, table->size );
  cons_t tmp = table->values[h];
  cons_t prev = NULL;
  while (tmp!=NULL) {
    if ( table->eq_p( key, cons_car(cons_car(tmp)) ) )
      break;
    else {
      prev = tmp;
      tmp = cons_cdr(tmp);
    }
  }
  if (tmp==NULL)
    return 0;
  else {
    table->num_vals--;
    if (prev==NULL)
      table->values[h] = cons_cdr(tmp);
    else
      cons_set_cdr(prev,cons_cdr(tmp));
    
    *ret = cons_cdr(cons_car(tmp));
    free_cons(cons_car(tmp));
    free_cons(tmp);
    return 1;
  }
}

array_t table_keys( table_t table )
{
  array_t ret = new_array(0,NULL);
  size_t i;
  for (i=0; i<table->size; i++) {
    cons_t tmp = table->values[i];
    while (tmp) {
      array_push_back( ret, cons_car(cons_car(tmp)) );
      tmp = cons_cdr(tmp);
    }
  }
  return ret;
}

array_t table_vals( table_t table )
{
  array_t ret = new_array(0,NULL);
  size_t i;
  for (i=0; i<table->size; i++) {
    cons_t tmp = table->values[i];
    while (tmp) {
      array_push_back( ret, cons_cdr(cons_car(tmp)) ); //note difference
      tmp = cons_cdr(tmp);                             //from above
    }
  }
  return ret;
}

/*
 * For testing purposes.
 */

/*
#include <stdio.h>
void print_table( table_t table )
{
  size_t i;
  printf( "\nTable:\n" );
  for (i=0; i<table->size; i++) {
    cons_t tmp = table->values[i];
    if (tmp) {
      printf( "%2i:", i );
      while(tmp) {
	char* s1 = repr(cons_car(cons_car(tmp)));
	char* s2 = repr(cons_cdr(cons_car(tmp)));
	printf( " %s:%s", s1, s2 );
	free(s1); free(s2);
	tmp = cons_cdr(tmp);
      }
      printf( "\n" );
    }
  }
}  
*/

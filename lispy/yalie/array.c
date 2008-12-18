#include <stdlib.h>
#include <assert.h>
#include "array.h"

struct Array {
  void** contents;
  unsigned long int length; //# of elements
  unsigned long int size;   //allocated space
};

array_t new_array( unsigned long int length, void* val )
{
  array_t ret = malloc( sizeof(struct Array) );
  ret->length = length;
  //minimum size: 8
  ret->size = length>8 ? length : 8;
  ret->contents = malloc( ret->size*sizeof(void*) );
  unsigned long int i;
  for (i=0; i<length; i++)
    ret->contents[i] = val;
  return ret;
}

void free_array( array_t array )
{
  /*
   * NB: Arrays, like Conses and Tables, don't to any
   * bookkeeping. The user needs to keep track of obj
   * references &c.
   */
  free( array->contents );
  free( array );
}

unsigned long int array_len( array_t array )
{
  return array->length;
}

void* array_ref( array_t array, unsigned long int index )
{
  assert( index < array->length );
  return array->contents[index];
}

void array_push( array_t array, unsigned long int index, void* val )
{
  //Pushing onto the index equal to the array length
  //appends an element to the back. Anything greater
  //results in an error and exit. Don't do that.
  assert( index <= array->length );

  if (array->length < array->size) {
    unsigned long int i;
    for (i=array->length; i>index; i--)
      array->contents[i] = array->contents[i-1];
    array->contents[index] = val;
    array->length++;
  }

  else {
    array->size *= 2;
    void** new_contents = malloc( array->size*sizeof(void*) );
    unsigned long int i;
    for (i=0; i<index; i++)
      new_contents[i] = array->contents[i];
    for (i=array->length; i>index; i--)
      new_contents[i] = array->contents[i-1];
    new_contents[index] = val;
    free(array->contents);
    array->contents = new_contents;
    array->length++;
  }
}

void* array_pop( array_t array, unsigned long int index )
{
  assert( index < array->length );

  void* ret = array->contents[index];

  unsigned long int i;
  for (i=index; i<array->length-1; i++)
    array->contents[i] = array->contents[i+1];
  array->length--;

  return ret;
}


//
// FOR TESTING
//
/*
#include <stdio.h>
#include "symbol.h"

void print_array( array_t array )
{
  printf( "%i %i [", array->length, array->size );
  int i;
  for (i=0; i<array->length; i++) {
    char* tmp = sym_repr( (sym_t)array_ref(array,i) );
    printf( "%s, ", tmp );
    free(tmp);
  }
  printf( "]\n" );
}

int main()
{
  sym_t a = new_sym("a");
  sym_t b = new_sym("b");
  sym_t c = new_sym("c");
  sym_t d = new_sym("d");


  array_t array = new_array(0,NULL);
  print_array(array);

  array_push(array,0,a);
  print_array(array);
  array_push(array,0,b);
  print_array(array);
  array_push(array,0,c);
  print_array(array);
  array_push(array,0,d);
  print_array(array);
  array_push(array,0,a);
  print_array(array);
  array_push(array,0,b);
  print_array(array);
  array_push(array,0,c);
  print_array(array);
  array_push(array,0,d);
  print_array(array);

  array_push(array,2,a);
  print_array(array);

  array_pop(array,2);
  print_array(array);
  array_pop(array,5);
  print_array(array);
  array_pop(array,0);
  print_array(array);

  free_array(array);
  free_sym(a);
  free_sym(b);
  free_sym(c);
  free_sym(d);
}
*/

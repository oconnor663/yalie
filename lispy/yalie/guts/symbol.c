#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol.h"

/*
struct Symbol {
  char* name;
};

sym_t new_sym( char* name )
{
  sym_t ret = malloc(sizeof(struct Symbol));
  ret->name = strdup(name);
  return ret;
}

void free_sym( sym_t sym )
{
  free(sym->name);
  free(sym);
}
*/

static int hash_char_star( void* name, int modulus )
{
  char* name_str = name;
  int ret = 0;
  while (*name_str) {
    ret += *name_str;
    name_str++;
  }
  return ret%modulus;
}

static bool char_star_eq( void* a, void* b )
{
  return strcmp( (char*)a, (char*)b ) == 0;
}

table_t new_sym_table()
{
  table_t ret = new_table( hash_char_star, char_star_eq );
  return ret;
}

void free_sym_table( table_t table )
{
  array_t names = table_keys(table); //the vals are just the same ptrs
  int i;
  for (i=0; i<array_len(names); i++)
    free( array_ref(names,i) );
  free_table( table );
  free_array( names );
}

const char* get_sym( table_t sym_table, char* name )
{
  char* ret;
  bool test = table_ref( sym_table, name, (void**)&ret );
  if (test)
    return (const char*) ret;
  else {
    char* new_sym = strdup(name);
    table_add(sym_table, new_sym, new_sym, NULL);
    return (const char*)new_sym;
  }
}

char* sym_repr( sym_t sym )
{
  return strdup(sym_t);
}

// FOR TESTING

/*
main()
{
  table_t t = new_sym_table();

  char* a = "foo";
  char* b = "foo";

  if (a!=b);
    printf( "Not eq.\n" );
      
  if (get_sym(t,a)==get_sym(t,b))
    printf( "These are, though.\n" );

  free_sym_table(t);
}
*/

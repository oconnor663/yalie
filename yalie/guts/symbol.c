#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol.h"

table_t GlobalSymbolTable = NULL;

static size_t char_star_hash( void* name, size_t modulus )
{
  char* name_str = name;
  size_t ret = 0;
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

static table_t init_sym_table()
{
  GlobalSymbolTable = new_table( char_star_hash, char_star_eq );
}

void free_sym_table()
{
  if (GlobalSymbolTable!=NULL) {
    array_t names = table_keys(GlobalSymbolTable); //just the same ptrs
    size_t i;
    for (i=0; i<array_len(names); i++)
      free( array_ref(names,i) );
    free_table( GlobalSymbolTable );
    free_array( names );
  }
}

sym_t get_sym( char* name )
{
  if (GlobalSymbolTable==NULL)
    init_sym_table();

  sym_t ret;
  bool test = table_ref( GlobalSymbolTable, name, (void**)&ret );
  if (test)
    return ret;
  else {
    sym_t new_sym = strdup(name);
    table_set(GlobalSymbolTable, new_sym, new_sym, NULL);
    return new_sym;
  }
}

char* sym_repr( sym_t sym )
{
  return strdup(sym);
}


// FOR TESTING
/*
main()
{
  char* a = "foo";
  char* b = "foo";

  if (a!=b);
    printf( "Not eq.\n" );
      
  if (get_sym(a)==get_sym(b))
    printf( "These are, though.\n" );

  free_sym_table(GlobalSymbolTable);
}
*/

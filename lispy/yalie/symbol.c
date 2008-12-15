#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol.h"

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

char* repr_sym( sym_t sym )
{
  return strdup(sym->name);
}

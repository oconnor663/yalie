#ifndef symbol_h_
#define symbol_h_

#include <stdbool.h>
#include "table.h"

extern table_t GlobalSymbolTable = NULL;

table_t new_sym_table(); //implicit in get_sym()
void free_sym_table( table_t table );

typedef char* sym_t;

sym_t get_sym( char* name );

char* sym_repr( sym_t sym );

#endif

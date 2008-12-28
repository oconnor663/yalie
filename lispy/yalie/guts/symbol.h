#ifndef symbol_h_
#define symbol_h_

#include <stdbool.h>
#include "table.h"

typedef char* sym_t;

//sym_t new_sym( char* name ); //will duplicate name
//void free_sym( sym_t sym );  //frees owned duplicate

table_t new_sym_table();
void free_sym_table( table_t table );
sym_t get_sym( table_t table, char* name );

char* sym_repr( sym_t sym );

#endif

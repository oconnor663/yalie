#ifndef hash_h_
#define hash_h_

#include "core.h"

typedef struct Table * table_t;

table_t new_table();
void free_table( table_t table );

void table_insert( table_t table, val_t key, val_t val );
val_t table_lookup( table_t table, val_t key ); //returns NULL for not-found

#endif

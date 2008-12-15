#ifndef hash_h_
#define hash_h_

#include "types.h"

typedef struct Table * table_t;

table_t new_table( int (*hash)(void*, int), bool (*eq_p)(void*,void*) );
void free_table( table_t table );

int table_insert( table_t table, void* key, void* val, void** ret );

int table_lookup( table_t table, void* key, void** ret );

int table_remove( table_t table, void* key, void** ret );

#endif

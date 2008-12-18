#ifndef hash_h_
#define hash_h_

#include "types.h"

typedef struct Table * table_t;

/*
 * As with other builtin data structures, the hash table is bare
 * bones. The caller must be responsible for all reference
 * bookkeeping, etc.
 */

table_t new_table( int (*hash)(void*, int), bool (*eq_p)(void*,void*) );
void free_table( table_t table );

int table_add( table_t table, void* key, void* val, void** ret );
int table_ref( table_t table, void* key, void** ret );
int table_del( table_t table, void* key, void** ret );

#endif

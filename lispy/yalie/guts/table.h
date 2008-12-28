#ifndef table_h_
#define table_h_

#include <stdbool.h>
#include "array.h"

typedef struct Table * table_t;

/*
 * As with other builtin data structures, the hash table is bare
 * bones. The caller must be responsible for all reference
 * bookkeeping, etc.
 */

table_t new_table( int (*hash)(void*, int), bool (*eq_p)(void*,void*) );
void free_table( table_t table );

int table_ptr_hash( void* ptr, int size );
bool table_ptr_eq( void* a, void* b );

int table_len( table_t table );

// Each of these functions returns 0 on a lookup failure, and
// 1 on success. In the case of add and del, they also set ret
// to the old value, for the user to bookkeep as necessary.
bool table_add( table_t table, void* key, void* val, void** ret );
bool table_ref( table_t table, void* key, void** ret );
bool table_del( table_t table, void* key, void** ret );

array_t table_keys( table_t table );
array_t table_vals( table_t table );
#endif

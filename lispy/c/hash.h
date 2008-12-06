#ifndef hash_h_
#define hash_h_

#include "types.h"

typedef struct Table * table_t;

table_t new_table();
void free_table( table_t table );

void* table_insert( table_t table,
		    int (*hash)(void*, int),
		    bool (*is_p)(void*,void*),
		    void* key,
		    void* val );

void* table_lookup( table_t table,
		    int (*hash)(void*, int),
		    bool (*is_p)(void*,void*),
		    void* key );

void* table_remove( table_t table,
		    int (*hash)(void*, int),
		    bool (*is_p)(void*,void*),
		    void* key );

#endif

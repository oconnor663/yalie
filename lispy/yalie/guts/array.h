#ifndef array_h_
#define array_h_

#include <stdlib.h>

typedef struct Array * array_t;

array_t new_array( size_t length, void* val );
void free_array( array_t array );

size_t array_len( array_t array );
void* array_ref( array_t array, size_t index );
void array_set( array_t array, size_t index, void* val );

void array_push( array_t array, size_t index, void* val );
void* array_pop( array_t array, size_t index );

#endif

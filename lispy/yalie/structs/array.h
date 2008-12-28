#ifndef array_h_
#define array_h_

typedef struct Array * array_t;

array_t new_array( unsigned long int length, void* val );
void free_array( array_t array );

unsigned long int array_len( array_t array );
void* array_ref( array_t array, unsigned long int index );
void array_set( array_t array, unsigned long int index, void* val );

void array_push( array_t array, unsigned long int index, void* val );
void* array_pop( array_t array, unsigned long int index );

#endif

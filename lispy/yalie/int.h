#ifndef int_h_
#define int_h_

typedef struct Int * int_t;

int_t new_int_z( long int i );
int_t new_int_s( char* str, int base );
void free_int( int_t i );
char* repr_int( int_t i );

#endif

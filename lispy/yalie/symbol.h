#ifndef symbol_h_
#define symbol_h_

#include <stdbool.h>

typedef struct Symbol * sym_t;

sym_t new_sym( char* name ); //will duplicate name
void free_sym( sym_t sym );  //frees owned duplicate
char* repr_sym( sym_t sym ); //duplicates again

#endif

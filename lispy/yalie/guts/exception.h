#ifndef exception_h_
#define exception_h_

typedef struct Exception * excep_t;

excep_t new_excep( char* error );
void free_excep( excep_t excep );

void excep_add_context( excep_t excep, char* context );

char* excep_repr( excep_t excep );

#endif

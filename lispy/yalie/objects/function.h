#ifndef function_h_
#define function_h_

#include "object.h"

// Any C function intended for userspace exposure should take this form.
typedef obj_t (*body_ptr_t)(obj_t, int, obj_t*);

typedef struct CFunction * c_func_t;

c_func_t new_c_func( body_ptr_t body, char* args );
void free_c_func( c_func_t f );

obj_t apply_c_func( c_func_t f, obj_t context, int argc, obj_t* argv );

#endif

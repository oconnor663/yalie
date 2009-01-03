#ifndef exception_h_
#define exception_h_

#include <stdbool.h>
#include "object.h"

extern obj_t Exception_Class;

void Init_Exception_Class();

obj_t new_exception_obj( char* message );
void append_exception( obj_t exception, char* func_name );

char* exception_repr( obj_t exception );

bool is_exception_p( obj_t obj );

#endif

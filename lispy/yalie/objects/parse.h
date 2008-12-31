#ifndef parse_h_
#define parse_h_

#include <stdio.h>
#include "object.h"

obj_t parse_string( char* str );
obj_t parse_file( FILE* file );

#endif

#ifndef parser_h_
#define parser_h_

#include <stdio.h>
#include "../objects/object.h"

obj_t read_repl();
array_t read_file( FILE* file ); //returns an array of all the parsed obj's
obj_t read_string( char* string );

#endif

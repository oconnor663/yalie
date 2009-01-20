#ifndef parser_h_
#define parser_h_

#include <stdio.h>
#include "../objects/object.h"

typedef struct ParseStream * parse_t;
parse_t new_repl();
void free_repl();
obj_t read_repl( parse_t repl, bool* is_eof );

obj_t read_file( FILE* file );

obj_t read_string( char* string );

#endif

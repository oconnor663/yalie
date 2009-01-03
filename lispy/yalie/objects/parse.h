#ifndef parse_h_
#define parse_h_

#include <stdio.h>
#include <stdbool.h>
#include "object.h"

extern bool yyeof;

char* getline( bool new_expr );

obj_t parse_string( char* str );
obj_t parse_file( FILE* file );

obj_t parse_repl();

#endif

#ifndef io_h_
#define io_h_

#include <stdio.h>
#include <stdbool.h>
#include "object.h"

obj_t StringClass();

obj_t new_string( char* text );

char* string_repr( obj_t string );

bool is_string( obj_t obj );

/*
obj_t StreamClass();

obj_t new_stream_s( char* filename, char* mode );
obj_t new_stream_f( FILE* file );

void stream_write( obj_t stream, char* text );
void stream_write_string( obj_t stream, obj_t string );
void stream_flush( obj_t stream );

char* stream_repr( obj_t stream );

bool is_stream( obj_t obj );
*/
#endif

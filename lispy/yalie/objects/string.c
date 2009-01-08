#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../guts/array.h"
#include "string.h"
#include "exception_obj.h"

obj_t GlobalStringClass = NULL;

static void init_string_class()
{
  GlobalStringClass = new_class_obj();
}

obj_t StringClass()
{
  if (GlobalStringClass==NULL)
    init_string_class();

  return GlobalStringClass;
}

typedef struct String {
  char* text;
  size_t len;
} * string_t;

obj_t new_string( char* text )
{
  obj_t ret = new_obj( StringClass() );
  string_t ret_guts = malloc( sizeof(struct String) );
  ret_guts->text = strdup(text);
  ret_guts->len = strlen(text);
  obj_set_guts( ret, ret_guts );
  return ret;
}

char* string_repr( obj_t string )
{
  char* ret;
  size_t ret_size;
  FILE* ret_stream = (FILE*)open_memstream( &ret, &ret_size ); //WHY?
  fprintf( ret_stream, "\"" );
  int i;
  for (i=0; i < ((string_t)obj_guts(string))->len; i++) {
    char c = ((string_t)obj_guts(string))->text[i];
    if (c=='\n')
      fprintf( ret_stream, "\n" );
    else if (c=='\t')
      fprintf( ret_stream, "\t" );
    else if (c=='\\')
      fprintf( ret_stream, "\\\\" );
    else
      fprintf( ret_stream, "%c", c );
  }
  fprintf( ret_stream, "\"" );
  fclose(ret_stream);
  return ret;
}

bool is_string( obj_t obj )
{
  return is_instance( obj, StringClass() );
}


obj_t GlobalStreamClass = NULL;

static void init_stream_class()
{
  GlobalStreamClass = new_class_obj();
}

obj_t StreamClass()
{
  if (GlobalStreamClass==NULL)
    init_stream_class();

  return GlobalStreamClass;
}

typedef struct Stream {
  char* text;
  size_t len;
} * stream_t;

obj_t new_stream_s( char* filename, char* mode )
{
  obj_t ret = new_obj( StreamClass() );
  FILE* ret_guts = fopen( filename, mode );
  if (ret_guts==NULL)
    return new_excep_obj( "File opening error" );
    // later implement frees
  obj_set_guts( ret, ret_guts );
  return ret;
}

obj_t new_stream_f( FILE* file )
{
  obj_t ret = new_obj( StreamClass() );
  obj_set_guts( ret, file );
  return ret;
}

void stream_write( obj_t stream, char* text )
{
  fprintf( obj_guts(stream), "%s", text );
}

void stream_write_string( obj_t stream, obj_t string )
{
  fprintf( obj_guts(stream), "%s", 
	   ((string_t)obj_guts(string))->text );
}

void stream_flush( obj_t stream )
{
  fflush( obj_guts(stream) );
}

char* stream_repr( obj_t stream )
{
  char* ret;
  asprintf( &ret, "<stream %p>", stream );
  return ret;
}

bool is_stream( obj_t obj )
{
  return is_instance( obj, StreamClass() );
}

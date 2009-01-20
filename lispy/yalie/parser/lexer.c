#define _GNU_SOURCE

#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <error.h>

#include "../objects/builtins.h"
#include "../repr.h"
#include "lexer.h"

struct LexStream {
  char* buffer; //NB: NOT NULL TERMINATED! (also backwards)
  size_t len;   //number of chars
  size_t size;  //space allocated
  FILE* stream; //NB: NOT OWNED (i.e. not closed)
};
  
lex_t new_lex( FILE* stream )
{
  lex_t ret = malloc( sizeof(struct LexStream) );
  ret->size = 4;
  ret->buffer = malloc( ret->size * sizeof(char) );
  ret->len = 0;
  ret->stream = stream;
  return ret;
}

void free_lex( lex_t lex )
{
  free(lex->buffer);
  free(lex);
}

int readc( lex_t lex )
{
  assert( lex!=NULL );

  int ret;
  if (lex->len==0)
    ret = getc(lex->stream);
  else {
    lex->len--;
    ret = lex->buffer[lex->len];
  }
  return ret;
}

void unreadc( int c, lex_t lex )
{
  assert( -1<=c && c<256 );

  if (lex->len==lex->size) {
    lex->size *= 2;
    lex->buffer = realloc( lex->buffer, lex->size );
  }

  lex->buffer[lex->len] = c;
  lex->len++;
}

token_t new_obj_token( obj_t obj )
// At most one of obj or punc should be nonzero/nonnull...
// Does not add or own any actual objects.
{
  assert( obj!=NULL );

  token_t ret = malloc( sizeof(struct Token) );
  ret->type = OBJ_TOK;
  ret->val.obj = obj;
  return ret;
}

token_t new_error_token( char* error )
// At most one of obj or punc should be nonzero/nonnull...
// Does not add or own any actual objects.
{
  assert( error!=NULL );

  token_t ret = malloc( sizeof(struct Token) );
  ret->type = ERROR_TOK;
  ret->val.obj = new_excep_obj(error);
  return ret;
}

token_t new_punc_token( int punc )
// At most one of obj or punc should be nonzero/nonnull...
// Does not add or own any actual objects.
{
  token_t ret = malloc( sizeof(struct Token) );
  ret->type = PUNC_TOK;
  ret->val.punc = punc;
  return ret;
}

token_t new_eof_token()
// At most one of obj or punc should be nonzero/nonnull...
// Does not add or own any actual objects.
{
  token_t ret = malloc( sizeof(struct Token) );
  ret->type = EOF_TOK;
  return ret;
}

void free_token( token_t tok )
{
  // does NOT free or in any way modify any associated obj_t
  free(tok);
}

/*
 * The ordering of the lex should be as follows:
 * 1) whitespace is cleared
 * 2) string literals are recognized
 * 3) number literals
 * 4) symbol literals or punctuation or error
 *
 * These functions will assume that tokens higher in the list have
 * already been tested for starting from the given point.
 */

bool is_white( int c )
{
  return c==' ' || c=='\t' || c=='\n';
}

bool is_punctuation( int c )
{
  return ( c=='.' || c==':' || c=='`' || c==',' || c==';' ||
	   c=='(' || c==')' || c=='{' || c=='}' );
}

bool is_separator( int c )
{
  return is_punctuation(c) || is_white(c) || c==EOF;
}

bool is_digit( int c )
{
  return '0'<=c && c<='9';
}

token_t lex_sym_and_punc( lex_t f )
{
  int c = readc(f);
  if (is_punctuation(c)) {
    return new_punc_token( c );
  }
  else {
    char* match;
    size_t match_size;
    FILE* match_stream = open_memstream(&match, &match_size);
    putc(c,match_stream);
    while (true) {
      c = readc(f);
      if (is_separator(c)) {
	unreadc(c,f);
	fclose(match_stream);
	obj_t ret = new_sym_obj(match);
	free(match);
	return new_obj_token( ret );
      }
      else {
	putc(c,match_stream);
      }
    }
  }
}

token_t lex_number( lex_t f )
// POLICY
// Starting with a number flags the token as a number.
// If it turns out to not lex properly (i.e. "123abc")
// then an error will be signaled. In particular, the
// offending token is NOT interpreted as a symbol.
{
  int c = readc(f);
  if (is_digit(c)) {
    char* match;
    size_t match_size;
    FILE* match_stream = open_memstream(&match,&match_size);
    putc( c, match_stream );
    while (true) {
      c = readc(f);
      if (is_digit(c))
	putc(c,match_stream);
      else if (is_separator(c)) {
	unreadc(c,f);
	fclose(match_stream);
	obj_t ret = new_int_s(match);
	free(match);
	return new_obj_token( ret );
      }
      else {
	// Not an integer
	unreadc(c,f);
	fclose(match_stream);
	int i;
	for (i=strlen(match)-1; i>-1; i--)
	  unreadc(match[i],f);
	free(match);
	return new_error_token( "Could not lex number" );
      }
    }
  }
  else {
    unreadc( c, f );
    return lex_sym_and_punc( f );
  }
}

char* prepare_string( char* str )
// Interprets the difference between raw and not raw strings
{
  size_t len = strlen(str);
  bool raw = (str[0]=='\'');

  char* new_str;
  size_t new_size;
  FILE* new_stream = open_memstream(&new_str,&new_size);
  
  size_t i = 1;
  while ( i < len-1 ) {  //avoids the terminating quotation mark
    if (str[i]=='\\' && !raw) { 
      // we know there's more before the closing quotation
      if (str[i+1]=='n') {
	putc( '\n', new_stream );
	i++;
      }
      else if (str[i+1]=='t') {
	putc( '\t', new_stream );
	i++;
      }
      else if (str[i+1]=='\\') {
	putc( '\\', new_stream );
	i++;
      }
      else {
	putc( '\\', new_stream );
      }
    }
    else
      putc( str[i], new_stream );
    i++;
  }
  
  fclose(new_stream);
  return new_str;
}

token_t lex_string( lex_t f )
{
  int c = readc(f);
  int delim;
  if (c!='"' && c!='\'') {
    // Not a string
    unreadc(c,f);
    return lex_number( f );
  }
  else {
    delim = c;
    char* match;
    size_t match_size;
    FILE* match_stream = open_memstream(&match,&match_size);
    putc( c, match_stream );

    bool escaped = false;
    while (true) {
      c = readc(f);
      if (c=='\n' || c==EOF) {
	fclose(match_stream);
	free(match);
	return new_error_token( "Unterminated string." );
      }
      else if (c=='\\') {
	escaped = !escaped;
	putc(c,match_stream);
      }
      else if (c==delim) {
	putc(c,match_stream);
	if (!escaped) {
	  fclose(match_stream);
	  char* prepared_match = prepare_string(match);
	  obj_t ret = new_string( prepared_match );
	  free(match);
	  free(prepared_match);
	  return new_obj_token( ret );
	}
      }
      else {
	escaped = false;
	putc( c, match_stream );
      }
    }
  }
}

token_t remove_whitespace( lex_t f )
{
  int c;
  while ( (c=readc(f))==' ' || c=='\t' || c=='\n' );
  //burn all the whitespace

  if (c==EOF) {
    return new_eof_token();
  }
  else {
    unreadc(c,f);
    return lex_string(f);
  }
}

token_t lex_token( lex_t f )
{
  return remove_whitespace( f );
}

/*
main()
{
  lex_t l = new_lex(stdin);
  int c = readc(l);
  printf( "first char: %c\n", c );
  unreadc(c,l);

  int d = readc(l), e=readc(l), f=readc(l), g=readc(l), h=readc(l), i=readc(l);
  printf( "sixth char: %c\n", i );
  unreadc(i,l);
  unreadc(h,l);
  unreadc(g,l);
  unreadc(f,l);
  unreadc(e,l);
  unreadc(d,l);

  printf( "whole thing: " );
  while ((c=readc(l))!=EOF)
    printf( "%c", c );
}
*/

 /*
array_t pointers; //keeping track of obj's

main()
{
  pointers = new_array(0,0);

  token_t tok;
  lex_t f = new_lex( stdin );
  while (true) {
    tok = lex_token(f);
    if (tok->type==ERROR_TOK) {
      printf( "Error encountered\n" );
      free_lex(f);
      free_token(tok);
      break;
    }
    else if (tok->type==EOF_TOK) {
      free_lex(f);
      free_token(tok);
      break;
    }
    else {
      if (tok->type==OBJ_TOK) {
	printf( "val: " );
	repr( tok->val.obj );
	putchar('\n');
	array_push_back(pointers, tok->val.obj);
      }
      free_token(tok);
      // FREE THOSE VALUES?
    }
  }
}
*/

/*
main()
{
  char* orig = "\"f\\too\\nb\\kar\"";
  printf( "%s\n", orig );
  char* str = prepare_string( orig );
  printf( "%s\n", str );
  free(str);
  char* orig2 = "'f\\too\\nb\\kar'";
  printf( "%s\n", orig2 );
  str = prepare_string( orig2 );
  printf( "%s\n", str );
  free(str);
}
*/

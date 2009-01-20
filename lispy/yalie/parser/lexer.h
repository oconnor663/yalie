#ifndef lexer_h_
#define lexer_h_

#include <stdio.h>
#include "../objects/object.h"
#include "../guts/exception.h"

typedef struct LexStream * lex_t;

lex_t new_lex( FILE* stream );
void free_lex( lex_t lex );


enum token_type {
  OBJ_TOK,
  PUNC_TOK,
  ERROR_TOK,
  EOF_TOK
};

typedef struct Token {
  enum token_type type;
  union TokenVal {
    obj_t obj;
    int punc;
  } val;
} * token_t;

token_t lex_token( lex_t f );
token_t new_error_token( char* error );
void free_token( token_t tok ); // Does NOT free associated objects,
                                // but does free associated exception.

#endif

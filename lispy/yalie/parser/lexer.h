#ifndef lexer_h_
#define lexer_h_

#include <stdio.h>
#include "../objects/object.h"

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
    obj_t obj; // only non-NULL for OBJ_TOK
    int punc;  // only nonzero for PUNC_TOK
  } val;
} * token_t;

token_t lex_token( lex_t f );
void free_token( token_t tok ); // Does NOT free associated objects

#endif

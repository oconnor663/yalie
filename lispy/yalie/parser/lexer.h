#ifndef lexer_h_
#define lexer_h_

#include <stdio.h>
#include "../objects/object.h"

typedef struct Lex * lex_t;

lex_t new_lex( FILE* stream );
void free_lex( lex_t lex );


enum token_type {
  OBJ_TOK,
  PUNC_TOK,
  ERROR_TOK, //indicates an exception object
  EOF_TOK
};

struct Token {
  enum token_type type;
  obj_t val; // only non-NULL for OBJ_TOK
  int punc;  // only nonzero for PUNC_TOK
};

struct Token lex_token( lex_t f );

#endif

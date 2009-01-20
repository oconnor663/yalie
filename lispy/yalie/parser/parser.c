#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <readline/readline.h>
#include "../objects/builtins.h"
#include "../guts/array.h"
#include "lexer.h"
#include <error.h>
#include "../repr.h"
#include <assert.h>

char* get_repl_line( char* prompt )
{
  char* line = readline( prompt );
  
  if (line!=NULL && line[0]!='\0')
    add_history(line);

  //including the \n avoids a SEGFAULT when reading later
  if (line!=NULL) {
    int len = strlen(line);
    line = realloc( line, (len+2)*sizeof(char) );
    line[len] = '\n';
    line[len+1] = '\0';
  }

  return line;
}

typedef struct ParseStream {
  bool is_repl, repl_eof;
  lex_t input;
  array_t buffer; 
  FILE* owned_stream; // for freeing
  char* owned_string; // for freeing
} * parse_t;

void parse_get_repl_line( parse_t parse, char* prompt )
// returns false on failure (that is, EOF from stdin)
{
  assert( array_len(parse->buffer)==0 );

  char* new_line = get_repl_line(prompt);

  if (new_line==NULL) // REPL EOF
    parse->repl_eof = true;

  else {
    if (parse->input!=NULL)
      free_lex( parse->input );
    if (parse->owned_stream!=NULL)
      fclose(parse->owned_stream);
    if (parse->owned_string!=NULL)
      free(parse->owned_string);

    parse->owned_string = new_line;
    parse->owned_stream = (FILE*)fmemopen( parse->owned_string,
					   strlen(parse->owned_string),
					   "r" );
    parse->input = new_lex(parse->owned_stream);
  }
}

parse_t new_parse( bool is_repl, lex_t input )
// buffer is ignored when (is_repl)
{
  parse_t ret = malloc( sizeof(struct ParseStream) );
  ret->buffer = new_array(0,0);
  ret->is_repl = is_repl;
  ret->repl_eof = false;
  ret->input = (is_repl?NULL:input);
  ret->owned_string = NULL;
  ret->owned_stream = NULL;

  if (is_repl)
    parse_get_repl_line(ret,">>> ");
  
  return ret;
}

parse_t new_repl()
{
  return new_parse( true, NULL );
}

void free_parse( parse_t parse )
{
  size_t i;
  for (i=0; i<array_len(parse->buffer); i++)
    free_token( array_ref(parse->buffer, i) );
    // Release associated objects???
  free_array(parse->buffer);
  if (parse->input!=NULL)
    free_lex(parse->input);
  if (parse->owned_stream!=NULL)
    fclose(parse->owned_stream);
  if (parse->owned_string!=NULL)
    free(parse->owned_string);
}

void free_repl( parse_t repl )
{
  free_parse(repl);
}

token_t parse_get_token( parse_t parse )
{
  if (array_len(parse->buffer)>0)
    return array_pop_back(parse->buffer);

  if (!(parse->is_repl)) {
    return lex_token(parse->input); //could be NULL
  }
  else {
    token_t ret = lex_token( parse->input );
    if (ret->type==EOF_TOK) { 
      parse_get_repl_line( parse, "... " );
      if (parse->repl_eof) {
	return new_error_token( "Encountered EOF in S-expression" );
      }
      return parse_get_token( parse );
    }
    else
      return ret;
  }
}

token_t parse_gentle_get_token( parse_t parse )
{
  if (array_len(parse->buffer)>0)
    return array_pop_back(parse->buffer);

  // Doesn't reread a line on the REPL if there is no token
  return lex_token( parse->input );
}

void parse_unget_token( parse_t parse, token_t tok )
{
  array_push_back(parse->buffer, (void*)tok);
}

/*
 * Here are some functions to help in translating punctuation.
 */

obj_t punc2symbol( int punc )
{
  switch (punc) {
  case '`':
    return new_sym_obj("backquote-prefix");
  case ';':
    return new_sym_obj("semicolon-prefix");
  case ',':
    return new_sym_obj("comma-prefix");
  case ':':
    return new_sym_obj("colon-infix");
  case '.':
    return new_sym_obj("period-infix");
  }
}

bool is_prefix( int punc )
{
  return (punc=='`' || punc==',' || punc==';');
}

bool is_infix( int punc )
{
  return (punc==':' || punc=='.');
}

/*
 * Here begin the functions that will built objects from the
 * tokens. The prefix helper function is there (as opposed to being
 * builtin to read_expr) for read_sexpr, because read_expr would eat
 * up infix punctuation at the beginning of S-expressions that
 * read_sexpr wants to handle itself.
 */

obj_t read_prefixed( parse_t parse );
obj_t read_infixes( parse_t parse, obj_t prefix, bool* modified );
obj_t read_sexpr( parse_t parse, bool is_start );
obj_t read_expr( parse_t parse );

obj_t read_prefixed( parse_t parse )
// This is the only function that should have to deal with ERROR_TOK's
// from the lexer. Any other function that gets tokens should be
// ungetting them if it doesn't use them.
{
  token_t tok = parse_gentle_get_token(parse);

  if (tok->type==EOF_TOK)
    return NULL;
  else if (tok->type==OBJ_TOK || tok->type==ERROR_TOK)
    return tok->val.obj;
  else if (tok->type==PUNC_TOK) {
    if (tok->val.punc=='(')
      return read_sexpr(parse,true);
    if (is_prefix(tok->val.punc)) {
      obj_t rest = read_prefixed(parse);
      if (rest==NULL)
	error(1,0,"Parser encountered EOF after prefix\n");
      return new_cons_obj( punc2symbol(tok->val.punc),
			   new_cons_obj(rest, new_nil_obj()) );
    }
  }
  error(1,0,"Parse (prefix) shouldn't have gotten this far.\n");
}

obj_t read_infixes( parse_t parse, obj_t prefix, bool* modified )
// Returns true if any infixes were found.
{
  if (modified!=NULL) *modified = false;
  if (prefix==NULL || is_excep(prefix))
    return prefix;
  obj_t ret = prefix;

  while (true) {
    token_t tok = parse_gentle_get_token(parse);
    if (tok->type==EOF_TOK)
      break;
    else if (tok->type==PUNC_TOK && is_infix(tok->val.punc)) {
      obj_t second = read_prefixed(parse);
      if (second==NULL)	
	return new_excep_obj( "EOF when expecting infix argument" );
      if (is_excep(second))
	return second;
      if (modified!=NULL) *modified = true;
      ret = new_cons_obj( punc2symbol(tok->val.punc),
			  new_cons_obj( ret,
					new_cons_obj( second, new_nil_obj() )));
    }
    else {
      parse_unget_token(parse,tok);
      break;
    }
  }
  return ret;
}

obj_t read_sexpr( parse_t parse, bool is_start )
{
  token_t tok = parse_get_token(parse);
  if (tok->type==ERROR_TOK)
    return tok->val.obj;

  if (tok->type==PUNC_TOK && tok->val.punc==')')
    return new_nil_obj();
  else
    parse_unget_token(parse,tok);

  bool infixes_found;
  obj_t obj = read_prefixed(parse);
  obj = read_infixes(parse,obj,&infixes_found);
  if (obj==NULL)
    return new_excep_obj( "EOF in S-expression" );
  if (is_excep(obj))
    return obj;

  // Here is the part where neat S-expression punctuation
  // syntax happens
  if (is_start && infixes_found) {
    obj_t tmp = cons_obj_cdr( cons_obj_cdr( obj ) );
    if (!is_nil(cons_obj_cdr(tmp)))
      error(1,0,"UHOH! weird error in S-expressions parser");
    obj_del_ref( cons_obj_cdr(tmp) );
    obj_t rest = read_sexpr(parse,false);
    if (is_excep(rest))
      return rest;  //FREE THINGS?
    cons_obj_set_cdr( tmp, rest );
    return obj;
  }
  else {
    obj_t rest = read_sexpr(parse,false);
    if (is_excep(rest))
      return rest;
    else
      return new_cons_obj( obj, rest );
  }  
}
  
obj_t read_expr( parse_t parse )
{
  obj_t obj = read_infixes(parse,read_prefixed(parse),NULL);
  return obj;
}

obj_t read_repl( parse_t parse, bool* is_eof )
{
  if (parse->repl_eof) {
    if (is_eof!=NULL) *is_eof = true;
    return NULL;
  }
  
  if (is_eof!=NULL) *is_eof = false;
  obj_t o = read_expr(parse);

  /*
  if (!is_excep(o)) {
    token_t test = parse_gentle_get_token(p);
    if (test->type!=EOF_TOK)
      error( 1,0,"Parse error: at most one expression per line please." );
  }
  */
  return o;
}

main()
{
  parse_t repl = new_repl();


  while (true) {
    bool is_eof;

    //THIS IS LOOPING FOREVER BECAUSE IM AN IDIOT
    //NEED TO KEEP TRACK OF THE WHOLE NEW EXPRESSION THING
    //AND READ_REPL NEEDS TO START HANGING...
    obj_t o = read_repl( repl, &is_eof );
    if (o!=NULL) {
      repr(o);
      printf( "\n" );
    }
    if (is_eof) {
      printf( "\n" );
      break;
    }
  }
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "types.h"

val_t new_val( void* obj, enum type type )
{
  val_t ret = malloc(sizeof(struct Val));
  ret->obj = obj;
  ret->type = type;
  ret->ref_count = 1;
  return ret;
}

void add_ref( val_t val )
{
  val->ref_count++;
}

void del_ref( val_t val )
{
  val->ref_count--;
  if (val->ref_count==0)
    switch (val->type) {

    case Nil:
      free(val);
      break;

    case Cons:
      del_ref(car(val->obj));
      del_ref(cdr(val->obj));
      free_cons(val->obj);
      free(val);
      break;

    case Symbol:
      free_sym(val->obj);
      free(val);
      break;

    case Int:
      free_int(val->obj);
      free(val);
      break;

    default:
      fprintf( stderr, "del_ref() encountered unknown type.\n" );
      free(val);
      break;
    }
}

/*
 * Below are all functions for printing.
 */

static char* strapp( char* a, char* b )
{
  char* ret = malloc( (strlen(a)+strlen(b)+1)*sizeof(char) );
  char* tmp = ret;
  strcpy(ret,a);
  strcat(ret,b);
  free(a);
  free(b);
  return ret;
}

static char* repr_nil()
{
  return strdup("()");
}

static char* repr_cons( val_t val )
{
  char* ret = strdup("(");
  ret = strapp( ret, repr(car(val->obj)) );
  val = cdr(val->obj);
  while (1) {
    if (val->type==Nil) {
      ret = strapp(ret,strdup(")"));
      break;
    }
    else if ( ((val_t)cdr(val->obj))->type!=Cons &&
	      ((val_t)cdr(val->obj))->type!=Nil ) {
      ret = strapp(ret, strdup(" "));
      ret = strapp(ret,repr(car(val->obj)));
      ret = strapp(ret,strdup(" . "));
      ret = strapp(ret,repr(cdr(val->obj)));
      ret = strapp(ret,strdup(")"));
      break;
    }
    else {
      ret = strapp(ret,strdup(" "));
      ret = strapp(ret,repr(car(val->obj)));
      val = cdr(val->obj);
    }
  }
  return ret;
}

char* repr( val_t val )
{
  switch (val->type) {
  case Nil:
    return repr_nil();
  case Symbol:
    return repr_sym(val->obj); //core.h
  case Cons:
    return repr_cons(val); //note the arg type
  case Int:
    return repr_int(val->obj); //core.h
  default:
    fprintf( stderr, "Error encountered in repr()\n" );
    return strdup("???");
  }
}

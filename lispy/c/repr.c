#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "repr.h"

char* strapp( char* a, char* b )
{
  char* ret = malloc( (strlen(a)+strlen(b)+1)*sizeof(char) );
  char* tmp = ret;
  strcpy(ret,a);
  strcat(ret,b);
  free(a);
  free(b);
  return ret;
}

char* repr_nil()
{
  return strdup("()");
}

char* repr_cons( val_t val )
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

/*
main()
{
  sym_t sym = new_sym("SyM");
  val_t s = new_val( sym, Symbol );
  val_t nil = new_val( NULL, Nil );
  cons_t c1 = new_cons(s,nil);
  val_t C1 = new_val(c1,Cons);
  cons_t c2 = new_cons(s, C1);
  val_t val = new_val( c2, Cons );
  char* ret = repr(val);
  printf( "%s\n", ret );
  free_sym(sym);
  free(s);
  free(nil);
  free_cons(c1);
  free(C1);
  free_cons(c2);
  free(val);
  free(ret);
}
*/

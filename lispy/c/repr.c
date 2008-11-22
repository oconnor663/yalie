#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "core.h"


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

char* repr( val_t val )
{
  if (val->type==Symbol)
    return strdup( (char*)val->obj );
  else if (val->type==Nil)
    return strdup("()");
  else if (val->type==Cons) {
    char* ret = strdup("(");
    ret = strapp(ret,repr(car(val->obj)));
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
  else
    return "?????";
}

main()
{
  val_t sym = new_val( "SYM", Symbol );
  val_t nil = new_val( NULL, Nil );
  cons_t c1 = new_cons(sym,nil);
  val_t C1 = new_val(c1,Cons);
  cons_t c2 = new_cons(sym, C1);
  val_t val = new_val( c2, Cons );
  char* ret = repr(val);
  printf( "%s\n", ret );
  free(sym);
  free(nil);
  free(c1);
  free(C1);
  free(c2);
  free(val);
  free(ret);
}

#include <stdio.h>
#include <stdbool.h>
#include <assert.h>
#include "objects/builtins.h"
#include "guts/guts.h"
#include "parser/parser.h"

#include "repr.h"

//obj_t test_fn( int argc, obj_t* argv )
//{
//  printf( "THIS IS ONLY A TEST\n" );
//  return new_nil_obj();
//}

void cleanup()
{
  printf( "Starting cleanup\n" );

  printf( "IntClass freeing---------------\n" );
  obj_del_ref(IntClass());
  printf( "SymClass freeing---------------\n" );
  obj_del_ref(SymClass());
  printf( "ConsClass freeing---------------\n" );
  obj_del_ref(ConsClass());
  printf( "NilClass freeing---------------\n" );
  obj_del_ref(NilClass());
  printf( "ExcepClass freeing---------------\n" );
  obj_del_ref(ExcepClass());
  printf( "FuncClass freeing---------------\n" );
  obj_del_ref(FuncClass());
  printf( "MethodClass freeing---------------\n" );
  obj_del_ref(MethodClass());
  printf( "StringClass freeing---------------\n" );
  obj_del_ref(StringClass());

  printf( "Clearing base classes----------\n" );
  cleanup_base_classes();

  free_sym_table();
}

int main( int argv, char** argc )
{
  printf( "Yalie v0.4\nPress Ctrl-D to exit.\n" );

  scope_t global_scope = new_scope( NULL );
  
  //scope_add( global_scope, get_sym("tfn"), new_func( test_fn, "()") );

  parse_t repl = new_repl();

  bool is_eof;
  while (true) {
    obj_t o = read_repl( repl, &is_eof );
    if (o!=NULL)
      obj_add_ref(o);
    
    if (is_eof) {
      assert(o==NULL);
      printf("\b\b\b\b");
      break;
    }

    if (o!=NULL) {
      if (is_excep(o))
	repr(o);
      else {
	obj_t val = eval(global_scope,o);
	obj_add_ref(val);
	repr( val );
	obj_del_ref(val);
      }
      printf( "\n" );
      obj_del_ref(o);
    }
  }

  free_scope(global_scope);
  free_repl(repl);
  cleanup();
}

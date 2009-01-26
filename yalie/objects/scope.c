#include <stdlib.h>
#include "scope.h"
#include "../guts/table.h"
#include "../guts/symbol.h"

struct Scope {
  table_t table;
  scope_t parent;
};

scope_t new_scope( scope_t parent )
{
  scope_t ret = malloc( sizeof(struct Scope) );
  ret->table = new_table( pointer_hash, pointer_eq );
  ret->parent = parent;
  return ret;
}

void free_scope( scope_t scope )
{
  array_t vals = table_vals( scope->table );
  int i;
  for (i=0; i<array_len(vals); i++)
    obj_del_ref( array_ref( vals, i ) );
  free_array(vals);
  free_table(scope->table);
  free(scope);
}


extern char* yytext;
void scope_add( scope_t scope, sym_t key, obj_t val )
{
  obj_t tmp;
  bool test = table_set( scope->table, key, val, (void*)&tmp );
  obj_add_ref(val);
  if (test)
    obj_del_ref(tmp);
}

bool scope_set( scope_t scope, sym_t key, obj_t val )
//returns false on failure
{
  obj_t tmp;
  // finds the highest scope with an existing binding
  while ( ! table_ref(scope->table,key,(void*)&tmp) ) {
    if (scope->parent==NULL)
      return false;
    else
      scope = scope->parent;
  }

  table_set( scope->table, key, val, (void*)&tmp );
  obj_add_ref(val);
  obj_del_ref(tmp);
  return true;
}

obj_t scope_ref( scope_t scope, sym_t key )
// Returns NULL on a failed lookup
{
  obj_t ret;
  bool test = table_ref( scope->table, key, (void*)&ret );
  if (test)
    return ret;
  else if (scope->parent!=NULL)
    return scope_ref( scope->parent, key );
  else
    return NULL;
}

void scope_del( scope_t scope, sym_t key )
{
  obj_t tmp;
  bool test = table_del( scope->table, key, (void*)&tmp );
  if (test)
    obj_del_ref(tmp);
}

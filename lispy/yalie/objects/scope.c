#include <stdlib.h>
#include <stdbool.h>
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
  ret->table = new_table( table_ptr_hash, table_ptr_eq );
  ret->parent = parent;
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

void scope_add( scope_t scope, sym_t key, obj_t val )
{
  obj_t tmp;
  bool test = table_add( scope->table, key, val, (void*)&tmp );
  obj_add_ref(val);
  if (test)
    obj_del_ref(tmp);
}

obj_t scope_ref( scope_t scope, sym_t key )
// Returns NULL on a failed lookup
{
  obj_t ret;
  bool test = table_ret( scope->table, key, &ret );
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

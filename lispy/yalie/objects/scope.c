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

void scope_add( scope_t scope, sym_t name, obj_t obj )
{
  obj_t tmp;
  bool test = table_add( scope->table, name, obj, &tmp );
  if (test)
    obj_del_ref(tmp);
}

obj_t scope_ref( scope_t scope, sym_t name )
// Returns NULL on a failed lookup
{
  obj_t ret;
  bool test = table_ret( scope->table, name, &ret );
  if (test)
    return ret;
  else if (scope->parent!=NULL)
    return scope_ref( scope->parent, name );
  else
    return NULL;
}

void scope_del( scope_t scope, sym_t name )
{
  obj_t tmp;
  bool test = table_del( scope->table, name, &tmp );
  if (test)
    obj_del_ref(tmp);
}

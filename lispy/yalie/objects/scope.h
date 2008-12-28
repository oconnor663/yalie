#ifndef scope_h_
#define scope_h_

/*
 * A scope is essentially a wrapper around the table.
 * It assumes that all of its keys will be symbols and that
 * all of its values will be objects. It holds and releases
 * references to those objects.
 */

typedef struct Scope * scope_t;

scope_t new_scope();
scope_t free_scope();

void scope_add( scope_t scope, sym_t name, obj_t obj );
obj_t scope_ref( scope_t scope, sym_t name ); //NULL on fail
void scope_del( scope_t scope, sym_t name );

#endif

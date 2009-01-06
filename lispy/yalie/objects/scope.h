#ifndef scope_h_
#define scope_h_

/*
 * A scope is essentially a wrapper around the table.
 * It assumes that all of its keys will be symbols and that
 * all of its values will be objects. It holds and releases
 * references to those objects.
 */

#include <stdbool.h>
#include "../guts/symbol.h"
#include "object.h"

typedef struct Scope * scope_t;

scope_t new_scope( scope_t parent );
void free_scope( scope_t scope );

//Adds/overwrites a binding on the bottom level
void scope_add( scope_t scope, sym_t name, obj_t val );

//Modifies the bottommost existing binding. false on failure
bool scope_set( scope_t scope, sym_t name, obj_t val );

//References the bottommost existing binding
//Returns NULL on failure
obj_t scope_ref( scope_t scope, sym_t name );

//Removes a bottom level binding only
void scope_del( scope_t scope, sym_t name );

#endif

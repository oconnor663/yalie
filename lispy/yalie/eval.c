#include "objects/object.h"
#include "objects/scope.h"
#include "objects/cons_class.h"
#include "objects/symbol_class.h"

obj_t eval( obj_t code, scope_t scope )
{
  // Self-evaluating objects.
  if ( ! (is_cons_p(obj_t) || is_symbol_p(obj_t)) )
    return code;

  else if ( is_symbol_p(obj_t) ) {
    obj_t ret = scope_ref( scope, obj_guts(obj_t) );
    if 
  }
}

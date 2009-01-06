#ifndef eval_h_
#define eval_h_

#include "object.h"
#include "scope.h"

obj_t eval( scope_t scope, obj_t code );

#endif

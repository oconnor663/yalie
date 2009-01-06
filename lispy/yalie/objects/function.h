#ifndef function_h_
#define function_h_

#include <stdbool.h>
#include "scope.h"
#include "object.h"

typedef obj_t (*func_ptr_t)(int argc, obj_t* argv);

obj_t FuncClass();
obj_t new_func( func_ptr_t body, char* args );
obj_t func_apply( obj_t func, int argc, obj_t* argv );
char* func_repr( obj_t func );
bool is_func( obj_t obj );

typedef obj_t (*form_ptr_t)(scope_t scope, int argc, obj_t* argv);

obj_t FormClass();
obj_t new_form( form_ptr_t body, char* args );
obj_t form_apply( obj_t form, scope_t scope, int argc, obj_t* argv );
char* form_repr( obj_t form );
bool is_form( obj_t obj );

typedef obj_t (*method_ptr_t)(obj_t obj, int argc, obj_t* argv);

obj_t MethodClass();
obj_t new_method( method_ptr_t body, char* args );
obj_t method_apply( obj_t method, obj_t obj, int argc, obj_t* argv );
char* method_repr( obj_t method );
bool is_method( obj_t obj );

#endif

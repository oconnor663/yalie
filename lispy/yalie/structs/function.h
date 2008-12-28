#ifndef function_h_
#define function_h_

typedef struct Function * func_t;

func_t new_func_c( obj_t (*f)(int argc, obj_t* argv) );
func_t new_func_l( obj_t 
void free_func( func_t );

// The only call necessary to invoke a C function. The return
// value here should be returned to userspace, unless it is an
// error. (Errors occurring during the evaluation of C functions
// should be reported back to the interpreter via this return
// value.)
obj_t func_apply_c( func_t f, int argc, obj_t* argv );

obj_t func_body_l( func_t f );

#endif

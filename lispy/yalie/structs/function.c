#include <stdlib.h>
#include <stdbool.h>
#include "function.h"

enum FnType {
  C,
  Lisp
};

struct Function {
  enum FnType type; // differentiates C and Lisp functions
  bool is_form; // causes lisp function to be expanded at compile time

  // This is used only by C functions, otherwise NULL
  obj_t (*c_fn)(int argc, obj_t* argv);

  // This is used only by Lisp functions, otherwise
  obj_t lisp_body;

  int min_args;
  int max_args; // -1 for unlimited
  obj_t args_list; // NULL for C functions  

  bool eval_args; // if false, arguments will not be implicitly eval'd
  
  env_t parent_scope; // for lexical scoping of non-forms
};

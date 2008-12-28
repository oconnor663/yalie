#include <stdlib.h>
#include "object.h"
#include "scope.h"

struct Object {
  class_t class;
  obj_t class_obj; //for garbage collection
  void* guts;
  scope_t members;
  scope_t methods;
  int ref_count;
};

struct Class {
  scope_t methods;
  obj_t parent; // allows the class to hold a reference
};              // to the parent with respect to garbage collection


/*
 * Declarations for OBJECTS
 * ----------------------------------------------------------
 */

obj_t new_obj( class_t class, obj_t class_obj )
{
  obj_t ret = malloc( sizeof(struct Object) );
  ret->class = class;
  ret->class_obj = class_obj;
  if (class_obj!=NULL)
    obj_add_ref( class_obj );
  ret->methods = new_scope( class->methods );
  ret->members = new_scope( NULL );
  ret->ref_count = 1;
  fprintf( stderr, "Would call `new' method on %p\n", ret );
  /*
   * Check for errors on the return.
   */
}

obj_t obj_add_ref( obj_t obj )
{
  obj->ref_count++;
}

obj_t obj_del_ref( obj_t obj )
{
  obj->ref_count--;
  if (obj_t->ref_count == 0) {
    fprintf( stderr, "Would call `del' method on %p\n", obj );
    if (obj->class_obj!=NULL)
      obj_del_ref( obj->class_obj );
    free_scope(ret->methods);
    free_scope(ret->members);
    free(obj);
  }
}

void* obj_guts( obj_t obj )
{
  return obj->guts;
}

/*
 * Declarations for CLASSES
 * -----------------------------------------------------------
 */

class_t new_class( obj_t parent )
{
  class_t ret = malloc(sizeof(struct Class));
  ret->parent = parent;
  if (parent!=NULL)
    obj_add_ref(parent);
  ret->methods = new_scope( parent->methods );
  return ret;
}

void free_class( class_t class )
{
  obj_del_ref(class->parent);
  free_scope(class->methods);
  free(class);
}

bool inherits_p( class_t child, class_t parent )
{
  while (parent!=NULL) {
    if (child==parent)
      return true;
    parent = parent->parent;
  }
  return false;
}

void class_add_method( class_t class, sym_t name, obj_t method )
{
  scope_add( class->methods, name, method );
}

obj_t class_ref_method( class_t class, sym_t name )
{
  //will return NULL on fail
  return scope_ref( class->methods, name );
}
void class_del_method( class_t class, sym_t name )
{
  scope_del( class->methods, name );
}

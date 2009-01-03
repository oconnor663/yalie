#include <stdlib.h>
#include <stdio.h>
#include "object.h"
#include "scope.h"
#include "cons_obj.h"
#include "symbol_obj.h"
#include "num.h"

struct Object {
  class_t class;
  obj_t class_obj; //for garbage collection
  void* guts;
  scope_t members;
  scope_t methods;
  unsigned long int ref_count;
};

struct Class {
  scope_t methods;
  class_t parent;
  obj_t parent_obj;
};


/*
 * Declarations for OBJECTS
 * ----------------------------------------------------------
 */

obj_t new_obj( obj_t class )
{
  obj_t ret = malloc( sizeof(struct Object) );
  ret->class_obj = class;
  ret->class = obj_guts(class);
  obj_add_ref( class );
  ret->methods = new_scope( ret->class->methods );
  ret->members = new_scope( NULL );
  ret->ref_count = 1;
  //fprintf( stderr, "Would call `new' method on %p\n", ret );
  /*
   * Check for errors on the return.
   */
  return ret;
}

void obj_add_ref( obj_t obj )
{
  obj->ref_count++;
}

void obj_del_ref( obj_t obj )
{
  obj->ref_count--;
  if (obj->ref_count == 0) {
    //fprintf( stderr, "Would call `del' method on %p\n", obj );
    if (obj->class_obj!=NULL)
      obj_del_ref( obj->class_obj );
    free_scope(obj->methods);
    free_scope(obj->members);
    free(obj);
  }
}

class_t obj_class( obj_t obj )
{
  return obj->class;
}

void* obj_guts( obj_t obj )
{
  return obj->guts;
}

void obj_set_guts( obj_t obj, void* guts )
{
  obj->guts = guts;
}

void obj_add_method( obj_t obj, sym_t name, obj_t method )
{
  scope_add( obj->methods, name, method );
}

obj_t obj_ref_method( obj_t obj, sym_t name )
{
  //will return NULL on fail
  return scope_ref( obj->methods, name );
}

void obj_del_method( obj_t obj, sym_t name )
{
  scope_del( obj->methods, name );
}

void obj_add_member( obj_t obj, sym_t name, obj_t member )
{
  scope_add( obj->members, name, member );
}

obj_t obj_ref_member( obj_t obj, sym_t name )
{
  //will return NULL on fail
  return scope_ref( obj->members, name );
}

void obj_del_member( obj_t obj, sym_t name )
{
  scope_del( obj->members, name );
}

/*
 * Declarations for CLASSES
 * -----------------------------------------------------------
 */

class_t new_class( obj_t parent )
{
  class_t ret = malloc(sizeof(struct Class));
    ret->parent_obj = parent;
  if (parent!=NULL) {
    obj_add_ref(parent);
    ret->parent = obj_guts(parent);
    ret->methods = new_scope( parent->methods );
  }
  else {
    ret->parent = NULL;
    ret->methods = new_scope( NULL );
  }
  return ret;
}

void free_class( class_t class )
{
  if (class->parent_obj!=NULL)
    obj_del_ref(class->parent_obj);
  free_scope(class->methods);
  free(class);
}

bool is_instance( obj_t obj, obj_t class )
{
  class_t child = obj_class( obj );
  class_t parent = obj_guts( class );

  while (child!=NULL) {
    if (child==parent)
      return true;
    child = child->parent;
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

/* 
 * Internal constructors
 * -------------------------------------------------
 */

obj_t ObjectClass;  //these two are externally visible
obj_t ClassClass;

void init_base_classes()
// This has to be done "by hand" because the inheritance structure
// of the Class class and the base Object class is all tangled up.
{
  class_t object_class = new_class(NULL);
  class_t class_class = malloc(sizeof(struct Class));

  class_class->methods = new_scope(object_class->methods);
  class_class->parent = object_class;
  class_class->parent_obj = ObjectClass;

  ObjectClass = malloc(sizeof(struct Object));
  ObjectClass->class_obj = ClassClass;
  ObjectClass->class = class_class;
  ObjectClass->guts = object_class; //NOTE
  ObjectClass->members = new_scope(NULL);
  ObjectClass->methods = new_scope(class_class->methods);
  ObjectClass->ref_count = 1;
  
  ClassClass = malloc(sizeof(struct Object));
  ClassClass->class_obj = ClassClass;
  ClassClass->class = class_class;
  ClassClass->guts = class_class; //NOTE
  ClassClass->members = new_scope(NULL);
  ClassClass->methods = new_scope(class_class->methods);
  ClassClass->ref_count = 1;

  init_cons_class();
  init_nil_class();
  init_sym_class();
  init_int_class();
}

obj_t new_class_obj()
// Understand: the class of the returned object will be the Class class,
// however that object will contain the class argument. Complicated :p
{
  class_t ret_class = new_class(ObjectClass);
  obj_t ret = new_obj( ClassClass );
  obj_set_guts( ret, ret_class );
  return ret;
}

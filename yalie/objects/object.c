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

static class_t new_class( obj_t parent )
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

static void free_class( class_t class )
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

void class_add_method( obj_t class, sym_t name, obj_t method )
{
  scope_add( ((class_t)obj_guts(class))->methods, name, method );
}

obj_t class_ref_method( obj_t class, sym_t name )
{
  //will return NULL on fail
  return scope_ref( ((class_t)obj_guts(class))->methods, name );
}

void class_del_method( obj_t class, sym_t name )
{
  scope_del( ((class_t)obj_guts(class))->methods, name );
}

/* 
 * Internal constructors
 * -------------------------------------------------
 */

obj_t GlobalObjectClass = NULL;
obj_t GlobalClassClass = NULL;

static void init_base_classes()
// This has to be done "by hand" because the inheritance structure
// of the Class class and the base Object class is all tangled up.
{
  class_t object_class = new_class(NULL);
  class_t class_class = malloc(sizeof(struct Class));

  class_class->methods = new_scope(object_class->methods);
  class_class->parent = object_class;
  class_class->parent_obj = GlobalObjectClass;

  GlobalObjectClass = malloc(sizeof(struct Object));
  GlobalObjectClass->class_obj = GlobalClassClass;
  GlobalObjectClass->class = class_class;
  GlobalObjectClass->guts = object_class; //NOTE
  GlobalObjectClass->members = new_scope(NULL);
  GlobalObjectClass->methods = new_scope(class_class->methods);
  GlobalObjectClass->ref_count = 1;
  
  GlobalClassClass = malloc(sizeof(struct Object));
  GlobalClassClass->class_obj = GlobalClassClass;
  GlobalClassClass->class = class_class;
  GlobalClassClass->guts = class_class; //NOTE
  GlobalClassClass->members = new_scope(NULL);
  GlobalClassClass->methods = new_scope(class_class->methods);
  GlobalClassClass->ref_count = 1;
}

obj_t ObjectClass()
{
  if (GlobalObjectClass==NULL)
    init_base_classes();
  return GlobalObjectClass;
}

obj_t ClassClass()
{
  if (GlobalClassClass==NULL)
    init_base_classes();
  return GlobalClassClass;
}

bool is_class( obj_t obj )
{
  return is_instance( obj, ClassClass() );
}

obj_t new_class_obj()
// Understand: the class of the returned object will be the Class class,
// however that object will contain the class argument. Complicated :p
{
  class_t ret_class = new_class( ObjectClass() );
  obj_t ret = new_obj( ClassClass() );
  obj_set_guts( ret, ret_class );
  return ret;
}

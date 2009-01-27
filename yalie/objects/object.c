#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "object.h"
#include "builtins.h"

struct Object {
  obj_t class;
  void* guts;
  scope_t members;
  scope_t methods;
  int ref_count;
};

struct Class {
  scope_t methods;
  class_t parent;
  obj_t parent_obj;
  //void (*init)(obj_t new_obj);
  void (*del)(obj_t dead_obj);
};


/*
 * Declarations for OBJECTS
 * ----------------------------------------------------------
 */

obj_t new_obj( obj_t class )
{
  obj_t ret = malloc( sizeof(struct Object) );
  ret->class = class;
  obj_add_ref( class );
  ret->methods = new_scope( ((class_t)obj_guts(class))->methods );
  ret->members = new_scope( NULL );
  ret->ref_count = 0;
  //if (((class_t)obj_guts(class))->init != NULL)
  //((class_t)obj_guts(class))->init(ret);
  return ret;
}

void obj_add_ref( obj_t obj )
{
  obj->ref_count++;
}

void obj_del_ref( obj_t obj )
{
  obj->ref_count--;
  printf( "REmaining refs: %i\n", obj->ref_count );
  if (obj->ref_count <= 0) {
    printf( "Killed\n" );
    if (((class_t)obj_guts(obj->class))->del != NULL)
      ((class_t)obj_guts(obj->class))->del(obj);
    if (obj->class!=NULL)
      obj_del_ref( obj->class );
    free_scope(obj->methods);
    free_scope(obj->members);
    free(obj);
  }
}

obj_t obj_class( obj_t obj )
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

static class_t new_class( obj_t parent,
			  //void (*init)(obj_t new_obj),
			  void (*del)(obj_t dead_obj) )
{
  assert (parent!=NULL);

  class_t ret = malloc(sizeof(struct Class));
  ret->parent_obj = parent;
  obj_add_ref(parent);
  ret->parent = obj_guts(parent);
  ret->methods = new_scope( parent->methods );
  //if (init==NULL)
  //ret->init = ((class_t)obj_guts(parent)->init);
  //else
  //ret->init = init;
  if (del==NULL)
    ret->del = ((class_t)obj_guts(parent))->del;
  else
    ret->del = del;
  return ret;
}

static void free_class( class_t class )
{
  if (class->parent_obj!=NULL)
    obj_del_ref(class->parent_obj);
  free_scope(class->methods);
  free(class);
}

static void del_class( obj_t class )
{
  free_class( (class_t)obj_guts(class) );
}

bool is_instance( obj_t obj, obj_t class )
{
  class_t child = obj_guts(obj->class);
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
  class_t object_class = malloc(sizeof(struct Class));
  class_t class_class = malloc(sizeof(struct Class));

  object_class->methods = new_scope(NULL);
  object_class->parent = NULL;
  object_class->parent_obj = NULL;
  //object_class->init = NULL;
  object_class->del = NULL;

  class_class->methods = new_scope(object_class->methods);
  class_class->parent = object_class;
  class_class->parent_obj = GlobalObjectClass;
  //class_class->init = NULL;
  class_class->del = del_class;

  GlobalObjectClass = malloc(sizeof(struct Object));
  GlobalObjectClass->class = GlobalClassClass;
  GlobalObjectClass->guts = object_class; //NOTE
  GlobalObjectClass->members = new_scope(NULL);
  GlobalObjectClass->methods = new_scope(class_class->methods);
  GlobalObjectClass->ref_count = 2; //so freeing ClassClass
                                    //won't kill it prematurely
  GlobalClassClass = malloc(sizeof(struct Object));
  GlobalClassClass->class = GlobalClassClass;
  GlobalClassClass->guts = class_class; //NOTE
  GlobalClassClass->members = new_scope(NULL);
  GlobalClassClass->methods = new_scope(class_class->methods);
  GlobalClassClass->ref_count = 1;
}

void cleanup_base_classes()
{
  free_class(obj_guts(GlobalClassClass));
  free_scope(GlobalClassClass->methods);
  free_scope(GlobalClassClass->members);
  free(GlobalClassClass);
  
  free_class(obj_guts(GlobalObjectClass));
  free_scope(GlobalObjectClass->methods);
  free_scope(GlobalObjectClass->members);
  free(GlobalObjectClass);  
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

obj_t new_class_obj( void (*del)(obj_t dead_obj) )
// Understand: the class of the returned object will be the Class class,
// however that object will contain the class argument. Complicated :p
{
  class_t ret_class = new_class( ObjectClass(), del );
  obj_t ret = new_obj( ClassClass() );
  obj_set_guts( ret, ret_class );
  return ret;
}

obj_t new_global_class_obj( void(*del)(obj_t dead_obj) )
{
  obj_t ret = new_class_obj(del);
  obj_add_ref(ret);
  return ret;
}

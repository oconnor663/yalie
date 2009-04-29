#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "object.h"
#include "../guts/guts.h"

struct Object {
  obj_t parent;
  table_t methods;
  scope_t members;
  void* guts;
  void (*free_guts)(void*);
  int ref_count;
};

obj_t new_obj( obj_t parent )
{
  obj_t ret = malloc( sizeof(struct Object) );
  ret->parent = parent;
  ret->methods = new_pointer_table();
  ret->members = new_scope( NULL );
  ret->guts = NULL;      //"child" and "clone" methods need to set this
  ret->free_guts = NULL; //and this
  ret->ref_count = 1;
  return ret;
}

void free_obj( obj_t obj )
{
  
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

bool is_child( obj_t obj, obj_t class )
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


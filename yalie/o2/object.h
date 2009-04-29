#ifndef object_h_
#define object_h_

#include <stdbool.h>
#include "../guts/symbol.h"

typedef struct Object * obj_t;

obj_t new_obj( obj_t parent );
void free_obj( obj_t obj );

void* obj_guts( obj_t obj );
void obj_set_guts( obj_t obj );
obj_t obj_parent( obj_t obj );

void obj_add_ref( obj_t obj );
void obj_del_ref( obj_t obj );

void obj_add_method( obj_t obj, sym_t name, obj_t method );
obj_t obj_ref_method( obj_t obj, sym_t name );
void obj_del_method( obj_t obj, sym_t name );

void obj_add_member( obj_t obj, sym_t name, obj_t member );
obj_t obj_ref_member( obj_t obj, sym_t name );
void obj_del_member( obj_t obj, sym_t name );

bool is_child( obj_t obj, obj_t class ); //hierarchical

obj_t ObjectClass();

void cleanup_base_classes();

#endif

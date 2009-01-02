#ifndef object_h_
#define object_h_

#include <stdbool.h>
#include "../guts/symbol.h"

typedef struct Object * obj_t;
typedef struct Class * class_t;


obj_t new_obj( obj_t class );
void obj_add_ref( obj_t obj );
void obj_del_ref( obj_t obj );

class_t obj_class( obj_t obj );

void* obj_guts( obj_t obj );
void obj_set_guts( obj_t obj, void* guts );

void obj_add_method( obj_t obj, sym_t name, obj_t method );
obj_t obj_ref_method( obj_t obj, sym_t name );
void obj_del_method( obj_t obj, sym_t name );
void obj_add_member( obj_t obj, sym_t name, obj_t member );
obj_t obj_ref_member( obj_t obj, sym_t name );
void obj_del_member( obj_t obj, sym_t name );


class_t new_class( obj_t parent );
void free_class( class_t class );

bool inherits_p( class_t child, class_t parent );

void class_add_method( class_t class, sym_t name, obj_t method );
obj_t class_ref_method( class_t class, sym_t name );
void class_del_method( class_t class, sym_t name );


extern obj_t Object_Class;
extern obj_t Class_Class;

void Init_Base_Classes();

obj_t new_class_obj( class_t class );

#endif

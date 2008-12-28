#ifndef object_h_
#define object_h_

#include <stdbool.h>
#include "../guts/symbol.h"

typedef struct Object * obj_t;
typedef struct Class * class_t;



obj_t new_obj( class_t class );
void obj_add_ref( obj_t obj );
void obj_del_ref( obj_t obj );

void* obj_guts( obj_t obj );



class_t new_class( class_t parent, sym_t type ); //parent's type
void free_class( class_t class );                //used when type
                                                 //arg is NULL
bool inherits_p( class_t child, class_t parent );

void class_add_method( class_t class, sym_t name );
obj_t class_ref_method( class_t class, sym_t name );
void class_del_method( class_t class, sym_t name );

#endif

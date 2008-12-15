#ifndef object_h_
#define object_h_

typedef struct Obj * obj_t;

val_t new_obj( class_t class );
void add_ref( val_t val );
void del_ref( val_t val );

void* obj_guts( obj_t obj );



#endif

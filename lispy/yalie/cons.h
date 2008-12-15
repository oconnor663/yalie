#ifndef cons_h_
#define cons_h_

typedef struct Cons * cons_t;

/* 
 * Note that conses are intended to be used both
 * by userspace functions and in building the interpreter.
 * As such, they are bare bones: the caller is expected
 * to handle any add_ref/del_ref bookkeeping, etc.
 */
cons_t new_cons( void* ar, void* dr );
void free_cons( cons_t cell );
void* car( cons_t cell );
void* cdr( cons_t cell );
void set_car( cons_t cell, void* val );
void set_cdr( cons_t cell, void* val );

#endif

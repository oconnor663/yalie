#ifndef core_h_
#define core_h_

#include <stdbool.h>

enum type {
  Nil,
  Cons,
  Symbol,
  Int
};

typedef struct Val {
  void* obj;
  enum type type;
  int ref_count;
} * val_t;

val_t new_val( void* obj, enum type type );
void add_ref( val_t val );
void del_ref( val_t val );

typedef struct Cons * cons_t;

//Note that conses are intended to be used both
//by userspace functions and in building the interpreter.
//As such, they are bare bones: the caller is expected
//to handle any add_ref/del_ref bookkeeping, etc.
cons_t new_cons( void* ar, void* dr );
void free_cons( cons_t cell );
void* car( cons_t cell );
void* cdr( cons_t cell );
void set_car( cons_t cell, val_t val );
void set_cdr( cons_t cell, val_t val );

typedef struct Symbol * sym_t;

sym_t new_sym( char* name ); //will duplicate name
void free_sym( sym_t sym );  //frees owned duplicate
char* repr_sym( sym_t sym ); //duplicates again
bool sym_eq_p( sym_t a, sym_t b );

typedef struct Int * int_t;

int_t new_int_z( long int i );
int_t new_int_s( char* str, int base );
void free_int( int_t i );
char* repr_int( int_t i );


#endif

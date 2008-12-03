#ifndef core_h_
#define core_h_

#include "types/cons.h"
#include "types/symbol.h"
#include "types/int.h"

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

/*
 * Printing is included here.
 */ 

char* repr( val_t val );

#endif

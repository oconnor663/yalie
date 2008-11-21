#ifndef core_h_
#define core_h_

enum type {
  Symbol,
  Cons,
  Int
};

typedef struct Val {
  void* obj;
  enum type type;
  int ref_count;
} * val_t;

val_t new_val( void* obj, enum type type );
void add_reference( val_t val );
void del_reference( val_t val );


typedef struct Cons * cons_t;

cons_t new_cons( void* ar, void* dr );
void free_cons( cons_t cell );
void* car( cons_t cell );
void* cdr( cons_t cell );

//typedef struct Symbol * symbol_t;
//typedef struct Int * int_t;

#endif

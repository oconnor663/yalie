#ifndef core_h_
#define core_h_

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

cons_t new_cons( void* ar, void* dr );
void free_cons( cons_t cell );
void* car( cons_t cell );
void* cdr( cons_t cell );


typedef struct Symbol * sym_t;

sym_t new_sym( char* name ); //will duplicate name
void free_sym( sym_t sym );  //frees owned duplicate
char* sym_name( sym_t sym ); //duplicates again

//typedef struct Int * int_t;

#endif

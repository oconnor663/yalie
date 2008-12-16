#ifndef int_h_
#define int_h_

typedef struct Int * int_t;

int_t new_int_z( long int i );
int_t new_int_s( char* str, int base );
void free_int( int_t i );

char* int_repr( int_t i );

int_t int_add( int_t a, obj_t b );
int_t int_sub( int_t a, obj_t b );
int_t int_neg( int_t a, obj_t b );

int_t int_mul( int_t a, obj_t b );
int_t int_div( int_t a, obj_t b );
int_t int_exp( int_t a, obj_t b );

typedef struct Float * float_t;

float_t new_float_f( double x );
float_t new_float_s( char* str, int base );
void free_float( float_t i );

char* float_repr( float_t i );

float_t float_add( float_t a, obj_t b );
float_t float_sub( float_t a, obj_t b );
float_t float_neg( float_t a, obj_t b );

float_t float_mul( float_t a, obj_t b );
float_t float_div( float_t a, obj_t b );
float_t float_exp( float_t a, obj_t b );

#endif

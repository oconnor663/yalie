#ifndef int_h_
#define int_h_

#include <stdbool.h>

typedef struct Int * int_t;

int_t new_int_z( long int i );
int_t new_int_s( char* str, int base );
void free_int( int_t i );

char* int_repr( int_t i );

bool int_eq( int_t a, int_t b )

int_t int_add( int_t a, int_t b );
int_t int_sub( int_t a, int_t b );
int_t int_neg( int_t i );

int_t int_mul( int_t a, int_t b );
int_t int_div( int_t a, int_t b );
int_t int_exp( int_t a, int_t b );

int_t int_and( int_t a, int_t b );
int_t int_or( int_t a, int_t b );
int_t int_xor( int_t a, int_t b );


typedef struct Float * float_t;

float_t new_float_f( double x );
float_t new_float_s( char* str, int base );
void free_float( float_t f );

char* float_repr( float_t f );

bool float_eq( float_t a, float_t b );
bool float_eq_i( float_t a, int_t b );

float_t float_add( float_t a, float_t b );
float_t float_add_i( float_t a, int_t b );
float_t float_sub( float_t a, float_t b );
float_t float_sub_i( float_t a, int_t b );
float_t float_neg( float_t f );

float_t float_mul( float_t a, float_t b );
float_t float_mul_i( float_t a, int_t b );
float_t float_div( float_t a, float_t b );
float_t float_div_i( float_t a, int_t b );
float_t float_exp( float_t a, float_t b );
float_t float_exp_i( float_t a, int_t b );

#endif

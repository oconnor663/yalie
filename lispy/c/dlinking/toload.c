#include <stdio.h>

void resolveme();

int t2( int i )
{
  resolveme();
  printf( "t2 is working\n" );
  return 2*i;
}

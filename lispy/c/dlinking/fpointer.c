#include <stdio.h>

void map( int* list, int len, void (*f)(int) )
{
  int i=0;
  for (;i<len;i++)
    f(list[i]);
}

void ppo( int i )
{
  printf( "%i\n", i+1 );
}

main()
{
  int list[3] = {3,4,5};
  int len = 3;
  map(list,len,ppo);
}

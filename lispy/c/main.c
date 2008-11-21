#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "core.h"
#include "input.h"

int main( int argc, char** argv )
{
  char holder;
  char* line = getline(true);
  while (line) {
    if (line[0]!='\0')
      printf( "%s\n", line );
    free(line);
    line = getline(true);
  }
  printf( "\n" );
}

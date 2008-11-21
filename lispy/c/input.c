#include <stdio.h>
#include <readline/readline.h>
#include "input.h"

#define PROMPT ">>> "
#define REPROMPT "... "

char* getline( bool new_expr )
{
  char* line = readline( new_expr?PROMPT:REPROMPT );
  if (line && line[0]!='\0')
    add_history(line);
  return line;
}


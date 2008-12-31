#include <stdio.h>
#include <dlfcn.h>

void resolveme()
{
  printf( "SUCCESS!\n" );
}

main()
{
  void* handle = dlopen("./toload.so", RTLD_LAZY );
  
  int (*func)(int);

  func = (int (*)(int)) dlsym(handle,"t2");

  printf( "%i\n", func(4) );

  dlclose(handle);
}

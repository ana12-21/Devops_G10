// fixtures/commits/C0/config.h — PPT slide 24
// MODE=0 is the default; C2 overrides it via Makefile CFLAGS (-DMODE=7).
// The #ifndef guard is what makes that override possible: a plain
// `#define MODE 0` would win over `-D` (and GCC would warn "MODE redefined").

#ifndef MODE
#define MODE  0
#endif

#define BASE 10
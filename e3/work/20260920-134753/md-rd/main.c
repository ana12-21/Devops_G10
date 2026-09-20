// fixtures/md-rd/main.c — PPT slide 17
// Reads config.h but Makefile does not declare it (MD).
// Does NOT read unused.h but Makefile declares it (RD).

#include <stdio.h>
#include "config.h"

int main(void) {
    printf("%d\n", VALUE);
    return 0;
}
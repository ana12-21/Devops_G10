// fixtures/commits/C2/main.c — unchanged from C1 (PPT slide 26)
// incremental = 12, clean = 19  (MODE overridden by CFLAGS -DMODE=7)

#include <stdio.h>
#include "config.h"
#include "feature.h"

int main(void) {
    printf("BASE=%d FEATURE=%d MODE=%d\n", BASE, FEATURE, MODE);
    return 0;
}
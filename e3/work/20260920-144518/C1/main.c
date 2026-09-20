// fixtures/commits/C1/main.c — PPT slide 25
// Added #include "feature.h", Makefile NOT updated.
// clean build output: 12  (BASE=10 + FEATURE=2 + MODE=0)
// EXPECTED FINDING: main.o is MISSING feature.h dependency.

#include <stdio.h>
#include "config.h"
#include "feature.h"

int main(void) {
    printf("BASE=%d FEATURE=%d MODE=%d\n", BASE, FEATURE, MODE);
    return 0;
}
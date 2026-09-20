// fixtures/commits/C0/main.c — PPT slide 24
// Declared correctly: only reads config.h (and standard headers).
// clean build output: 10  (BASE=10, MODE=0)

#include <stdio.h>
#include "config.h"

int main(void) {
    printf("BASE=%d MODE=%d\n", BASE, MODE);
    return 0;
}
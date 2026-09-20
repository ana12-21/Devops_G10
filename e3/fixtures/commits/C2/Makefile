# fixtures/commits/C2/Makefile — PPT slide 26
# C2: only compile command changed:  CFLAGS adds -DMODE=7
# Source code unchanged from C1.
# incremental = 12   (plain make by timestamp does NOT detect the command change)
# clean      = 19   (BASE=10 + FEATURE=2 + MODE=7)

CC      ?= cc
CFLAGS  ?= -O0 -Wall -DMODE=7

main.o: main.c config.h
	$(CC) $(CFLAGS) -c main.c -o main.o

main: main.o
	$(CC) main.o -o main

clean:
	rm -f main.o main
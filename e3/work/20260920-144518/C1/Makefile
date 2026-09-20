# fixtures/commits/C1/Makefile — PPT slide 25
# C1: main.c adds #include "feature.h", but Makefile is NOT updated.
# clean build output = 12  (BASE=10 + FEATURE=2 + MODE=0)
# EXPECTED FINDING: main.o is MISSING feature.h.

CC      ?= cc
CFLAGS  ?= -O0 -Wall

main.o: main.c config.h
	$(CC) $(CFLAGS) -c main.c -o main.o

main: main.o
	$(CC) main.o -o main

clean:
	rm -f main.o main
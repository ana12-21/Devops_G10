# fixtures/commits/C0/Makefile — PPT slide 24
# C0: declared correctly. clean build output = 10.
# main.o's project dependency on config.h is properly declared.

CC      ?= cc
CFLAGS  ?= -O0 -Wall

main.o: main.c config.h
	$(CC) $(CFLAGS) -c main.c -o main.o

main: main.o
	$(CC) main.o -o main

clean:
	rm -f main.o main
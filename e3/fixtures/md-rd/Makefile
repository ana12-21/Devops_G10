# fixtures/md-rd/Makefile — PPT slide 17
# Findings to verify:
#   MISSING:   main.o reads config.h but Makefile does not declare it
#   REDUNDANT: Makefile declares unused.h but main.o does not read it
#
# Expected behaviour (slides 18-21):
#   make && ./app               -> 1  (config.h = VALUE 1)
#   edit config.h -> VALUE 2; make; ./app  -> still 1  (MD:漏重建)
#   make clean && make && ./app -> 2  (clean build picks up new VALUE)
#   edit unused.h comment; make -> re-runs "cc -c main.c"  (RD:多余编译)

CC      ?= cc
CFLAGS  ?= -O0 -Wall

main.o: main.c unused.h
	$(CC) $(CFLAGS) -c main.c -o main.o

app: main.o
	$(CC) main.o -o app

clean:
	rm -f main.o app
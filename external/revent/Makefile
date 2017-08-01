#use below for aarch64 and arm-eabi (may work for chromebook)
#CROSS_COMPILE=aarch64-linux-gnu-
#CROSS_COMPILE=arm-eabi-
#use below for chromebook
CROSS_COMPILE=armv8l-linux-gnueabihf-
CC=gcc

ifdef DEBUG
	CFLAGS=-static -lc -02 #g
else
	CFLAGS=-static -lc -O2
endif

revent: revent.c
	$(CROSS_COMPILE)$(CC) $(CFLAGS) revent.c -o revent

clean:
	rm -rf revent

.PHONY: clean

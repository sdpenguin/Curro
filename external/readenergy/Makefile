# To build:
#
# CROSS_COMPILE=aarch64-linux-gnu- make
# For chromebook: won't work because of 64 bit issues that need fixing:
# CROSS_COMPILE=armv8l-linux-gnueabihf-

CROSS_COMPILE?=aarch64-linux-gnu-
CC=$(CROSS_COMPILE)gcc
CFLAGS='-Wl,-static -Wl,-lc'

readenergy: readenergy.c
	$(CC) $(CFLAGS) readenergy.c -o readenergy
	cp readenergy ../../instrumentation/juno_energy/readenergy

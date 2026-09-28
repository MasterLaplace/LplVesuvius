# The C core of the prize software: a shared library the Python layer loads.
#
#   make            the library, optimised WITH its symbols (-O2 -g), into vesuve/_core/
#   make test       the C tests, under AddressSanitizer and UndefinedBehaviorSanitizer
#   make debug      the library without optimisation, for the debugger
#   make clean
#
# ⚠ The warnings live HERE, not in the CI: whoever builds by hand sees exactly what the merge gate
# will see. None is tolerated (-Werror).

CC       ?= cc
WARN     := -std=c11 -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wsign-conversion \
            -Wdouble-promotion -Wstrict-prototypes -Wmissing-prototypes -Werror
COMMON   := $(WARN) -Icore/include -fPIC
OPTIMISE := -O2 -g
NOOPT    := -O0 -g3
SANITISE := -O1 -g3 -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all

SOURCES  := $(wildcard core/src/*.c)
TESTS    := $(wildcard core/tests/test_*.c)
OUTPUT   := vesuve/_core
LIBRARY  := $(OUTPUT)/libvesuve.so

.PHONY: all debug test clean

all: $(LIBRARY)

$(LIBRARY): $(SOURCES) core/include/vesuve.h
	@mkdir -p $(OUTPUT)
	$(CC) $(COMMON) $(OPTIMISE) -shared -o $@ $(SOURCES) -lm

debug: $(SOURCES) core/include/vesuve.h
	@mkdir -p $(OUTPUT)
	$(CC) $(COMMON) $(NOOPT) -shared -o $(LIBRARY) $(SOURCES) -lm

build/tests/%: core/tests/%.c $(SOURCES) core/include/vesuve.h core/tests/minitest.h
	@mkdir -p build/tests
	$(CC) $(COMMON) $(SANITISE) -Icore/tests -o $@ $< $(SOURCES) -lm

test: $(patsubst core/tests/%.c,build/tests/%,$(TESTS))
	@failed=0; for t in $^; do ./$$t || failed=1; done; exit $$failed

clean:
	rm -rf build $(OUTPUT)

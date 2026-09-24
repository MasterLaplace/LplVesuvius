# Le noyau C du logiciel des prix : une bibliothèque partagée que la couche Python charge.
#
#   make            la bibliothèque, optimisée AVEC ses symboles (-O2 -g), dans vesuve/_noyau/
#   make test       les tests C, sous AddressSanitizer et UndefinedBehaviorSanitizer
#   make debug      la bibliothèque sans optimisation, pour le débogueur
#   make clean
#
# ⚠ Les avertissements vivent ICI, pas dans la CI : qui compile à la main voit exactement ce que la
# porte de merge verra. Aucun n'est toléré (-Werror).

CC      ?= cc
AVERTIR := -std=c11 -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wsign-conversion \
           -Wdouble-promotion -Wstrict-prototypes -Wmissing-prototypes -Werror
COMMUN  := $(AVERTIR) -Inoyau/include -fPIC
OPTIM   := -O2 -g
SANS    := -O0 -g3
SANITIZ := -O1 -g3 -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all

SOURCES := $(wildcard noyau/src/*.c)
TESTS   := $(wildcard noyau/tests/test_*.c)
SORTIE  := vesuve/_noyau
BIB     := $(SORTIE)/libvesuve.so

.PHONY: all debug test clean

all: $(BIB)

$(BIB): $(SOURCES) noyau/include/vesuve.h
	@mkdir -p $(SORTIE)
	$(CC) $(COMMUN) $(OPTIM) -shared -o $@ $(SOURCES) -lm

debug: $(SOURCES) noyau/include/vesuve.h
	@mkdir -p $(SORTIE)
	$(CC) $(COMMUN) $(SANS) -shared -o $(BIB) $(SOURCES) -lm

build/tests/%: noyau/tests/%.c $(SOURCES) noyau/include/vesuve.h noyau/tests/minitest.h
	@mkdir -p build/tests
	$(CC) $(COMMUN) $(SANITIZ) -Inoyau/tests -o $@ $< $(SOURCES) -lm

test: $(patsubst noyau/tests/%.c,build/tests/%,$(TESTS))
	@echec=0; for t in $^; do ./$$t || echec=1; done; exit $$echec

clean:
	rm -rf build $(SORTIE)

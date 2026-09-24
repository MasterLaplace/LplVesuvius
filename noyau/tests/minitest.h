/*
 * minitest.h -- le plus petit harnais qui fasse échouer un test pour de bon.
 *
 * Chaque vérification est comptée, un échec imprime son fichier, sa ligne et ce qui était attendu,
 * et `FIN()` rend 1 s'il y a eu un échec OU si aucune vérification n'a tourné : une batterie vide
 * n'est pas une batterie verte.
 */
#ifndef MINITEST_H
#define MINITEST_H

#include <math.h>
#include <stdio.h>

static int minitest_verifications = 0;
static int minitest_echecs = 0;

#define VERIFIER(condition)                                                                        \
    do {                                                                                           \
        ++minitest_verifications;                                                                  \
        if (!(condition)) {                                                                        \
            ++minitest_echecs;                                                                     \
            fprintf(stderr, "  ECHEC %s:%d : %s\n", __FILE__, __LINE__, #condition);               \
        }                                                                                          \
    } while (0)

#define VERIFIER_PROCHE(obtenu, attendu, tolerance)                                                \
    do {                                                                                           \
        double minitest_o_ = (double)(obtenu), minitest_a_ = (double)(attendu);                     \
        ++minitest_verifications;                                                                  \
        if (!(fabs(minitest_o_ - minitest_a_) <= (double)(tolerance))) {                            \
            ++minitest_echecs;                                                                     \
            fprintf(stderr, "  ECHEC %s:%d : %s = %.10g, attendu %.10g (tolerance %g)\n",           \
                    __FILE__, __LINE__, #obtenu, minitest_o_, minitest_a_, (double)(tolerance));   \
        }                                                                                          \
    } while (0)

#define FIN(nom)                                                                                   \
    do {                                                                                           \
        if (minitest_verifications == 0) {                                                         \
            fprintf(stderr, "%s : AUCUNE vérification n'a tourné\n", nom);                          \
            return 1;                                                                              \
        }                                                                                          \
        fprintf(stderr, "%s : %d vérifications, %d échecs\n", nom, minitest_verifications,          \
                minitest_echecs);                                                                  \
        return minitest_echecs ? 1 : 0;                                                            \
    } while (0)

#endif /* MINITEST_H */

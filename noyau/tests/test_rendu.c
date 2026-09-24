/* test_rendu.c -- l'échantillonnage le long des normales, sur un volume dont on connaît la valeur partout. */
#include <stdlib.h>

#include "minitest.h"
#include "vesuve.h"

enum { NZ = 20, NY = 16, NX = 12 };

int main(void)
{
    /* V = x + 2y + 3z est linéaire : l'interpolation trilinéaire le rend EXACTEMENT. */
    uint8_t volume[NZ * NY * NX];
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x) volume[(z * NY + y) * NX + x] = (uint8_t)(x + 2 * y + 3 * z);

    const float points[] = {4.5f, 6.25f, 8.0f,   /* un point intérieur */
                            1.0f, 1.0f, 1.0f,    /* un point dont la normale sort du volume */
                            -1.0f, -1.0f, -1.0f}; /* un point invalide, la sentinelle tifxyz */
    const float normales[] = {0.0f, 0.0f, 1.0f, 0.0f, 0.0f, -1.0f, 0.0f, 0.0f, 1.0f};
    const float decalages[] = {-2.0f, 0.0f, 1.5f};
    float sortie[3 * 3];
    uint8_t valide[3 * 3];
    VERIFIER(vesuve_echantillonner_le_long_des_normales(volume, NZ, NY, NX, points, normales, 3, decalages,
                                                        3, sortie, valide) == VESUVE_OK);
    /* point 0 : x + 2y + 3z = 4,5 + 12,5 + 3 (8 + d) */
    VERIFIER(valide[0 * 3 + 0] == 1);
    VERIFIER_PROCHE(sortie[0 * 3 + 0], 4.5 + 12.5 + 3.0 * 6.0, 1e-4);
    VERIFIER_PROCHE(sortie[1 * 3 + 0], 4.5 + 12.5 + 3.0 * 8.0, 1e-4);
    VERIFIER_PROCHE(sortie[2 * 3 + 0], 4.5 + 12.5 + 3.0 * 9.5, 1e-4);
    /* point 1 : z = 1 - d ; d = 1,5 donne z = -0,5, hors du volume, donc invalide */
    VERIFIER(valide[0 * 3 + 1] == 1 && valide[2 * 3 + 1] == 0);
    VERIFIER_PROCHE(sortie[0 * 3 + 1], 1.0 + 2.0 + 3.0 * 3.0, 1e-4);
    /* point 2 : la sentinelle -1 ne se rend jamais */
    VERIFIER(valide[1 * 3 + 2] == 0 && sortie[1 * 3 + 2] == 0.0f);

    VERIFIER(vesuve_echantillonner_le_long_des_normales(volume, NZ, NY, NX, points, normales, 3, decalages,
                                                        0, sortie, valide) == VESUVE_ARGUMENT);
    FIN("test_rendu");
}

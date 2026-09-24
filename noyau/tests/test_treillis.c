/* test_treillis.c -- E4 : le filtre, les bords, le pas d'une coupe et d'une couture. */
#include <stdlib.h>
#include <string.h>

#include "minitest.h"
#include "vesuve.h"

enum { NZ = 109, NY = 128, NX = 128, N = 109 };

static double bosse(int z, double centre)
{
    const double d = ((double)z - centre) / 4.0;
    return 100.0 * exp(-d * d);
}

static void pas_dune_coupe(void)
{
    double a[N], b[N];
    for (int z = 0; z < N; ++z) {
        a[z] = bosse(z, 50.0);
        b[z] = bosse(z, 57.0); /* la même matière, sept couches plus bas dans le chunk b */
    }
    int pas = 99, sature = 9;
    VERIFIER(vesuve_pas_dune_coupe(a, b, N, 36, &pas, &sature) == VESUVE_OK);
    VERIFIER(pas == 7);
    VERIFIER(sature == 0);

    VERIFIER(vesuve_pas_dune_coupe(b, a, N, 36, &pas, &sature) == VESUVE_OK);
    VERIFIER(pas == -7); /* le signe suit l'ordre des deux chunks */

    for (int z = 0; z < N; ++z) b[z] = bosse(z, 50.0 + 40.0);
    VERIFIER(vesuve_pas_dune_coupe(a, b, N, 36, &pas, &sature) == VESUVE_OK);
    VERIFIER(sature == 1); /* 40 couches dépassent la plage : la couture a pu sauter */

    double plat[N];
    for (int z = 0; z < N; ++z) plat[z] = 12.0;
    VERIFIER(vesuve_pas_dune_coupe(a, plat, N, 36, &pas, &sature) == VESUVE_INDECIDABLE);
    VERIFIER(vesuve_pas_dune_coupe(a, b, N, 0, &pas, &sature) == VESUVE_ARGUMENT);
}

static void egalite_exacte(void)
{
    /* Une impulsion dans a, deux dans b à dix couches de part et d'autre : les décalages -10 et +10
       alignent chacun une impulsion. Toutes les valeurs centrées sont ENTIÈRES (moyennes 1 et 2),
       donc les deux scores sont égaux au bit, et le PREMIER maximum -- le pas le plus positif,
       comme np.argmax chez le producteur -- doit gagner. */
    double a[N], b[N];
    for (int z = 0; z < N; ++z) a[z] = b[z] = 0.0;
    a[54] = 109.0;
    b[44] = 109.0;
    b[64] = 109.0;
    int pas = 0, sature = 0;
    VERIFIER(vesuve_pas_dune_coupe(a, b, N, 36, &pas, &sature) == VESUVE_OK);
    VERIFIER(pas == 10);
}

static void pas_dune_couture(void)
{
    /* Quatre coupes aux pas 1, 3, 1, 3 : moyenne 2, désaccord (1 + 1) / 2 - (3 + 3) / 2 = -2. */
    enum { C = 5 };
    static double a[C * N], b[C * N];
    const int decalages[C] = {1, 3, 1, 3, 0};
    for (int c = 0; c < C; ++c)
        for (int z = 0; z < N; ++z) {
            a[c * N + z] = bosse(z, 50.0);
            b[c * N + z] = bosse(z, 50.0 + decalages[c]);
        }
    const uint8_t lisible[C] = {1, 1, 1, 1, 0}; /* la cinquième n'existe que d'un côté */
    double pas = 0.0, desaccord = 0.0;
    int coupes = 0;
    VERIFIER(vesuve_pas_dune_couture(a, b, lisible, C, N, 36, &pas, &desaccord, &coupes) == VESUVE_OK);
    VERIFIER_PROCHE(pas, 2.0, 1e-12);
    VERIFIER_PROCHE(desaccord, -2.0, 1e-12);
    VERIFIER(coupes == 4);

    const uint8_t une_seule[C] = {1, 0, 0, 0, 0};
    VERIFIER(vesuve_pas_dune_couture(a, b, une_seule, C, N, 36, &pas, &desaccord, &coupes) ==
             VESUVE_INDECIDABLE);
}

static void bords_et_profondeur(void)
{
    uint8_t *bloc = malloc((size_t)NZ * NY * NX);
    VERIFIER(bloc != NULL);
    if (!bloc) return;
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                bloc[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)((x + y) % 256);
    const int coupes[2] = {4, 124};
    uint16_t droit[2 * NZ], gauche[2 * NZ], bas[2 * NZ], haut[2 * NZ];
    VERIFIER(vesuve_profils_de_bord(bloc, NZ, NY, NX, coupes, 2, 16, droit, gauche, bas, haut) ==
             VESUVE_OK);
    /* rangée 4 : x de 112 à 127 donne (116 + ... + 131) = 1976 ; x de 0 à 15 donne 4*16 + 120 = 184 */
    VERIFIER(droit[0] == 1976 && gauche[0] == 184);
    /* colonne 124 : y de 112 à 127 donne 16*124 + 1912 = 3896, modulo 256 par voxel -- calculé :
       (124 + y) % 256 pour y = 112..127 vaut 236..251, somme 3896 ; y = 0..15 vaut 124..139, 2104 */
    VERIFIER(bas[1 * NZ + 5] == 3896 && haut[1 * NZ + 5] == 2104);

    double profil[NZ];
    for (int z = 0; z < NZ; ++z)
        memset(bloc + (size_t)z * NY * NX, z, (size_t)NY * NX);
    VERIFIER(vesuve_profil_de_profondeur(bloc, NZ, NY, NX, profil) == VESUVE_OK);
    VERIFIER_PROCHE(profil[0], 0.0, 1e-12);
    VERIFIER_PROCHE(profil[77], 77.0, 1e-12);
    VERIFIER(vesuve_profils_de_bord(bloc, NZ, NY, NX, coupes, 2, 0, droit, gauche, bas, haut) ==
             VESUVE_ARGUMENT);
    free(bloc);
}

static void filtre(void)
{
    uint8_t *bloc = malloc((size_t)NZ * NY * NX);
    VERIFIER(bloc != NULL);
    if (!bloc) return;
    int couches = -1, retenu = -1;

    /* Des stries le long de x : un gradient dans une seule direction, cohérence 1. */
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                bloc[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(128 + 100 * sin(y / 3.0));
    VERIFIER(vesuve_filtre_de_texture(bloc, NZ, NY, NX, 0.15, &couches, &retenu) == VESUVE_OK);
    VERIFIER(couches == NZ && retenu == 1);

    /* Un bruit sans direction : cohérence proche de zéro dans chaque couche. */
    srand(20260924u);
    for (size_t i = 0; i < (size_t)NZ * NY * NX; ++i) bloc[i] = (uint8_t)(rand() % 256);
    VERIFIER(vesuve_filtre_de_texture(bloc, NZ, NY, NX, 0.15, &couches, &retenu) == VESUVE_OK);
    VERIFIER(couches == 0 && retenu == 0);

    /* Exactement nz / 4 = 27 couches striées suffisent, 26 non. */
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                if (z < 27)
                    bloc[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(128 + 100 * sin(y / 3.0));
    VERIFIER(vesuve_filtre_de_texture(bloc, NZ, NY, NX, 0.15, &couches, &retenu) == VESUVE_OK);
    VERIFIER(couches == 27 && retenu == 1);
    for (int y = 0; y < NY; ++y)
        for (int x = 0; x < NX; ++x) bloc[((size_t)26 * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(rand() % 256);
    VERIFIER(vesuve_filtre_de_texture(bloc, NZ, NY, NX, 0.15, &couches, &retenu) == VESUVE_OK);
    VERIFIER(couches == 26 && retenu == 0);

    /* Un bloc uniforme n'a aucun gradient : aucune couche n'est texturée, sans division par zéro. */
    memset(bloc, 7, (size_t)NZ * NY * NX);
    VERIFIER(vesuve_filtre_de_texture(bloc, NZ, NY, NX, 0.15, &couches, &retenu) == VESUVE_OK);
    VERIFIER(couches == 0 && retenu == 0);
    free(bloc);
}

int main(void)
{
    pas_dune_coupe();
    egalite_exacte();
    pas_dune_couture();
    bords_et_profondeur();
    filtre();
    FIN("test_treillis");
}

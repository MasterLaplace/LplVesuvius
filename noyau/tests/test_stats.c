/* test_stats.c -- l'aire sous la courbe, et ses deux bords. */
#include "minitest.h"
#include "vesuve.h"

int main(void)
{
    vesuve_paire travail[16];
    double auc = -1.0;

    const double parfait[] = {0.1, 0.2, 0.8, 0.9};
    const uint8_t etiquettes[] = {0, 0, 1, 1};
    VERIFIER(vesuve_aire_sous_la_courbe(parfait, etiquettes, 4, travail, &auc) == VESUVE_OK);
    VERIFIER_PROCHE(auc, 1.0, 1e-12);

    const double inverse[] = {0.9, 0.8, 0.2, 0.1};
    VERIFIER(vesuve_aire_sous_la_courbe(inverse, etiquettes, 4, travail, &auc) == VESUVE_OK);
    VERIFIER_PROCHE(auc, 0.0, 1e-12);

    /* Tout ex aequo : rangs moyens, donc exactement le hasard. */
    const double egaux[] = {0.5, 0.5, 0.5, 0.5};
    VERIFIER(vesuve_aire_sous_la_courbe(egaux, etiquettes, 4, travail, &auc) == VESUVE_OK);
    VERIFIER_PROCHE(auc, 0.5, 1e-12);

    /* Un cas à la main : positifs 0,4 et 0,7 contre négatifs 0,1, 0,4, 0,9.
       Paires gagnées : (0,4 > 0,1) + 0,5 (0,4 = 0,4) + (0,7 > 0,1) + (0,7 > 0,4) = 3,5 sur 6. */
    const double mele[] = {0.1, 0.4, 0.9, 0.4, 0.7};
    const uint8_t e2[] = {0, 0, 0, 1, 1};
    VERIFIER(vesuve_aire_sous_la_courbe(mele, e2, 5, travail, &auc) == VESUVE_OK);
    VERIFIER_PROCHE(auc, 3.5 / 6.0, 1e-12);

    const uint8_t sans_positif[] = {0, 0, 0, 0};
    VERIFIER(vesuve_aire_sous_la_courbe(parfait, sans_positif, 4, travail, &auc) == VESUVE_INDECIDABLE);
    FIN("test_stats");
}

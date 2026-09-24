/* stats.c -- les statistiques de validation : l'aire sous la courbe aux rangs moyens. */
#include <stdlib.h>

#include "vesuve.h"

static int par_score(const void *gauche, const void *droite)
{
    const double a = ((const vesuve_paire *)gauche)->score, b = ((const vesuve_paire *)droite)->score;
    return (a > b) - (a < b);
}

vesuve_statut vesuve_aire_sous_la_courbe(const double *scores, const uint8_t *etiquettes, size_t n,
                                         vesuve_paire *travail, double *auc)
{
    if (!scores || !etiquettes || !travail || !auc || n == 0) return VESUVE_ARGUMENT;
    size_t positifs = 0;
    for (size_t i = 0; i < n; ++i) {
        travail[i].score = scores[i];
        travail[i].etiquette = etiquettes[i] ? 1u : 0u;
        positifs += travail[i].etiquette;
    }
    const size_t negatifs = n - positifs;
    if (positifs == 0 || negatifs == 0) return VESUVE_INDECIDABLE;
    qsort(travail, n, sizeof *travail, par_score);
    /* Un groupe d'ex aequo occupant [debut, fin) reçoit le rang moyen (debut + fin + 1) / 2. */
    double somme_des_rangs = 0.0;
    for (size_t debut = 0; debut < n;) {
        size_t fin = debut + 1;
        while (fin < n && travail[fin].score == travail[debut].score) ++fin;
        const double rang = ((double)debut + (double)fin + 1.0) / 2.0;
        for (size_t i = debut; i < fin; ++i)
            if (travail[i].etiquette) somme_des_rangs += rang;
        debut = fin;
    }
    const double p = (double)positifs, q = (double)negatifs;
    *auc = (somme_des_rangs - p * (p + 1.0) / 2.0) / (p * q);
    return VESUVE_OK;
}

/* formulaire.c -- les équations fermées que le dépôt a validées. Chacune cite son fait. */
#include <math.h>

#include "vesuve.h"

/* hc en keV·m : lambda[m] = HC_KEV_M / E[keV] (CODATA 2018), comme `nombre_de_fresnel.py:87`. */
static const double HC_KEV_M = 1.23984193e-9;

vesuve_statut vesuve_demi_feuillet_voxels(double pas_um, double voxel_um, int *demi)
{
    if (!demi || !(pas_um > 0.0) || !(voxel_um > 0.0)) return VESUVE_ARGUMENT;
    /* Python rend round(x) au pair le plus proche sur un demi exact ; nearbyint fait de même
       dans le mode d'arrondi par défaut. */
    *demi = (int)nearbyint(pas_um / voxel_um / 2.0);
    return VESUVE_OK;
}

vesuve_statut vesuve_longueur_tenable(double demi_feuillet, double sigma, double *n_max)
{
    if (!n_max || !(demi_feuillet > 0.0) || !(sigma > 0.0)) return VESUVE_ARGUMENT;
    const double r = demi_feuillet / sigma;
    *n_max = r * r;
    return VESUVE_OK;
}

vesuve_statut vesuve_dispersion_de_k_rangees(double sigma_partage, double sigma_propre, int k,
                                             double *sigma_k)
{
    if (!sigma_k || k < 1 || sigma_partage < 0.0 || sigma_propre < 0.0) return VESUVE_ARGUMENT;
    *sigma_k = sqrt(sigma_partage * sigma_partage + sigma_propre * sigma_propre / (double)k);
    return VESUVE_OK;
}

vesuve_statut vesuve_bruit_propre_du_triangle(double v_ij, double v_ik, double v_jk, double *variance)
{
    if (!variance || v_ij < 0.0 || v_ik < 0.0 || v_jk < 0.0) return VESUVE_ARGUMENT;
    const double v = (v_ij + v_ik - v_jk) / 2.0;
    if (v < 0.0) return VESUVE_INDECIDABLE; /* une variance négative réfute le modèle des bruits propres */
    *variance = v;
    return VESUVE_OK;
}

vesuve_statut vesuve_erreur_dune_dispersion(double sigma, int n, double *erreur)
{
    if (!erreur || n < 1 || sigma < 0.0) return VESUVE_ARGUMENT;
    *erreur = sigma / sqrt(2.0 * (double)n);
    return VESUVE_OK;
}

vesuve_statut vesuve_compte_decisif(double garantie, int *compte)
{
    if (!compte || !(garantie > 0.0) || !(garantie < 1.0)) return VESUVE_ARGUMENT;
    *compte = (int)ceil(9.0 * (1.0 - garantie) / garantie);
    return VESUVE_OK;
}

vesuve_statut vesuve_longueur_de_bloc(int n, int *longueur)
{
    if (!longueur || n < 1) return VESUVE_ARGUMENT;
    /* pow et non cbrt : le producteur calcule n ** (1.0 / 3.0), c'est-à-dire ce même pow. */
    const int b = (int)ceil(pow((double)n, 1.0 / 3.0));
    *longueur = b < 1 ? 1 : (b > n ? n : b);
    return VESUVE_OK;
}

vesuve_statut vesuve_alpha_de_convergence(double e0, double e1, double n0, double n1, double *alpha)
{
    if (!alpha || !(n0 > 0.0) || !(n1 > 0.0) || e1 < 0.0) return VESUVE_ARGUMENT;
    if (n1 / n0 < 2.0) return VESUVE_INDECIDABLE; /* une fenêtre qui ne double pas ne donne pas de pente */
    if (!(e0 > 0.0) || !(e1 > 0.0)) return VESUVE_INDECIDABLE;
    *alpha = log(e1 / e0) / log(n1 / n0);
    return VESUVE_OK;
}

vesuve_statut vesuve_coherence(const double *increments, int n, double *coherence)
{
    if (!increments || !coherence || n < 1) return VESUVE_ARGUMENT;
    double somme = 0.0, absolue = 0.0;
    for (int i = 0; i < n; ++i) {
        somme += increments[i];
        absolue += fabs(increments[i]);
    }
    if (!(absolue > 0.0)) return VESUVE_INDECIDABLE; /* rien n'a tourné : ni cohérent, ni incohérent */
    *coherence = fabs(somme) / absolue;
    return VESUVE_OK;
}

vesuve_statut vesuve_coherence_corrigee(double coherence, int n, double *corrigee)
{
    if (!corrigee || n < 2 || coherence < 0.0 || coherence > 1.0) return VESUVE_ARGUMENT;
    const double plancher = 1.0 / sqrt((double)n);
    const double c = (coherence - plancher) / (1.0 - plancher);
    *corrigee = c > 0.0 ? c : 0.0;
    return VESUVE_OK;
}

vesuve_statut vesuve_nombre_de_fresnel(double pas_um, double distance_m, double energie_kev,
                                       double *fresnel)
{
    if (!fresnel || !(pas_um > 0.0) || distance_m < 0.0 || !(energie_kev > 0.0)) return VESUVE_ARGUMENT;
    const double lambda_m = HC_KEV_M / energie_kev;
    *fresnel = sqrt(lambda_m * distance_m) * 1e6 / pas_um; /* l ordre du producteur, au bit pres */
    return VESUVE_OK;
}

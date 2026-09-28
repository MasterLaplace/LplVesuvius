/* formulary.c -- the closed-form equations the research validated. Each one cites its fact. */
#include <math.h>

#include "vesuve.h"

/* hc in keV·m: lambda[m] = HC_KEV_M / E[keV] (CODATA 2018), as in `nombre_de_fresnel.py:87`. */
static const double HC_KEV_M = 1.23984193e-9;

vesuve_status vesuve_half_sheet_voxels(double step_um, double voxel_um, int *half)
{
    if (!half || !(step_um > 0.0) || !(voxel_um > 0.0)) return VESUVE_BAD_ARGUMENT;
    /* Python rounds an exact half to the nearest even; nearbyint does the same in the default
       rounding mode. */
    *half = (int)nearbyint(step_um / voxel_um / 2.0);
    return VESUVE_OK;
}

vesuve_status vesuve_holdable_length(double half_sheet, double sigma, double *n_max)
{
    if (!n_max || !(half_sheet > 0.0) || !(sigma > 0.0)) return VESUVE_BAD_ARGUMENT;
    const double r = half_sheet / sigma;
    *n_max = r * r;
    return VESUVE_OK;
}

vesuve_status vesuve_spread_of_k_rows(double sigma_shared, double sigma_own, int k, double *sigma_k)
{
    if (!sigma_k || k < 1 || sigma_shared < 0.0 || sigma_own < 0.0) return VESUVE_BAD_ARGUMENT;
    *sigma_k = sqrt(sigma_shared * sigma_shared + sigma_own * sigma_own / (double)k);
    return VESUVE_OK;
}

vesuve_status vesuve_triangle_own_noise(double v_ij, double v_ik, double v_jk, double *variance)
{
    if (!variance || v_ij < 0.0 || v_ik < 0.0 || v_jk < 0.0) return VESUVE_BAD_ARGUMENT;
    const double v = (v_ij + v_ik - v_jk) / 2.0;
    if (v < 0.0) return VESUVE_UNDECIDABLE; /* a negative variance refutes the own-noise model */
    *variance = v;
    return VESUVE_OK;
}

vesuve_status vesuve_spread_standard_error(double sigma, int n, double *error)
{
    if (!error || n < 1 || sigma < 0.0) return VESUVE_BAD_ARGUMENT;
    *error = sigma / sqrt(2.0 * (double)n);
    return VESUVE_OK;
}

vesuve_status vesuve_decisive_count(double guarantee, int *count)
{
    if (!count || !(guarantee > 0.0) || !(guarantee < 1.0)) return VESUVE_BAD_ARGUMENT;
    *count = (int)ceil(9.0 * (1.0 - guarantee) / guarantee);
    return VESUVE_OK;
}

vesuve_status vesuve_block_length(int n, int *length)
{
    if (!length || n < 1) return VESUVE_BAD_ARGUMENT;
    /* pow and not cbrt: the research computes n ** (1.0 / 3.0), that is, this same pow. */
    const int b = (int)ceil(pow((double)n, 1.0 / 3.0));
    *length = b < 1 ? 1 : (b > n ? n : b);
    return VESUVE_OK;
}

vesuve_status vesuve_convergence_alpha(double e0, double e1, double n0, double n1, double *alpha)
{
    if (!alpha || !(n0 > 0.0) || !(n1 > 0.0) || e1 < 0.0) return VESUVE_BAD_ARGUMENT;
    if (n1 / n0 < 2.0) return VESUVE_UNDECIDABLE; /* a window that does not double gives no slope */
    if (!(e0 > 0.0) || !(e1 > 0.0)) return VESUVE_UNDECIDABLE;
    *alpha = log(e1 / e0) / log(n1 / n0);
    return VESUVE_OK;
}

vesuve_status vesuve_coherence(const double *increments, int n, double *coherence)
{
    if (!increments || !coherence || n < 1) return VESUVE_BAD_ARGUMENT;
    double sum = 0.0, absolute = 0.0;
    for (int i = 0; i < n; ++i) {
        sum += increments[i];
        absolute += fabs(increments[i]);
    }
    if (!(absolute > 0.0)) return VESUVE_UNDECIDABLE; /* nothing turned: neither coherent nor incoherent */
    *coherence = fabs(sum) / absolute;
    return VESUVE_OK;
}

vesuve_status vesuve_corrected_coherence(double coherence, int n, double *corrected)
{
    if (!corrected || n < 2 || coherence < 0.0 || coherence > 1.0) return VESUVE_BAD_ARGUMENT;
    const double floor_value = 1.0 / sqrt((double)n);
    const double c = (coherence - floor_value) / (1.0 - floor_value);
    *corrected = c > 0.0 ? c : 0.0;
    return VESUVE_OK;
}

vesuve_status vesuve_fresnel_number(double step_um, double distance_m, double energy_kev, double *fresnel)
{
    if (!fresnel || !(step_um > 0.0) || distance_m < 0.0 || !(energy_kev > 0.0)) return VESUVE_BAD_ARGUMENT;
    const double lambda_m = HC_KEV_M / energy_kev;
    *fresnel = sqrt(lambda_m * distance_m) * 1e6 / step_um; /* the research's order, bit for bit */
    return VESUVE_OK;
}

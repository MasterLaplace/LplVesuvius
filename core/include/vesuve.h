/*
 * vesuve.h -- the C core of the prize software.
 *
 * What this file holds: the equations the research validated, and the loops where the time goes.
 * Each function names the equation it computes and the registry fact that carries it
 * (`docs/rapports/REGISTRE_faits.tsv` on the `experimental` branch). None reads a file, opens a
 * connection or allocates beyond what the caller hands it: the core computes, the Python services
 * read and write.
 *
 * Every function returns a `vesuve_status`. A result is written only when the status is
 * `VESUVE_OK`, and `VESUVE_UNDECIDABLE` is never a disguised zero: it means "I could not".
 */
#ifndef VESUVE_H
#define VESUVE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define VESUVE_VERSION "0.2.0"

typedef enum {
    VESUVE_OK = 0,
    VESUVE_BAD_ARGUMENT = 1,      /* an input outside its domain: the caller made a mistake */
    VESUVE_UNDECIDABLE = 2,       /* the data cannot answer, and the reason is known */
    VESUVE_NOT_IMPLEMENTED = 99   /* skeleton: the function exists, its body not yet */
} vesuve_status;

/** @brief The core's version, which the Python layer compares with its own on load. */
const char *vesuve_version(void);

/** @brief A readable name for a status, for error messages. */
const char *vesuve_status_name(vesuve_status status);

/* ------------------------------------------------------------------------------------------------
 * E2 -- the scale, and B -- the budget of a sheet trace
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief The half sheet in voxels: round(step / voxel / 2).
 *
 * It is both the search range of the step and the threshold of the certificate (36 for 173 µm at
 * 2.4 µm, `que_montrent_ces_deux_vues.py:60`).
 */
vesuve_status vesuve_half_sheet_voxels(double step_um, double voxel_um, int *half);

/**
 * @brief [N5] How long a sheet trace holds: n_max = (delta / sigma)^2 seams (`R4-F340`).
 */
vesuve_status vesuve_holdable_length(double half_sheet, double sigma, double *n_max);

/**
 * @brief [N2] The spread of a mean of k rows: sqrt(sigma_s^2 + sigma_o^2 / k) (`R4-F328`).
 */
vesuve_status vesuve_spread_of_k_rows(double sigma_shared, double sigma_own, int k, double *sigma_k);

/**
 * @brief [N7] A row's own noise, from the triangle of three disagreements (`R4-F343`):
 * sigma_i^2 = (V_ij + V_ik - V_jk) / 2. A negative variance refutes the model: UNDECIDABLE.
 */
vesuve_status vesuve_triangle_own_noise(double v_ij, double v_ik, double v_jk, double *variance);

/**
 * @brief [D1] The sampling error of a spread: sigma / sqrt(2 n).
 */
vesuve_status vesuve_spread_standard_error(double sigma, int n, double *error);

/**
 * @brief [D2] The decisive count of a negative side at guarantee g: ceil(9 (1 - g) / g) (`R5-L21`).
 */
vesuve_status vesuve_decisive_count(double guarantee, int *count);

/**
 * @brief The block length of the block bootstrap: max(1, min(ceil(n^(1/3)), n)) (`R4-L22`).
 */
vesuve_status vesuve_block_length(int n, int *length);

/* ------------------------------------------------------------------------------------------------
 * E4 -- the lattice: a chunk becomes a digest, two neighbouring digests a step per seam
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief The research filter (`le_creux_borne_t_il_la_marche.py:61`, `fiber_orientation.py:66`).
 *
 * For each z layer, on the centred in-plane gradients, J = (<gx^2>, <gy^2>, <gx gy>) and the
 * coherence sqrt((Jxx - Jyy)^2 + 4 Jxy^2) / (Jxx + Jyy). The chunk is kept when at least nz / 4
 * layers exceed the floor (0.15). Block in C order [nz][ny][nx].
 *
 * @param textured_layers receives the number of layers above the floor.
 * @param kept receives 1 if the chunk passes the filter, 0 otherwise.
 */
vesuve_status vesuve_texture_filter(const uint8_t *block, int nz, int ny, int nx, double floor_value,
                                    int *textured_layers, int *kept);

/**
 * @brief A chunk's edge profiles, as integer SUMS over `width` voxels
 * (`combien_de_rangees_faut_il_pour_lire_le_pas.py:398-424`).
 *
 * For each cut row r: right[r][z] = sum of the last `width` columns of section (z, r, .),
 * left[r][z] = sum of the first. For each cut column c: bottom[c][z] = sum of the last `width` rows
 * of (z, ., c), top[c][z] = of the first. A sum divided by `width` gives exactly the research mean,
 * and fits in 16 bits. Each output has ncuts * nz cells, cut major.
 */
vesuve_status vesuve_edge_profiles(const uint8_t *block, int nz, int ny, int nx, const int *cuts,
                                   int ncuts, int width, uint16_t *right, uint16_t *left,
                                   uint16_t *bottom, uint16_t *top);

/**
 * @brief A chunk's depth profile: the mean of each layer (nz values).
 */
vesuve_status vesuve_depth_profile(const uint8_t *block, int nz, int ny, int nx, double *profile);

/**
 * @brief The step of one cut (`la_derive_saccumule_t_elle.py:99`, `un_pas`).
 *
 * a and b centred, then for each shift k from -range to +range the correlation normalised by the
 * energy of both windows; the step is -(argmax - range), the FIRST maximum on a tie. Sign: z of the
 * material in chunk b minus z of the same material in chunk a. A flat edge (zero energy) is
 * UNDECIDABLE.
 *
 * @param saturated receives 1 if |step| reaches the range: the seam may have jumped half a sheet.
 */
vesuve_status vesuve_cut_step(const double *a, const double *b, int n, int range, int *step,
                              int *saturated);

/**
 * @brief The step of one seam, averaged over its readable cuts (`le_pas_de_k_rangees`, `204`:120).
 *
 * a and b are ncuts profiles of n values; `readable[i]` says whether cut i exists on both sides.
 * The readable cuts whose step is decidable, in order, give: the step (their mean), the
 * disagreement (mean of the even ranks minus mean of the odd ranks) and their count. Fewer than two,
 * or an empty half mean: UNDECIDABLE. The values are NOT rounded: the published figures round to four
 * decimals with Python's `round`, which the Python layer applies.
 */
vesuve_status vesuve_seam_step(const double *a, const double *b, const uint8_t *readable, int ncuts,
                               int n, int range, double *step, double *disagreement, int *cuts);

/* ------------------------------------------------------------------------------------------------
 * E6 -- the certificate: NO function here, and that is measured.
 *
 * Replaying the whole hand-free procedure of `246` from its published readings takes 3.5 s in
 * Python, and its bootstrap null reproduces bit for bit only in numpy's summation order. Porting it
 * to C would buy no time and cost the parity: it lives in `vesuve/lattice/`.
 * ---------------------------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------------------------------
 * E7 -- judging without ground truth
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief [F25] The convergence test: alpha = log(e1 / e0) / log(n1 / n0) (`R3-F10`).
 * A window that does not double (n1 / n0 < 2) or a zero error at the start: UNDECIDABLE.
 */
vesuve_status vesuve_convergence_alpha(double e0, double e1, double n0, double n1, double *alpha);

/**
 * @brief [F15] The coherence of increments: |sum d_i| / sum |d_i|.
 */
vesuve_status vesuve_coherence(const double *increments, int n, double *coherence);

/**
 * @brief [F17] The coherence corrected for its noise floor 1/sqrt(n):
 * max(0, (c - 1/sqrt(n)) / (1 - 1/sqrt(n))).
 */
vesuve_status vesuve_corrected_coherence(double coherence, int n, double *corrected);

/* ------------------------------------------------------------------------------------------------
 * E8 -- rendering, and validating by the ink
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief [F31] The Fresnel number of a scan regime: F = sqrt(lambda D) / p, lambda = hc / E
 * (`src/encre/nombre_de_fresnel.py:142`, `R6-F08`).
 *
 * ⚠ It is the inverse square root of the classical Fresnel number a^2 / (lambda D), which
 * `docs/archive/151` writes by mistake: this form is the one that gives F = 0.39 for the thirteen
 * prize scrolls.
 */
vesuve_status vesuve_fresnel_number(double step_um, double distance_m, double energy_kev, double *fresnel);

/** A (score, label) pair: the sorting buffer of the area under the curve. */
typedef struct {
    double score;
    uint8_t label;
} vesuve_pair;

/**
 * @brief The area under the ROC curve, by Mann-Whitney on mid ranks (`evaluate_segment.py:72`).
 * `labels` is 0 or 1; without a positive or a negative: UNDECIDABLE. `work`: n pairs.
 */
vesuve_status vesuve_area_under_curve(const double *scores, const uint8_t *labels, size_t n,
                                      vesuve_pair *work, double *auc);

/**
 * @brief Trilinear sampling of a volume along the normals of a surface.
 *
 * For each point p and each offset d, output[d][p] = V(p + d n) interpolated; an invalid point or
 * normal (not finite) gives 0 and the cell is 0 in `valid`. Volume in C order [nz][ny][nx], points
 * and normals in (x, y, z) in the frame of the volume.
 */
vesuve_status vesuve_sample_along_normals(const uint8_t *volume, int nz, int ny, int nx, const float *points,
                                          const float *normals, size_t npoints, const float *offsets,
                                          int noffsets, float *output, uint8_t *valid);

#ifdef __cplusplus
}
#endif

#endif /* VESUVE_H */

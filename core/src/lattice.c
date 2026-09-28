/*
 * lattice.c -- E4: a chunk becomes a digest, two neighbouring digests become a step.
 *
 * This whole file reproduces the research producer of the loop chain (`src/nappe/`, slices 199, 204,
 * 222): the texture filter, the sixteen-voxel edge profiles, the correlation normalised by energy,
 * the mean of the cuts and the disagreement of even and odd ranks. Sums are done in integers where
 * that is exact, and that is what makes the digest equal to the research means bit for bit.
 */
#include <math.h>

#include "vesuve.h"

static size_t index_of(int z, int y, int x, int ny, int nx)
{
    return ((size_t)z * (size_t)ny + (size_t)y) * (size_t)nx + (size_t)x;
}

vesuve_status vesuve_texture_filter(const uint8_t *block, int nz, int ny, int nx, double floor_value,
                                    int *textured_layers, int *kept)
{
    if (!block || !textured_layers || !kept || nz < 1 || ny < 3 || nx < 3) return VESUVE_BAD_ARGUMENT;
    const double cells = (double)(ny - 2) * (double)(nx - 2);
    int above = 0;
    for (int z = 0; z < nz; ++z) {
        /* Centred gradients are differences of integers: their sums of products are exact in
           64 bits, where the research accumulates in float32. */
        int64_t sxx = 0, syy = 0, sxy = 0;
        for (int y = 1; y < ny - 1; ++y)
            for (int x = 1; x < nx - 1; ++x) {
                const int64_t gy = (int64_t)block[index_of(z, y + 1, x, ny, nx)] - block[index_of(z, y - 1, x, ny, nx)];
                const int64_t gx = (int64_t)block[index_of(z, y, x + 1, ny, nx)] - block[index_of(z, y, x - 1, ny, nx)];
                sxx += gx * gx;
                syy += gy * gy;
                sxy += gx * gy;
            }
        const double jxx = (double)sxx / cells, jyy = (double)syy / cells, jxy = (double)sxy / cells;
        const double trace = jxx + jyy;
        const double coherence =
            trace > 0.0 ? sqrt((jxx - jyy) * (jxx - jyy) + 4.0 * jxy * jxy) / trace : 0.0;
        if (coherence > floor_value) ++above;
    }
    *textured_layers = above;
    *kept = above >= nz / 4 ? 1 : 0;
    return VESUVE_OK;
}

vesuve_status vesuve_edge_profiles(const uint8_t *block, int nz, int ny, int nx, const int *cuts,
                                   int ncuts, int width, uint16_t *right, uint16_t *left,
                                   uint16_t *bottom, uint16_t *top)
{
    if (!block || !cuts || !right || !left || !bottom || !top || nz < 1 || ncuts < 1) return VESUVE_BAD_ARGUMENT;
    if (width < 1 || width > ny || width > nx || width * 255 > UINT16_MAX) return VESUVE_BAD_ARGUMENT;
    for (int i = 0; i < ncuts; ++i)
        if (cuts[i] < 0 || cuts[i] >= ny || cuts[i] >= nx) return VESUVE_BAD_ARGUMENT;
    for (int i = 0; i < ncuts; ++i) {
        const int c = cuts[i];
        for (int z = 0; z < nz; ++z) {
            unsigned r = 0, l = 0, b = 0, t = 0;
            for (int j = 0; j < width; ++j) {
                r += block[index_of(z, c, nx - width + j, ny, nx)];
                l += block[index_of(z, c, j, ny, nx)];
                b += block[index_of(z, ny - width + j, c, ny, nx)];
                t += block[index_of(z, j, c, ny, nx)];
            }
            const size_t k = (size_t)i * (size_t)nz + (size_t)z;
            right[k] = (uint16_t)r;
            left[k] = (uint16_t)l;
            bottom[k] = (uint16_t)b;
            top[k] = (uint16_t)t;
        }
    }
    return VESUVE_OK;
}

vesuve_status vesuve_depth_profile(const uint8_t *block, int nz, int ny, int nx, double *profile)
{
    if (!block || !profile || nz < 1 || ny < 1 || nx < 1) return VESUVE_BAD_ARGUMENT;
    const size_t plane = (size_t)ny * (size_t)nx;
    for (int z = 0; z < nz; ++z) {
        uint64_t sum = 0;
        const uint8_t *layer = block + (size_t)z * plane;
        for (size_t i = 0; i < plane; ++i) sum += layer[i];
        profile[z] = (double)sum / (double)plane;
    }
    return VESUVE_OK;
}

vesuve_status vesuve_cut_step(const double *a, const double *b, int n, int range, int *step, int *saturated)
{
    if (!a || !b || !step || !saturated || n < 2 || range < 1) return VESUVE_BAD_ARGUMENT;
    double ma = 0.0, mb = 0.0;
    for (int i = 0; i < n; ++i) {
        ma += a[i];
        mb += b[i];
    }
    ma /= (double)n;
    mb /= (double)n;
    double ea = 0.0, eb = 0.0;
    for (int i = 0; i < n; ++i) {
        ea += (a[i] - ma) * (a[i] - ma);
        eb += (b[i] - mb) * (b[i] - mb);
    }
    if (!(ea > 0.0) || !(eb > 0.0)) return VESUVE_UNDECIDABLE; /* a flat edge */
    const int p = range < (n - 1) / 2 ? range : (n - 1) / 2;
    if (p < 1) return VESUVE_UNDECIDABLE;

    int best = 0;
    double best_score = -INFINITY;
    for (int k = -p; k <= p; ++k) {
        const int da = k > 0 ? k : 0, db = k < 0 ? -k : 0;
        const int length = n - (k > 0 ? k : -k);
        double sab = 0.0, saa = 0.0, sbb = 0.0;
        for (int i = 0; i < length; ++i) {
            const double x = a[da + i] - ma, y = b[db + i] - mb;
            sab += x * y;
            saa += x * x;
            sbb += y * y;
        }
        const double e = saa * sbb;
        const double score = e > 0.0 ? sab / sqrt(e) : -1.0;
        if (score > best_score) { /* strict: the FIRST maximum wins, as np.argmax */
            best_score = score;
            best = k + p;
        }
    }
    *step = -(best - p);
    *saturated = (*step >= p || *step <= -p) ? 1 : 0;
    return VESUVE_OK;
}

vesuve_status vesuve_seam_step(const double *a, const double *b, const uint8_t *readable, int ncuts,
                               int n, int range, double *step, double *disagreement, int *cuts)
{
    if (!a || !b || !readable || !step || !disagreement || !cuts || ncuts < 1 || n < 2 || range < 1)
        return VESUVE_BAD_ARGUMENT;
    /* Integer steps: their sums are exact, so the means equal the research ones. */
    long sum = 0, even_sum = 0, odd_sum = 0;
    int read = 0, evens = 0, odds = 0;
    for (int i = 0; i < ncuts; ++i) {
        if (!readable[i]) continue;
        int p = 0, s = 0;
        const vesuve_status st =
            vesuve_cut_step(a + (size_t)i * (size_t)n, b + (size_t)i * (size_t)n, n, range, &p, &s);
        if (st == VESUVE_BAD_ARGUMENT) return st;
        if (st != VESUVE_OK) continue; /* a flat cut does not count, as in the research */
        sum += p;
        if (read % 2 == 0) {
            even_sum += p;
            ++evens;
        } else {
            odd_sum += p;
            ++odds;
        }
        ++read;
    }
    if (read < 2 || evens == 0 || odds == 0) return VESUVE_UNDECIDABLE;
    *step = (double)sum / (double)read;
    *disagreement = (double)even_sum / (double)evens - (double)odd_sum / (double)odds;
    *cuts = read;
    return VESUVE_OK;
}

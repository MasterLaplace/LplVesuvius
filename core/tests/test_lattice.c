/* test_lattice.c -- E4: the filter, the edges, the step of a cut and of a seam. */
#include <stdlib.h>
#include <string.h>

#include "minitest.h"
#include "vesuve.h"

enum { NZ = 109, NY = 128, NX = 128, N = 109 };

static double bump(int z, double centre)
{
    const double d = ((double)z - centre) / 4.0;
    return 100.0 * exp(-d * d);
}

static void cut_step(void)
{
    double a[N], b[N];
    for (int z = 0; z < N; ++z) {
        a[z] = bump(z, 50.0);
        b[z] = bump(z, 57.0); /* the same material, seven layers lower in chunk b */
    }
    int step = 99, saturated = 9;
    CHECK(vesuve_cut_step(a, b, N, 36, &step, &saturated) == VESUVE_OK);
    CHECK(step == 7);
    CHECK(saturated == 0);

    CHECK(vesuve_cut_step(b, a, N, 36, &step, &saturated) == VESUVE_OK);
    CHECK(step == -7); /* the sign follows the order of the two chunks */

    for (int z = 0; z < N; ++z) b[z] = bump(z, 50.0 + 40.0);
    CHECK(vesuve_cut_step(a, b, N, 36, &step, &saturated) == VESUVE_OK);
    CHECK(saturated == 1); /* 40 layers exceed the range: the seam may have jumped */

    double flat[N];
    for (int z = 0; z < N; ++z) flat[z] = 12.0;
    CHECK(vesuve_cut_step(a, flat, N, 36, &step, &saturated) == VESUVE_UNDECIDABLE);
    CHECK(vesuve_cut_step(a, b, N, 0, &step, &saturated) == VESUVE_BAD_ARGUMENT);
}

static void exact_tie(void)
{
    /* One pulse in a, two in b ten layers on either side: shifts -10 and +10 each align one pulse.
       All centred values are INTEGERS (means 1 and 2), so both scores are equal to the bit, and the
       FIRST maximum -- the most positive step, as np.argmax in the research -- must win. */
    double a[N], b[N];
    for (int z = 0; z < N; ++z) a[z] = b[z] = 0.0;
    a[54] = 109.0;
    b[44] = 109.0;
    b[64] = 109.0;
    int step = 0, saturated = 0;
    CHECK(vesuve_cut_step(a, b, N, 36, &step, &saturated) == VESUVE_OK);
    CHECK(step == 10);
}

static void seam_step(void)
{
    /* Four cuts at steps 1, 3, 1, 3: mean 2, disagreement (1 + 1) / 2 - (3 + 3) / 2 = -2. */
    enum { C = 5 };
    static double a[C * N], b[C * N];
    const int shifts[C] = {1, 3, 1, 3, 0};
    for (int c = 0; c < C; ++c)
        for (int z = 0; z < N; ++z) {
            a[c * N + z] = bump(z, 50.0);
            b[c * N + z] = bump(z, 50.0 + shifts[c]);
        }
    const uint8_t readable[C] = {1, 1, 1, 1, 0}; /* the fifth exists on one side only */
    double step = 0.0, disagreement = 0.0;
    int cuts = 0;
    CHECK(vesuve_seam_step(a, b, readable, C, N, 36, &step, &disagreement, &cuts) == VESUVE_OK);
    CHECK_CLOSE(step, 2.0, 1e-12);
    CHECK_CLOSE(disagreement, -2.0, 1e-12);
    CHECK(cuts == 4);

    const uint8_t only_one[C] = {1, 0, 0, 0, 0};
    CHECK(vesuve_seam_step(a, b, only_one, C, N, 36, &step, &disagreement, &cuts) == VESUVE_UNDECIDABLE);
}

static void edges_and_depth(void)
{
    uint8_t *block = malloc((size_t)NZ * NY * NX);
    CHECK(block != NULL);
    if (!block) return;
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                block[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)((x + y) % 256);
    const int cuts[2] = {4, 124};
    uint16_t right[2 * NZ], left[2 * NZ], bottom[2 * NZ], top[2 * NZ];
    CHECK(vesuve_edge_profiles(block, NZ, NY, NX, cuts, 2, 16, right, left, bottom, top) == VESUVE_OK);
    /* row 4: x from 112 to 127 gives (116 + ... + 131) = 1976; x from 0 to 15 gives 4*16 + 120 = 184 */
    CHECK(right[0] == 1976 && left[0] == 184);
    /* column 124: (124 + y) % 256 for y = 112..127 is 236..251, sum 3896; y = 0..15 is 124..139, 2104 */
    CHECK(bottom[1 * NZ + 5] == 3896 && top[1 * NZ + 5] == 2104);

    double profile[NZ];
    for (int z = 0; z < NZ; ++z)
        memset(block + (size_t)z * NY * NX, z, (size_t)NY * NX);
    CHECK(vesuve_depth_profile(block, NZ, NY, NX, profile) == VESUVE_OK);
    CHECK_CLOSE(profile[0], 0.0, 1e-12);
    CHECK_CLOSE(profile[77], 77.0, 1e-12);
    CHECK(vesuve_edge_profiles(block, NZ, NY, NX, cuts, 2, 0, right, left, bottom, top) == VESUVE_BAD_ARGUMENT);
    free(block);
}

static void filter(void)
{
    uint8_t *block = malloc((size_t)NZ * NY * NX);
    CHECK(block != NULL);
    if (!block) return;
    int layers = -1, kept = -1;

    /* Stripes along x: a gradient in one direction only, coherence 1. */
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                block[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(128 + 100 * sin(y / 3.0));
    CHECK(vesuve_texture_filter(block, NZ, NY, NX, 0.15, &layers, &kept) == VESUVE_OK);
    CHECK(layers == NZ && kept == 1);

    /* Noise without direction: coherence close to zero in every layer. */
    srand(20260924u);
    for (size_t i = 0; i < (size_t)NZ * NY * NX; ++i) block[i] = (uint8_t)(rand() % 256);
    CHECK(vesuve_texture_filter(block, NZ, NY, NX, 0.15, &layers, &kept) == VESUVE_OK);
    CHECK(layers == 0 && kept == 0);

    /* Exactly nz / 4 = 27 striped layers are enough, 26 are not. */
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x)
                if (z < 27)
                    block[((size_t)z * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(128 + 100 * sin(y / 3.0));
    CHECK(vesuve_texture_filter(block, NZ, NY, NX, 0.15, &layers, &kept) == VESUVE_OK);
    CHECK(layers == 27 && kept == 1);
    for (int y = 0; y < NY; ++y)
        for (int x = 0; x < NX; ++x) block[((size_t)26 * NY + (size_t)y) * NX + (size_t)x] = (uint8_t)(rand() % 256);
    CHECK(vesuve_texture_filter(block, NZ, NY, NX, 0.15, &layers, &kept) == VESUVE_OK);
    CHECK(layers == 26 && kept == 0);

    /* A uniform block has no gradient: no layer is textured, with no division by zero. */
    memset(block, 7, (size_t)NZ * NY * NX);
    CHECK(vesuve_texture_filter(block, NZ, NY, NX, 0.15, &layers, &kept) == VESUVE_OK);
    CHECK(layers == 0 && kept == 0);
    free(block);
}

int main(void)
{
    cut_step();
    exact_tie();
    seam_step();
    edges_and_depth();
    filter();
    FINISH("test_lattice");
}

/* test_formulary.c -- the closed-form equations, against values computed separately. */
#include "minitest.h"
#include "vesuve.h"

static void scale_and_budget(void)
{
    int half = -1;
    CHECK(vesuve_half_sheet_voxels(173.0, 2.4, &half) == VESUVE_OK);
    CHECK(half == 36); /* 173 / 2.4 = 72.08; the rounded half is 36 */
    CHECK(vesuve_half_sheet_voxels(173.0, 0.0, &half) == VESUVE_BAD_ARGUMENT);

    double n = 0.0;
    CHECK(vesuve_holdable_length(36.0, 3.4004, &n) == VESUVE_OK);
    CHECK_CLOSE(n, 112.08, 0.005); /* R4-F341, the worst pair of rows */
    CHECK(vesuve_holdable_length(36.0, 0.0, &n) == VESUVE_BAD_ARGUMENT);

    double s = 0.0;
    CHECK(vesuve_spread_of_k_rows(1.0, 2.0, 4, &s) == VESUVE_OK);
    CHECK_CLOSE(s, sqrt(2.0), 1e-12);
    CHECK(vesuve_spread_of_k_rows(1.0, 2.0, 0, &s) == VESUVE_BAD_ARGUMENT);

    double v = 0.0;
    CHECK(vesuve_triangle_own_noise(5.0, 4.0, 3.0, &v) == VESUVE_OK);
    CHECK_CLOSE(v, 3.0, 1e-12);
    CHECK(vesuve_triangle_own_noise(1.0, 1.0, 5.0, &v) == VESUVE_UNDECIDABLE);
}

static void decision(void)
{
    double e = 0.0;
    CHECK(vesuve_spread_standard_error(1.0, 50, &e) == VESUVE_OK);
    CHECK_CLOSE(e, 0.1, 1e-12);
    CHECK(vesuve_spread_standard_error(1.0, 0, &e) == VESUVE_BAD_ARGUMENT);

    int m = 0;
    CHECK(vesuve_decisive_count(0.05, &m) == VESUVE_OK);
    CHECK(m == 171); /* the research's LE_COMPTE_DECISIF */
    CHECK(vesuve_decisive_count(0.0, &m) == VESUVE_BAD_ARGUMENT);

    int b = 0;
    CHECK(vesuve_block_length(1000, &b) == VESUVE_OK && b == 10);
    CHECK(vesuve_block_length(28, &b) == VESUVE_OK && b == 4);
    CHECK(vesuve_block_length(1, &b) == VESUVE_OK && b == 1);
    /* Parity with the research on n = 1..10000 is checked against ITS function, in Python: a value of
       n^(1/3) recited from memory would be a decoy, not an oracle. */
    CHECK(vesuve_block_length(0, &b) == VESUVE_BAD_ARGUMENT);
}

static void judge(void)
{
    double a = -9.0;
    CHECK(vesuve_convergence_alpha(10.0, 20.0, 31.0, 62.0, &a) == VESUVE_OK);
    CHECK_CLOSE(a, 1.0, 1e-12); /* the error follows the window */
    CHECK(vesuve_convergence_alpha(10.0, 10.0, 31.0, 81.0, &a) == VESUVE_OK);
    CHECK_CLOSE(a, 0.0, 1e-12); /* it converges */
    CHECK(vesuve_convergence_alpha(10.0, 20.0, 31.0, 41.0, &a) == VESUVE_UNDECIDABLE);
    CHECK(vesuve_convergence_alpha(0.0, 20.0, 31.0, 81.0, &a) == VESUVE_UNDECIDABLE);

    const double turning[] = {1.0, 1.0, 1.0, 1.0};
    const double alternating[] = {1.0, -1.0, 1.0, -1.0};
    double c = -1.0;
    CHECK(vesuve_coherence(turning, 4, &c) == VESUVE_OK);
    CHECK_CLOSE(c, 1.0, 1e-12);
    CHECK(vesuve_coherence(alternating, 4, &c) == VESUVE_OK);
    CHECK_CLOSE(c, 0.0, 1e-12);
    const double zeros[] = {0.0, 0.0};
    CHECK(vesuve_coherence(zeros, 2, &c) == VESUVE_UNDECIDABLE);

    double k = -1.0;
    CHECK(vesuve_corrected_coherence(0.5, 4, &k) == VESUVE_OK);
    CHECK_CLOSE(k, 0.0, 1e-12); /* 1 / sqrt(4): exactly the noise floor */
    CHECK(vesuve_corrected_coherence(1.0, 4, &k) == VESUVE_OK);
    CHECK_CLOSE(k, 1.0, 1e-12);
    CHECK(vesuve_corrected_coherence(0.2, 64, &k) == VESUVE_OK);
    CHECK_CLOSE(k, (0.2 - 0.125) / 0.875, 1e-12);
}

static void fresnel(void)
{
    double f = 0.0;
    CHECK(vesuve_fresnel_number(9.362, 1.2, 113.0, &f) == VESUVE_OK);
    /* lambda = 1.23984193e-9 / 113 m; sqrt(lambda * 1.2) / 9.362e-6, computed by hand */
    CHECK_CLOSE(f, 0.38758, 0.00005);
    CHECK(vesuve_fresnel_number(2.4, 0.2, 78.0, &f) == VESUVE_OK);
    CHECK_CLOSE(f, 0.74292, 0.00005);
    CHECK(vesuve_fresnel_number(9.362, 1.2, 0.0, &f) == VESUVE_BAD_ARGUMENT);
    CHECK(vesuve_fresnel_number(0.0, 1.2, 113.0, &f) == VESUVE_BAD_ARGUMENT);
}

int main(void)
{
    scale_and_budget();
    decision();
    judge();
    fresnel();
    FINISH("test_formulary");
}

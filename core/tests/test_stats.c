/* test_stats.c -- the area under the curve, and its two edges. */
#include "minitest.h"
#include "vesuve.h"

int main(void)
{
    vesuve_pair work[16];
    double auc = -1.0;

    const double perfect[] = {0.1, 0.2, 0.8, 0.9};
    const uint8_t labels[] = {0, 0, 1, 1};
    CHECK(vesuve_area_under_curve(perfect, labels, 4, work, &auc) == VESUVE_OK);
    CHECK_CLOSE(auc, 1.0, 1e-12);

    const double inverse[] = {0.9, 0.8, 0.2, 0.1};
    CHECK(vesuve_area_under_curve(inverse, labels, 4, work, &auc) == VESUVE_OK);
    CHECK_CLOSE(auc, 0.0, 1e-12);

    /* All tied: mid ranks, so exactly chance. */
    const double equal[] = {0.5, 0.5, 0.5, 0.5};
    CHECK(vesuve_area_under_curve(equal, labels, 4, work, &auc) == VESUVE_OK);
    CHECK_CLOSE(auc, 0.5, 1e-12);

    /* A case by hand: positives 0.4 and 0.7 against negatives 0.1, 0.4, 0.9.
       Pairs won: (0.4 > 0.1) + 0.5 (0.4 = 0.4) + (0.7 > 0.1) + (0.7 > 0.4) = 3.5 out of 6. */
    const double mixed[] = {0.1, 0.4, 0.9, 0.4, 0.7};
    const uint8_t l2[] = {0, 0, 0, 1, 1};
    CHECK(vesuve_area_under_curve(mixed, l2, 5, work, &auc) == VESUVE_OK);
    CHECK_CLOSE(auc, 3.5 / 6.0, 1e-12);

    const uint8_t no_positive[] = {0, 0, 0, 0};
    CHECK(vesuve_area_under_curve(perfect, no_positive, 4, work, &auc) == VESUVE_UNDECIDABLE);
    FINISH("test_stats");
}

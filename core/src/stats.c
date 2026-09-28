/* stats.c -- the validation statistics: the area under the curve on mid ranks. */
#include <stdlib.h>

#include "vesuve.h"

static int by_score(const void *left, const void *right)
{
    const double a = ((const vesuve_pair *)left)->score, b = ((const vesuve_pair *)right)->score;
    return (a > b) - (a < b);
}

vesuve_status vesuve_area_under_curve(const double *scores, const uint8_t *labels, size_t n,
                                      vesuve_pair *work, double *auc)
{
    if (!scores || !labels || !work || !auc || n == 0) return VESUVE_BAD_ARGUMENT;
    size_t positives = 0;
    for (size_t i = 0; i < n; ++i) {
        work[i].score = scores[i];
        work[i].label = labels[i] ? 1u : 0u;
        positives += work[i].label;
    }
    const size_t negatives = n - positives;
    if (positives == 0 || negatives == 0) return VESUVE_UNDECIDABLE;
    qsort(work, n, sizeof *work, by_score);
    /* A group of ties occupying [start, end) gets the mid rank (start + end + 1) / 2. */
    double rank_sum = 0.0;
    for (size_t start = 0; start < n;) {
        size_t end = start + 1;
        while (end < n && work[end].score == work[start].score) ++end;
        const double rank = ((double)start + (double)end + 1.0) / 2.0;
        for (size_t i = start; i < end; ++i)
            if (work[i].label) rank_sum += rank;
        start = end;
    }
    const double p = (double)positives, q = (double)negatives;
    *auc = (rank_sum - p * (p + 1.0) / 2.0) / (p * q);
    return VESUVE_OK;
}

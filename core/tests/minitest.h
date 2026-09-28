/*
 * minitest.h -- the smallest harness that makes a test fail for real.
 *
 * Every check is counted, a failure prints its file, its line and what was expected, and `FINISH()`
 * returns 1 if a check failed OR if no check ran: an empty battery is not a green battery.
 */
#ifndef MINITEST_H
#define MINITEST_H

#include <math.h>
#include <stdio.h>

static int minitest_checks = 0;
static int minitest_failures = 0;

#define CHECK(condition)                                                                           \
    do {                                                                                           \
        ++minitest_checks;                                                                         \
        if (!(condition)) {                                                                        \
            ++minitest_failures;                                                                   \
            fprintf(stderr, "  FAIL %s:%d: %s\n", __FILE__, __LINE__, #condition);                 \
        }                                                                                          \
    } while (0)

#define CHECK_CLOSE(got, expected, tolerance)                                                      \
    do {                                                                                           \
        double minitest_g_ = (double)(got), minitest_e_ = (double)(expected);                      \
        ++minitest_checks;                                                                         \
        if (!(fabs(minitest_g_ - minitest_e_) <= (double)(tolerance))) {                            \
            ++minitest_failures;                                                                   \
            fprintf(stderr, "  FAIL %s:%d: %s = %.10g, expected %.10g (tolerance %g)\n",            \
                    __FILE__, __LINE__, #got, minitest_g_, minitest_e_, (double)(tolerance));      \
        }                                                                                          \
    } while (0)

#define FINISH(name)                                                                               \
    do {                                                                                           \
        if (minitest_checks == 0) {                                                                \
            fprintf(stderr, "%s: NO check ran\n", name);                                           \
            return 1;                                                                              \
        }                                                                                          \
        fprintf(stderr, "%s: %d checks, %d failures\n", name, minitest_checks, minitest_failures); \
        return minitest_failures ? 1 : 0;                                                          \
    } while (0)

#endif /* MINITEST_H */

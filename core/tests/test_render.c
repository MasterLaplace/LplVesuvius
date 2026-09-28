/* test_render.c -- sampling along normals, on a volume whose value is known everywhere. */
#include <stdlib.h>

#include "minitest.h"
#include "vesuve.h"

enum { NZ = 20, NY = 16, NX = 12 };

int main(void)
{
    /* V = x + 2y + 3z is linear: trilinear interpolation returns it EXACTLY. */
    uint8_t volume[NZ * NY * NX];
    for (int z = 0; z < NZ; ++z)
        for (int y = 0; y < NY; ++y)
            for (int x = 0; x < NX; ++x) volume[(z * NY + y) * NX + x] = (uint8_t)(x + 2 * y + 3 * z);

    const float points[] = {4.5f, 6.25f, 8.0f,    /* an interior point */
                            1.0f, 1.0f, 1.0f,     /* a point whose normal leaves the volume */
                            -1.0f, -1.0f, -1.0f}; /* an invalid point, the tifxyz sentinel */
    const float normals[] = {0.0f, 0.0f, 1.0f, 0.0f, 0.0f, -1.0f, 0.0f, 0.0f, 1.0f};
    const float offsets[] = {-2.0f, 0.0f, 1.5f};
    float output[3 * 3];
    uint8_t valid[3 * 3];
    CHECK(vesuve_sample_along_normals(volume, NZ, NY, NX, points, normals, 3, offsets, 3, output, valid) ==
          VESUVE_OK);
    /* point 0: x + 2y + 3z = 4.5 + 12.5 + 3 (8 + d) */
    CHECK(valid[0 * 3 + 0] == 1);
    CHECK_CLOSE(output[0 * 3 + 0], 4.5 + 12.5 + 3.0 * 6.0, 1e-4);
    CHECK_CLOSE(output[1 * 3 + 0], 4.5 + 12.5 + 3.0 * 8.0, 1e-4);
    CHECK_CLOSE(output[2 * 3 + 0], 4.5 + 12.5 + 3.0 * 9.5, 1e-4);
    /* point 1: z = 1 - d; d = 1.5 gives z = -0.5, outside the volume, so invalid */
    CHECK(valid[0 * 3 + 1] == 1 && valid[2 * 3 + 1] == 0);
    CHECK_CLOSE(output[0 * 3 + 1], 1.0 + 2.0 + 3.0 * 3.0, 1e-4);
    /* point 2: the -1 sentinel is never rendered */
    CHECK(valid[1 * 3 + 2] == 0 && output[1 * 3 + 2] == 0.0f);

    CHECK(vesuve_sample_along_normals(volume, NZ, NY, NX, points, normals, 3, offsets, 0, output, valid) ==
          VESUVE_BAD_ARGUMENT);
    FINISH("test_render");
}

/* rendu.c -- E8 : échantillonner un volume le long des normales d'une surface. */
#include <math.h>

#include "vesuve.h"

static float voxel(const uint8_t *v, int ny, int nx, int z, int y, int x)
{
    return (float)v[((size_t)z * (size_t)ny + (size_t)y) * (size_t)nx + (size_t)x];
}

/* L'interpolation trilinéaire en q, supposé dans [0, n - 1] sur chaque axe. */
static float trilineaire(const uint8_t *v, int nz, int ny, int nx, float qx, float qy, float qz)
{
    const int x0 = (int)floorf(qx), y0 = (int)floorf(qy), z0 = (int)floorf(qz);
    const int x1 = x0 + 1 < nx ? x0 + 1 : x0, y1 = y0 + 1 < ny ? y0 + 1 : y0, z1 = z0 + 1 < nz ? z0 + 1 : z0;
    const float fx = qx - (float)x0, fy = qy - (float)y0, fz = qz - (float)z0;
    const float c00 = voxel(v, ny, nx, z0, y0, x0) * (1.0f - fx) + voxel(v, ny, nx, z0, y0, x1) * fx;
    const float c01 = voxel(v, ny, nx, z0, y1, x0) * (1.0f - fx) + voxel(v, ny, nx, z0, y1, x1) * fx;
    const float c10 = voxel(v, ny, nx, z1, y0, x0) * (1.0f - fx) + voxel(v, ny, nx, z1, y0, x1) * fx;
    const float c11 = voxel(v, ny, nx, z1, y1, x0) * (1.0f - fx) + voxel(v, ny, nx, z1, y1, x1) * fx;
    const float c0 = c00 * (1.0f - fy) + c01 * fy, c1 = c10 * (1.0f - fy) + c11 * fy;
    return c0 * (1.0f - fz) + c1 * fz;
}

vesuve_statut vesuve_echantillonner_le_long_des_normales(const uint8_t *volume, int nz, int ny, int nx,
                                                         const float *points, const float *normales,
                                                         size_t npoints, const float *decalages,
                                                         int ndecalages, float *sortie, uint8_t *valide)
{
    if (!volume || !points || !normales || !decalages || !sortie || !valide || nz < 1 || ny < 1 || nx < 1 ||
        ndecalages < 1)
        return VESUVE_ARGUMENT;
    const float mx = (float)(nx - 1), my = (float)(ny - 1), mz = (float)(nz - 1);
    for (int d = 0; d < ndecalages; ++d) {
        const float t = decalages[d];
        for (size_t p = 0; p < npoints; ++p) {
            const float *q = points + 3 * p, *m = normales + 3 * p;
            const float qx = q[0] + t * m[0], qy = q[1] + t * m[1], qz = q[2] + t * m[2];
            const size_t k = (size_t)d * npoints + p;
            const int dedans = isfinite(qx) && isfinite(qy) && isfinite(qz) && qx >= 0.0f && qx <= mx &&
                               qy >= 0.0f && qy <= my && qz >= 0.0f && qz <= mz;
            valide[k] = dedans ? 1u : 0u;
            sortie[k] = dedans ? trilineaire(volume, nz, ny, nx, qx, qy, qz) : 0.0f;
        }
    }
    return VESUVE_OK;
}

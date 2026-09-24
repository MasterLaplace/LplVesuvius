/*
 * treillis.c -- E4 : un chunk devient un digest, deux digests voisins deviennent un pas.
 *
 * Tout ce fichier reproduit le producteur de la chaîne des boucles (`src/nappe/`, tranches 199, 204,
 * 222) : le filtre de texture, les profils de bord de seize voxels, la corrélation normalisée par
 * l'énergie, la moyenne des coupes et le désaccord des rangs pairs et impairs. Les sommes se font en
 * entiers là où c'est exact, et c'est ce qui rend le digest bit pour bit égal aux moyennes du
 * producteur.
 */
#include <math.h>

#include "vesuve.h"

static size_t indice(int z, int y, int x, int ny, int nx)
{
    return ((size_t)z * (size_t)ny + (size_t)y) * (size_t)nx + (size_t)x;
}

vesuve_statut vesuve_filtre_de_texture(const uint8_t *bloc, int nz, int ny, int nx, double plancher,
                                       int *couches_texturees, int *retenu)
{
    if (!bloc || !couches_texturees || !retenu || nz < 1 || ny < 3 || nx < 3) return VESUVE_ARGUMENT;
    const double cases = (double)(ny - 2) * (double)(nx - 2);
    int au_dessus = 0;
    for (int z = 0; z < nz; ++z) {
        /* Les gradients centrés sont des différences d'entiers : leurs sommes de produits sont
           exactes en 64 bits, là où le producteur accumule en float32. */
        int64_t sxx = 0, syy = 0, sxy = 0;
        for (int y = 1; y < ny - 1; ++y)
            for (int x = 1; x < nx - 1; ++x) {
                const int64_t gy = (int64_t)bloc[indice(z, y + 1, x, ny, nx)] - bloc[indice(z, y - 1, x, ny, nx)];
                const int64_t gx = (int64_t)bloc[indice(z, y, x + 1, ny, nx)] - bloc[indice(z, y, x - 1, ny, nx)];
                sxx += gx * gx;
                syy += gy * gy;
                sxy += gx * gy;
            }
        const double jxx = (double)sxx / cases, jyy = (double)syy / cases, jxy = (double)sxy / cases;
        const double trace = jxx + jyy;
        const double coherence =
            trace > 0.0 ? sqrt((jxx - jyy) * (jxx - jyy) + 4.0 * jxy * jxy) / trace : 0.0;
        if (coherence > plancher) ++au_dessus;
    }
    *couches_texturees = au_dessus;
    *retenu = au_dessus >= nz / 4 ? 1 : 0;
    return VESUVE_OK;
}

vesuve_statut vesuve_profils_de_bord(const uint8_t *bloc, int nz, int ny, int nx, const int *coupes,
                                     int ncoupes, int largeur, uint16_t *droit, uint16_t *gauche,
                                     uint16_t *bas, uint16_t *haut)
{
    if (!bloc || !coupes || !droit || !gauche || !bas || !haut || nz < 1 || ncoupes < 1) return VESUVE_ARGUMENT;
    if (largeur < 1 || largeur > ny || largeur > nx || largeur * 255 > UINT16_MAX) return VESUVE_ARGUMENT;
    for (int i = 0; i < ncoupes; ++i)
        if (coupes[i] < 0 || coupes[i] >= ny || coupes[i] >= nx) return VESUVE_ARGUMENT;
    for (int i = 0; i < ncoupes; ++i) {
        const int c = coupes[i];
        for (int z = 0; z < nz; ++z) {
            unsigned d = 0, g = 0, b = 0, h = 0;
            for (int j = 0; j < largeur; ++j) {
                d += bloc[indice(z, c, nx - largeur + j, ny, nx)];
                g += bloc[indice(z, c, j, ny, nx)];
                b += bloc[indice(z, ny - largeur + j, c, ny, nx)];
                h += bloc[indice(z, j, c, ny, nx)];
            }
            const size_t k = (size_t)i * (size_t)nz + (size_t)z;
            droit[k] = (uint16_t)d;
            gauche[k] = (uint16_t)g;
            bas[k] = (uint16_t)b;
            haut[k] = (uint16_t)h;
        }
    }
    return VESUVE_OK;
}

vesuve_statut vesuve_profil_de_profondeur(const uint8_t *bloc, int nz, int ny, int nx, double *profil)
{
    if (!bloc || !profil || nz < 1 || ny < 1 || nx < 1) return VESUVE_ARGUMENT;
    const size_t plan = (size_t)ny * (size_t)nx;
    for (int z = 0; z < nz; ++z) {
        uint64_t somme = 0;
        const uint8_t *couche = bloc + (size_t)z * plan;
        for (size_t i = 0; i < plan; ++i) somme += couche[i];
        profil[z] = (double)somme / (double)plan;
    }
    return VESUVE_OK;
}

vesuve_statut vesuve_pas_dune_coupe(const double *a, const double *b, int n, int plage, int *pas,
                                    int *sature)
{
    if (!a || !b || !pas || !sature || n < 2 || plage < 1) return VESUVE_ARGUMENT;
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
    if (!(ea > 0.0) || !(eb > 0.0)) return VESUVE_INDECIDABLE; /* un bord plat */
    const int p = plage < (n - 1) / 2 ? plage : (n - 1) / 2;
    if (p < 1) return VESUVE_INDECIDABLE;

    int meilleur = 0;
    double score_max = -INFINITY;
    for (int k = -p; k <= p; ++k) {
        const int da = k > 0 ? k : 0, db = k < 0 ? -k : 0;
        const int longueur = n - (k > 0 ? k : -k);
        double sab = 0.0, saa = 0.0, sbb = 0.0;
        for (int i = 0; i < longueur; ++i) {
            const double x = a[da + i] - ma, y = b[db + i] - mb;
            sab += x * y;
            saa += x * x;
            sbb += y * y;
        }
        const double e = saa * sbb;
        const double score = e > 0.0 ? sab / sqrt(e) : -1.0;
        if (score > score_max) { /* strict : le PREMIER maximum gagne, comme np.argmax */
            score_max = score;
            meilleur = k + p;
        }
    }
    *pas = -(meilleur - p);
    *sature = (*pas >= p || *pas <= -p) ? 1 : 0;
    return VESUVE_OK;
}

vesuve_statut vesuve_pas_dune_couture(const double *a, const double *b, const uint8_t *lisible,
                                      int ncoupes, int n, int plage, double *pas, double *desaccord,
                                      int *coupes)
{
    if (!a || !b || !lisible || !pas || !desaccord || !coupes || ncoupes < 1 || n < 2 || plage < 1)
        return VESUVE_ARGUMENT;
    /* Des pas entiers : leurs sommes sont exactes, donc les moyennes égalent celles du producteur. */
    long somme = 0, somme_paire = 0, somme_impaire = 0;
    int lus = 0, pairs = 0, impairs = 0;
    for (int i = 0; i < ncoupes; ++i) {
        if (!lisible[i]) continue;
        int p = 0, s = 0;
        const vesuve_statut st =
            vesuve_pas_dune_coupe(a + (size_t)i * (size_t)n, b + (size_t)i * (size_t)n, n, plage, &p, &s);
        if (st == VESUVE_ARGUMENT) return st;
        if (st != VESUVE_OK) continue; /* une coupe plate ne compte pas, comme chez le producteur */
        somme += p;
        if (lus % 2 == 0) {
            somme_paire += p;
            ++pairs;
        } else {
            somme_impaire += p;
            ++impairs;
        }
        ++lus;
    }
    if (lus < 2 || pairs == 0 || impairs == 0) return VESUVE_INDECIDABLE;
    *pas = (double)somme / (double)lus;
    *desaccord = (double)somme_paire / (double)pairs - (double)somme_impaire / (double)impairs;
    *coupes = lus;
    return VESUVE_OK;
}

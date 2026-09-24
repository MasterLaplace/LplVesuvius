/* test_formulaire.c -- les équations fermées, contre des valeurs calculées à part. */
#include "minitest.h"
#include "vesuve.h"

static void echelle_et_budget(void)
{
    int demi = -1;
    VERIFIER(vesuve_demi_feuillet_voxels(173.0, 2.4, &demi) == VESUVE_OK);
    VERIFIER(demi == 36); /* 173 / 2,4 = 72,08 ; la moitié arrondie vaut 36 */
    VERIFIER(vesuve_demi_feuillet_voxels(173.0, 0.0, &demi) == VESUVE_ARGUMENT);

    double n = 0.0;
    VERIFIER(vesuve_longueur_tenable(36.0, 3.4004, &n) == VESUVE_OK);
    VERIFIER_PROCHE(n, 112.08, 0.005); /* R4-F341, la pire paire de rangées */
    VERIFIER(vesuve_longueur_tenable(36.0, 0.0, &n) == VESUVE_ARGUMENT);

    double s = 0.0;
    VERIFIER(vesuve_dispersion_de_k_rangees(1.0, 2.0, 4, &s) == VESUVE_OK);
    VERIFIER_PROCHE(s, sqrt(2.0), 1e-12);
    VERIFIER(vesuve_dispersion_de_k_rangees(1.0, 2.0, 0, &s) == VESUVE_ARGUMENT);

    double v = 0.0;
    VERIFIER(vesuve_bruit_propre_du_triangle(5.0, 4.0, 3.0, &v) == VESUVE_OK);
    VERIFIER_PROCHE(v, 3.0, 1e-12);
    VERIFIER(vesuve_bruit_propre_du_triangle(1.0, 1.0, 5.0, &v) == VESUVE_INDECIDABLE);
}

static void decision(void)
{
    double e = 0.0;
    VERIFIER(vesuve_erreur_dune_dispersion(1.0, 50, &e) == VESUVE_OK);
    VERIFIER_PROCHE(e, 0.1, 1e-12);
    VERIFIER(vesuve_erreur_dune_dispersion(1.0, 0, &e) == VESUVE_ARGUMENT);

    int m = 0;
    VERIFIER(vesuve_compte_decisif(0.05, &m) == VESUVE_OK);
    VERIFIER(m == 171); /* LE_COMPTE_DECISIF du dépôt */
    VERIFIER(vesuve_compte_decisif(0.0, &m) == VESUVE_ARGUMENT);

    int b = 0;
    VERIFIER(vesuve_longueur_de_bloc(1000, &b) == VESUVE_OK && b == 10);
    VERIFIER(vesuve_longueur_de_bloc(28, &b) == VESUVE_OK && b == 4);
    VERIFIER(vesuve_longueur_de_bloc(1, &b) == VESUVE_OK && b == 1);
    /* La parité avec le producteur sur n = 1..10000 est vérifiée contre SA fonction, en Python :
       une valeur de n^(1/3) récitée de mémoire serait un leurre, pas un oracle. */
    VERIFIER(vesuve_longueur_de_bloc(0, &b) == VESUVE_ARGUMENT);
}

static void juge(void)
{
    double a = -9.0;
    VERIFIER(vesuve_alpha_de_convergence(10.0, 20.0, 31.0, 62.0, &a) == VESUVE_OK);
    VERIFIER_PROCHE(a, 1.0, 1e-12); /* l'écart suit la fenêtre */
    VERIFIER(vesuve_alpha_de_convergence(10.0, 10.0, 31.0, 81.0, &a) == VESUVE_OK);
    VERIFIER_PROCHE(a, 0.0, 1e-12); /* il converge */
    VERIFIER(vesuve_alpha_de_convergence(10.0, 20.0, 31.0, 41.0, &a) == VESUVE_INDECIDABLE);
    VERIFIER(vesuve_alpha_de_convergence(0.0, 20.0, 31.0, 81.0, &a) == VESUVE_INDECIDABLE);

    const double tourne[] = {1.0, 1.0, 1.0, 1.0};
    const double alterne[] = {1.0, -1.0, 1.0, -1.0};
    double c = -1.0;
    VERIFIER(vesuve_coherence(tourne, 4, &c) == VESUVE_OK);
    VERIFIER_PROCHE(c, 1.0, 1e-12);
    VERIFIER(vesuve_coherence(alterne, 4, &c) == VESUVE_OK);
    VERIFIER_PROCHE(c, 0.0, 1e-12);
    const double nuls[] = {0.0, 0.0};
    VERIFIER(vesuve_coherence(nuls, 2, &c) == VESUVE_INDECIDABLE);

    double k = -1.0;
    VERIFIER(vesuve_coherence_corrigee(0.5, 4, &k) == VESUVE_OK);
    VERIFIER_PROCHE(k, 0.0, 1e-12); /* 1 / sqrt(4) : exactement le plancher du bruit */
    VERIFIER(vesuve_coherence_corrigee(1.0, 4, &k) == VESUVE_OK);
    VERIFIER_PROCHE(k, 1.0, 1e-12);
    VERIFIER(vesuve_coherence_corrigee(0.2, 64, &k) == VESUVE_OK);
    VERIFIER_PROCHE(k, (0.2 - 0.125) / 0.875, 1e-12);
}

static void fresnel(void)
{
    double f = 0.0;
    VERIFIER(vesuve_nombre_de_fresnel(9.362, 1.2, 113.0, &f) == VESUVE_OK);
    /* lambda = 1,23984193e-9 / 113 m ; sqrt(lambda * 1,2) / 9,362e-6, calculé à la main */
    VERIFIER_PROCHE(f, 0.38758, 0.00005);
    VERIFIER(vesuve_nombre_de_fresnel(2.4, 0.2, 78.0, &f) == VESUVE_OK);
    VERIFIER_PROCHE(f, 0.74292, 0.00005);
    VERIFIER(vesuve_nombre_de_fresnel(9.362, 1.2, 0.0, &f) == VESUVE_ARGUMENT);
    VERIFIER(vesuve_nombre_de_fresnel(0.0, 1.2, 113.0, &f) == VESUVE_ARGUMENT);
}

int main(void)
{
    echelle_et_budget();
    decision();
    juge();
    fresnel();
    FIN("test_formulaire");
}

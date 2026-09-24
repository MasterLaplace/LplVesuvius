/*
 * vesuve.h -- le noyau C du logiciel des prix.
 *
 * Ce que ce fichier contient : les équations que le dépôt a validées, et les boucles où le temps part.
 * Chaque fonction nomme l'équation qu'elle calcule et le fait du registre qui la porte
 * (`docs/rapports/REGISTRE_faits.tsv`). Aucune ne lit un fichier, n'ouvre une connexion ni n'alloue
 * au-delà de ce que l'appelant lui donne : le noyau calcule, les services Python lisent et écrivent.
 *
 * Toutes les fonctions rendent un `vesuve_statut`. Un résultat n'est écrit que si le statut vaut
 * `VESUVE_OK`, et `VESUVE_INDECIDABLE` n'est jamais un zéro déguisé : c'est « je n'ai pas pu ».
 */
#ifndef VESUVE_H
#define VESUVE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define VESUVE_VERSION "0.1.0"

typedef enum {
    VESUVE_OK = 0,
    VESUVE_ARGUMENT = 1,       /* une entrée hors de son domaine : l'appelant s'est trompé */
    VESUVE_INDECIDABLE = 2,    /* les données ne permettent pas de répondre, et la raison est connue */
    VESUVE_NON_IMPLEMENTE = 99 /* ossature : la fonction existe, son corps pas encore (V-001) */
} vesuve_statut;

/** @brief La version du noyau, que la couche Python compare à la sienne au chargement. */
const char *vesuve_version(void);

/** @brief Un nom lisible pour un statut, pour les messages d'erreur. */
const char *vesuve_nom_du_statut(vesuve_statut statut);

/* ------------------------------------------------------------------------------------------------
 * E2 -- l'échelle, et B -- le budget de la nappe
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief Le demi-feuillet en voxels : round(pas / voxel / 2).
 *
 * C'est à la fois la plage de recalage du pas et le seuil du certificat (36 pour 173 µm à 2,4 µm,
 * `que_montrent_ces_deux_vues.py:60`).
 */
vesuve_statut vesuve_demi_feuillet_voxels(double pas_um, double voxel_um, int *demi);

/**
 * @brief [N5] La longueur tenable d'une nappe : n_max = (delta / sigma)^2 coutures (`R4-F340`).
 */
vesuve_statut vesuve_longueur_tenable(double demi_feuillet, double sigma, double *n_max);

/**
 * @brief [N2] La dispersion d'une moyenne de k rangées : sqrt(sigma_p^2 + sigma_b^2 / k) (`R4-F328`).
 */
vesuve_statut vesuve_dispersion_de_k_rangees(double sigma_partage, double sigma_propre, int k,
                                             double *sigma_k);

/**
 * @brief [N7] Le bruit propre d'une rangée tiré du triangle de trois désaccords (`R4-F343`) :
 * sigma_i^2 = (V_ij + V_ik - V_jk) / 2. Une variance négative réfute le modèle : INDECIDABLE.
 */
vesuve_statut vesuve_bruit_propre_du_triangle(double v_ij, double v_ik, double v_jk, double *variance);

/**
 * @brief [D1] L'erreur d'échantillonnage d'une dispersion : sigma / sqrt(2 n).
 */
vesuve_statut vesuve_erreur_dune_dispersion(double sigma, int n, double *erreur);

/**
 * @brief [D2] Le compte décisif d'une face négative à la garantie g : ceil(9 (1 - g) / g) (`R5-L21`).
 */
vesuve_statut vesuve_compte_decisif(double garantie, int *compte);

/**
 * @brief La longueur de bloc du bootstrap par blocs : max(1, min(ceil(n^(1/3)), n)) (`R4-L22`).
 */
vesuve_statut vesuve_longueur_de_bloc(int n, int *longueur);

/* ------------------------------------------------------------------------------------------------
 * E4 -- le treillis : un chunk devient un digest, deux digests voisins un pas par couture
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief Le filtre du producteur (`le_creux_borne_t_il_la_marche.py:61`, `fiber_orientation.py:66`).
 *
 * Par couche z, sur les gradients centrés dans le plan, J = (<gx^2>, <gy^2>, <gx gy>) et la
 * cohérence sqrt((Jxx - Jyy)^2 + 4 Jxy^2) / (Jxx + Jyy). Le chunk est retenu quand au moins
 * nz / 4 couches dépassent le plancher (0,15). Bloc en ordre C [nz][ny][nx].
 *
 * @param couches_texturees reçoit le nombre de couches au-dessus du plancher.
 * @param retenu reçoit 1 si le chunk passe le filtre, 0 sinon.
 */
vesuve_statut vesuve_filtre_de_texture(const uint8_t *bloc, int nz, int ny, int nx, double plancher,
                                       int *couches_texturees, int *retenu);

/**
 * @brief Les profils de bord d'un chunk, en SOMMES entières de `largeur` voxels
 * (`combien_de_rangees_faut_il_pour_lire_le_pas.py:398-424`).
 *
 * Pour chaque rangée de coupe r : droit[r][z] = somme des `largeur` dernières colonnes de la
 * section (z, r, .), gauche[r][z] = somme des `largeur` premières. Pour chaque colonne de coupe c :
 * bas[c][z] = somme des `largeur` dernières rangées de (z, ., c), haut[c][z] = des premières.
 * Une somme divisée par `largeur` rend exactement la moyenne du producteur, et tient sur 16 bits.
 * Chaque sortie a ncoupes * nz cases, rangée de coupe majeure.
 */
vesuve_statut vesuve_profils_de_bord(const uint8_t *bloc, int nz, int ny, int nx, const int *coupes,
                                     int ncoupes, int largeur, uint16_t *droit, uint16_t *gauche,
                                     uint16_t *bas, uint16_t *haut);

/**
 * @brief Le profil de profondeur d'un chunk : la moyenne de chaque couche (nz valeurs).
 */
vesuve_statut vesuve_profil_de_profondeur(const uint8_t *bloc, int nz, int ny, int nx, double *profil);

/**
 * @brief Le pas d'une coupe (`la_derive_saccumule_t_elle.py:99`, `un_pas`).
 *
 * a et b centrés, puis pour chaque décalage k de -plage à +plage la corrélation normalisée par
 * l'énergie des deux fenêtres ; le pas vaut -(argmax - plage), le PREMIER maximum en cas d'égalité.
 * Signe : z de la matière dans le chunk b moins z de la même matière dans le chunk a.
 * Un bord plat (énergie nulle) est INDECIDABLE.
 *
 * @param sature reçoit 1 si |pas| atteint la plage : la couture a pu sauter un demi-feuillet.
 */
vesuve_statut vesuve_pas_dune_coupe(const double *a, const double *b, int n, int plage, int *pas,
                                    int *sature);

/**
 * @brief Le pas d'une couture, moyenné sur ses coupes lisibles (`le_pas_de_k_rangees`, `204`:120).
 *
 * a et b sont ncoupes profils de n valeurs ; `lisible[i]` dit si la coupe i existe des deux côtés.
 * Les coupes lisibles dont le pas est décidable, dans l'ordre, donnent : le pas (leur moyenne), le
 * désaccord (moyenne des rangs pairs moins moyenne des rangs impairs) et leur nombre. Moins de deux,
 * ou une demi-moyenne vide : INDECIDABLE. Les valeurs ne sont PAS arrondies : la publication arrondit
 * à quatre décimales avec le `round` de Python, que la couche Python applique.
 */
vesuve_statut vesuve_pas_dune_couture(const double *a, const double *b, const uint8_t *lisible,
                                      int ncoupes, int n, int plage, double *pas, double *desaccord,
                                      int *coupes);

/* ------------------------------------------------------------------------------------------------
 * E6 -- le certificat : AUCUNE fonction ici, et c'est mesuré.
 *
 * Rejouer la procédure sans main de `246` entière depuis ses lectures publiées prend 3,5 s en Python,
 * et son nul par bootstrap ne se reproduit au bit près que dans l'ordre de sommation de numpy. La
 * porter en C n'achèterait aucun temps et coûterait la parité : elle vit dans `vesuve/treillis/`.
 * ---------------------------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------------------------------
 * E7 -- juger sans vérité terrain
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief [F25] Le test de convergence : alpha = log(e1 / e0) / log(n1 / n0) (`R3-F10`).
 * Une fenêtre qui ne double pas (n1 / n0 < 2) ou un écart nul au départ : INDECIDABLE.
 */
vesuve_statut vesuve_alpha_de_convergence(double e0, double e1, double n0, double n1, double *alpha);

/**
 * @brief [F15] La cohérence d'incréments : |somme d_i| / somme |d_i|.
 */
vesuve_statut vesuve_coherence(const double *increments, int n, double *coherence);

/**
 * @brief [F17] La cohérence corrigée de son plancher de bruit 1/sqrt(n) :
 * max(0, (c - 1/sqrt(n)) / (1 - 1/sqrt(n))).
 */
vesuve_statut vesuve_coherence_corrigee(double coherence, int n, double *corrigee);

/* ------------------------------------------------------------------------------------------------
 * E8 -- rendre, et valider par l'encre
 * ---------------------------------------------------------------------------------------------- */

/**
 * @brief [F31] Le nombre de Fresnel du régime de scan : F = sqrt(lambda D) / p, lambda = hc / E
 * (`src/encre/nombre_de_fresnel.py:142`, `R6-F08`).
 *
 * ⚠ C'est l'inverse de la racine du nombre de Fresnel classique a^2 / (lambda D), que
 * `docs/archive/151` écrit par erreur : c'est cette forme-ci qui rend F = 0,39 pour les treize
 * rouleaux du prix.
 */
vesuve_statut vesuve_nombre_de_fresnel(double pas_um, double distance_m, double energie_kev,
                                       double *fresnel);

/** Une paire (score, étiquette) : le tampon de tri de l'aire sous la courbe. */
typedef struct {
    double score;
    uint8_t etiquette;
} vesuve_paire;

/**
 * @brief L'aire sous la courbe ROC, par Mann-Whitney aux rangs moyens (`evaluate_segment.py:72`).
 * `etiquettes` vaut 0 ou 1 ; sans positif ou sans négatif : INDECIDABLE. `travail` : n paires.
 */
vesuve_statut vesuve_aire_sous_la_courbe(const double *scores, const uint8_t *etiquettes, size_t n,
                                         vesuve_paire *travail, double *auc);

/**
 * @brief L'échantillonnage trilinéaire d'un volume le long des normales d'une surface.
 *
 * Pour chaque point p et chaque décalage d, sortie[d][p] = V(p + d n) interpolé ; un point ou une
 * normale invalide (non fini) rend 0 et la case vaut 0 dans `valide`. Volume en ordre C
 * [nz][ny][nx], points et normales en (x, y, z) dans le repère du volume.
 */
vesuve_statut vesuve_echantillonner_le_long_des_normales(const uint8_t *volume, int nz, int ny, int nx,
                                                         const float *points, const float *normales,
                                                         size_t npoints, const float *decalages,
                                                         int ndecalages, float *sortie, uint8_t *valide);

#ifdef __cplusplus
}
#endif

#endif /* VESUVE_H */

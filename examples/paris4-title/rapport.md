# paris4-title — rapport

`vesuve 0.1.0` · noyau `0.1.0` · Linux x86_64 python 3.13.14 · 27.82 s

## Les exigences du prix

| exigence | état | ce qui est mesuré |
|---|---|---|
| une image que les papyrologues puissent lire | **non mesurée** | des vues de la fin du texte sur la bande la plus intérieure, à 19,2 µm par pixel ; personne ne les a lues |
| tout volume de Scroll 1, 2,4 µm compris | **atteinte** | les cartes d'encre publiées sur le volume à 2,4 µm |
| validation sur une région tenue à l'écart | **partiel** | deux révisions indépendantes de la même bande confrontées (T5) ; pas de vérité de terrain |
| le cœur du rouleau | **non atteinte** | les spires w000 à w009 ne sont dans aucune bande publiée |

## Les étages

### T0 — la règle (B1) : fait

- `la_regle` : le début du texte est à l'extérieur du rouleau, la fin et le titre (le colophon) au cœur : « the end of the papyrus (the innermost part of the carbonised scroll) where the colophon with the title of the work may be preserved »
- `son_statut` : rapporté (`docs/archive/06_mesures_a_faire.md:10-15`, Bodleian), pas mesuré ici
- `ce_que_dit_le_prix` : aucune encre détectée jusqu'ici dans la région attendue ; encre peut-être différente ; rangées du haut physiquement manquantes

### T1 — la bande la plus intérieure (B1) : fait

- `les_bandes_vues` : 55
- `la_plus_interieure` : w010-027
- `ses_revisions` : ["20260623141924", "20260701183124"]
- `ce_qui_manque` : les spires w000 à w009 ne sont dans aucune bande publiée : le cœur même n'est pas tracé

### T2·20260623141924 — le sens de l'enroulement (B1) : partiel

*la silhouette de la carte ne corrèle qu'à 0.30 avec celle du maillage : l'orientation retenue n'est pas établie*

- `le_rayon_au_debut_mm` : 5.54
- `le_rayon_a_la_fin_mm` : 2.88
- `lorientation_de_la_carte` : identite
- `sa_correlation` : 0.303
- `le_coeur_est_du_cote` : droite de la carte

### T4·20260623141924 — la fin du texte (B1) : fait

- `le_seuil` : 0.128
- `la_derniere_colonne` : [146, 222]
- `ses_tranches_ecrites` : [5, 15]
- `la_part_de_la_bande_apres_le_texte` : 0.5033
- `la_regle` : 16 tranches × 449 cellules le long de la spire, écrite ou vide par le seuil d'Otsu sur toutes les cellules : aucun paramètre choisi

### T2·20260701183124 — le sens de l'enroulement (B1) : fait

- `le_rayon_au_debut_mm` : 5.41
- `le_rayon_a_la_fin_mm` : 2.88
- `lorientation_de_la_carte` : identite
- `sa_correlation` : 0.981
- `le_coeur_est_du_cote` : droite de la carte

### T4·20260701183124 — la fin du texte (B1) : fait

- `le_seuil` : 0.1393
- `la_derniere_colonne` : [239, 306]
- `ses_tranches_ecrites` : [0, 2]
- `la_part_de_la_bande_apres_le_texte` : 0.3163
- `la_regle` : 16 tranches × 449 cellules le long de la spire, écrite ou vide par le seuil d'Otsu sur toutes les cellules : aucun paramètre choisi

### T5 — le témoin : deux révisions de la même bande (B3) : fait

- `les_parts_apres_le_texte` : [0.5033, 0.3163]
- `leur_ecart` : 0.187
- `la_lecture` : deux maillages indépendants de la même bande : s'ils placent la fin du texte au même endroit de la spire, la fin n'est pas un artefact d'un seul maillage

### T6 — les candidats (B1) : fait

- `les_lieux` : [{"le_segment": "20260623141924", "la_derniere_colonne_px": [7344, 11218], "sa_derniere_ligne_px": 5968, "sa_hauteur_ecrite": 1.0, "la_region_candidate_px": {"colonnes": [6376, 15092], "rangees": [5968, 5969]}}, {"le_segment": "20260701183124", "la_derniere_colonne_px": [11311, 14529], "sa_derniere_ …
- `les_produits` : ["20260623141924_derniere_colonne.png", "20260623141924_sous_la_derniere_ligne.png", "20260623141924_bande_entiere.jpg", "20260701183124_derniere_colonne.png", "20260701183124_sous_la_derniere_ligne.png", "20260701183124_bande_entiere.jpg", "candidats.json"]
- `la_lecture` : quand la dernière colonne est COURTE et que rien ne la suit vers le cœur, c'est la forme de la fin d'un livre : le titre final se cherche sous sa dernière ligne et dans l'espace qui la suit. En orange la colonne, en bleu la région
- `ce_quil_reste` : lire, et chercher une AUTRE encre : le prix dit que la région attendue n'a montré aucune encre détectable ; ces vues sont celles du modèle publié, et le produit ink-3d ou la carte à 1,129 µm sont les suivantes à regarder


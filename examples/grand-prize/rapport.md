# grand-prize — rapport

`vesuve 0.1.0` · noyau `0.1.0` · Linux x86_64 python 3.13.14 · 4.31 s

## Les exigences du prix

| exigence | état | ce qui est mesuré |
|---|---|---|
| un des treize rouleaux éligibles | **non atteinte** | PHercParis4 : le référent de la méthode, hors de la liste |
| 100 % du recto déroulé | **non atteinte** | un segment publié : 6333 chunks certifiés sur 97771 (6.48% de SON empreinte), un segment n'est pas un rouleau |
| pipeline automatique, au plus 8 h d'humain | **atteinte** | 0 h : la procédure prend chaque décision sans main (`R4-F410`) ; la seule entrée est la présence |
| 70 % des caractères lisibles par colonne | **non mesurée** | aucune lecture ; au régime du prix l'encre publiée est plate (`R1-F20`) |
| un maillage par colonne, `column_NN.tifxyz` | **non atteinte** | la surface certifiée est rendue entière, avec `approval.tif` ; pas de découpage en colonnes |
| image Docker | **atteinte** | `vesuve/Dockerfile`, qui lance ce pipeline depuis les données embarquées |
| graines fixées et rapportées | **atteinte** | nul par blocs : graine 20261105, 999 tirages ; juge : graine 20260924 |
| intégré à VC3D | **non mesurée** | la surface et `approval.tif` suivent le contrat tifxyz que villa lit |

## Les étages

### E0 — l'objet (B1) : partiel

*PHercParis4 n'est pas un des treize rouleaux du prix : la méthode est construite là où le référent existe, et il faudra la transporter sur un rouleau sans vérité de terrain (`151` E0)*

- `lobjet` : PHercParis4
- `le_segment` : 20230702185753
- `eligible` : false
- `les_eligibles` : ["PHerc0125", "PHerc0191", "PHerc0211", "PHerc0257", "PHerc0268", "PHerc0358", "PHerc0800", "PHerc0813", "PHerc0826", "PHerc1203", "PHerc1218", "PHerc1447", "PHerc1545"]

### E1 — le volume (B1) : fait

- `le_volume` : PHercParis4/segments/20230702185753/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
- `la_grille` : [396, 285]
- `les_chunks_presents` : 97771
- `la_provenance` : la liste des clés du dépôt, relue par `ou_sarrete_le_segment.py` (98 pages)

### E2 — l'échelle (B1) : fait

- **[E2] le demi-feuillet** (`R4-F14`) : $`\delta = \mathrm{round}\!\left(\frac{s}{2\,v}\right)`$

  s_um = 173, v_um = 2.4 → **36**


### B — le budget de la nappe (B1) : fait

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = traverser la_moyenne_des_rangees, delta = 36, sigma = 1.9245 → **349.92**

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = traverser le_plancher_de_la_matiere, delta = 36, sigma = 2.233 → **259.913**

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = traverser une_rangee_seule, delta = 36, sigma = 2.4587 → **214.385**

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = saccorder 197-199, delta = 36, sigma = 3.4004 → **112.084**

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = saccorder 198-197, delta = 36, sigma = 2.7138 → **175.974**

- **[N5] la longueur tenable** (`R4-F340`) : $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = saccorder 198-199, delta = 36, sigma = 2.9794 → **145.998**

- **[N7] le triangle des bruits propres** (`R4-F343`) : $`\sigma_{b,i}^2 = \frac{\sigma_\Delta^2(i,j) + \sigma_\Delta^2(i,k) - \sigma_\Delta^2(j,k)}{2}`$

  rangee = 198, var_198_197 = 7.36471, var_198_199 = 8.87682, var_197_199 = 11.5627 → **2.33941**

- `la_longueur_tenable_qui_lie` : 112.08
- `les_coutures_dune_rangee` : 284
- `la_conclusion` : une rangée de 284 coutures dépasse les 112.08 que l'accord permet : deux rangées marchées chacune pour soi finissent sur deux feuillets (`R4-F341`). D'où le certificat : fermer des boucles plutôt que marcher.

### E4 — le treillis : les bandes publiées (B4) : fait

- `les_bandes_publiees` : 112
- `les_bandes_donnees` : 0

### E4L — le treillis : lire ce que la procédure demande (B4) : sauté

*rejeu : les bandes publiées et celles données par --lectures ; --lire lit ce que la procédure demande*

- `les_bandes_publiees` : 112
- `les_bandes_neuves` : 0
- `les_chunks_lus_ici` : 0
- `les_tours_de_lecture` : 0

### E6 — le certificat (B4) : partiel

*111 bandes (24263 chunks) restent à lire pour juger ce que la procédure trouve ; la couverture est celle de ce qui est jugé. `vesuve grand-prize --lire` les lit, environ 21 min à 16 fils*

- **[S] la portée qui voit** (`R4-F409`) : $`p = \max_{\text{coupes hors traversée}} (y_{j+1} - y_j) - 1 = 29`$

  ecart_qui_evite = 30 → **29**

- **[L] la fermeture d'une boucle** (`R4-F393`) : $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  boucle = 14, 26, 32, 81, largeur = 9, etat = dessous → **-2.0133**

- **[P] le profil d'une boucle** (`R4-F403`) : $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  boucle = 14, 26, 32, 81, a_la_coupe = 71, demi = 36 → **-8.1875**

- **[L] la fermeture d'une boucle** (`R4-F393`) : $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  boucle = 26, 223, 243, 260, largeur = 9, etat = franchit → **-35.6938**

- **[P] le profil d'une boucle** (`R4-F403`) : $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  boucle = 26, 223, 243, 260, a_la_coupe = 173, demi = 36 → **-40.2188**

- **[M] la marge de départage** (`R4-F401`) : $`\mu_n = |L_n| - \min_m |L_m| - \mathrm{m\acute ediane}\,|L_n^{\mathrm{nul}}|`$

  la_ligne_qui_derive = 260, la_plus_serree = letroite → **{'laile': 11.2626, 'la_large': 2.8875}**

- **[L] la fermeture d'une boucle** (`R4-F393`) : $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  boucle = 26, 112, 243, 269, largeur = 9, etat = dessous → **1.2159**

- **[P] le profil d'une boucle** (`R4-F403`) : $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  boucle = 26, 112, 243, 269, a_la_coupe = 54, demi = 36 → **7.3125**

- **[L] la fermeture d'une boucle** (`R4-F393`) : $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  boucle = 216, 308, 13, 22, largeur = 9, etat = dessous → **6.9445**

- **[P] le profil d'une boucle** (`R4-F403`) : $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  boucle = 216, 308, 13, 22, a_la_coupe = 308, demi = 36 → **6.9446**

- **[K] la couverture** (`R4-F410`) : $`\kappa = \frac{|A \wedge \bigcup_b M_b|}{|A|}`$

  chunks = 6333, sur = 97771 → **0.0648**

- `le_rectangle` : [26, 384, 22, 243]
- `les_etats` : {"à lire": 33, "dessous": 3, "franchit": 1, "aucune aile": 1}
- `les_boucles_qui_tiennent` : [{"les_coins": [14, 26, 32, 81], "la_largeur": 9}, {"les_coins": [26, 112, 243, 269], "la_largeur": 9}, {"les_coins": [216, 308, 13, 22], "la_largeur": 9}]
- `les_bandes_a_lire` : 111
- `les_chunks_a_lire` : 24263
- `le_temps_de_lecture_estime_min` : 21.3
- `les_ailes_autour_dun_rectangle_non_juge` : true
- `lavertissement` : des ailes sont certifiées autour d'un rectangle qui n'est pas lui-même jugé : elles tiennent sur leur profil, mais le rectangle qui les relie n'est pas prouvé

### E7 — le juge sans vérité terrain (B3) : sauté

*demandé avec --juger N : il lit N chunks certifiés sur le bucket*


### E8 — l'encre, la règle graduée (B3) : fait

- `la_carte` : PHercParis4/segments/20230702185753/ink-detection/downsampled/PHercParis4-20230702185753-2.4um-0.22m-78keV-volume-20260411134726-20260417190342-new_canon_autoresearch_recipe-tile256-stride128-ds8.jpg
- `sa_forme` : [6325, 4550]
- `limage` : encre_sous_le_masque.jpg
- `la_lecture` : la carte d'encre PUBLIÉE (modèle de l'équipe, 2,4 µm), sous le masque : l'encre est la règle graduée qui dit si le déroulé fait du sens, pas l'ouvrage

### E9 — l'emballage (B1) : fait

- `la_surface` : PHercParis4/segments/20230702185753/mesh/20230702185753-on-20260411134726-2.4um.tifxyz
- `sa_grille` : [2530, 1820]
- `les_sommets_certifies` : 258292
- `les_sommets_valides` : 4029118
- `les_produits` : ["masque_par_chunk.tif", "masque_par_chunk.png", "certificat.json", "bandes_a_lire.json", "20230702185753_certifie.tifxyz/ (x, y, z, meta.json, approval.tif)"]
- `ce_qui_nest_pas_produit` : `column_NN.tifxyz` : découper la surface en colonnes de texte demande que l'encre soit lisible colonne par colonne, et au régime des treize rouleaux le détecteur publié ne sépare pas la feuille du vide (`R1-F20`). Le livrable est la surface certifiée, entière, et son masque.


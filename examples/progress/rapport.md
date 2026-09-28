# progress — rapport

`vesuve 0.1.0` · noyau `0.1.0` · Linux x86_64 python 3.13.14 · 4.36 s

## Les exigences du prix

| exigence | état | ce qui est mesuré |
|---|---|---|
| détecter un cas d'échec d'une méthode existante sur de vraies données | **atteinte** | la colonne 260, des lignes 26 à 223 : le cumul franchit le demi-feuillet aux coupes [163, 173, 203] (pic -40.2188 voxels à la coupe 173) |
| reproductible et documenté | **atteinte** | rejeu depuis les données embarquées, sans réseau ni graine libre |
| borner ce qu'on affirme | **atteinte** | une région à regarder, pas une condamnation (`R4-F406`) |

## Les étages

### P0 — le segment audité (B1) : fait

- `lobjet` : PHercParis4
- `le_segment` : 20230702185753
- `le_volume` : PHercParis4/segments/20230702185753/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
- `sa_nature` : un segment publié, tracé par d'autres : l'audit juge une méthode existante

### P1 — le certificat, lu à l'envers (B4) : fait

- **[P] le profil d'une boucle** (`R4-F403`) : $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  boucle = 26, 223, 243, 260, a_la_coupe = 173, demi = 36 → **-40.2188**

- **[M] la marge de départage** (`R4-F401`) : $`\mu_n = |L_n| - \min_m |L_m| - \mathrm{m\acute ediane}\,|L_n^{\mathrm{nul}}|`$

  la_ligne_qui_derive = 260 → **{'laile': 11.2626, 'la_large': 2.8875}**

- `les_boucles_jugees` : 4
- `les_boucles_qui_franchissent` : 1

### P2 — les cas d'échec (B1) : fait

- `les_chunks_suspects` : 963
- `les_cas` : ["la colonne 260, des lignes 26 à 223 : le cumul franchit le demi-feuillet aux coupes [163, 173, 203] (pic -40.2188 voxels à la coupe 173)"]
- `la_limite` : l'audit ne départage pas une colonne mal lue d'une matière qui s'écarte (`R4-F406`) : il désigne où regarder

### P3 — la région suspecte, sur l'encre publiée (B3) : fait

- `limage` : encre_et_region_suspecte.jpg


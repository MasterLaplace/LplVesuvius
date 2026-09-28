# first-letters — rapport

`vesuve 0.1.0` · noyau `0.1.0` · Linux x86_64 python 3.13.14 · 15.5 s

## Les exigences du prix

| exigence | état | ce qui est mesuré |
|---|---|---|
| un des 23 rouleaux éligibles | **atteinte** | PHerc1447, volume 20250521151220 |
| dix lettres dans 4 cm² | **non mesurée** | aucune lettre n'est lue par ce pipeline : c'est le travail d'un œil |
| une image programmatique statique, nommée d'après son maillage | **atteinte** | 20250702235910-auto_grown_20250702235910292_encre.png, 20250702235910-auto_grown_20250702235910292_fibres.png |
| barre d'échelle de 1 cm | **atteinte** | 10 mm = 1157 px à 8.64 µm |
| rangées annotées | **non atteinte** | aucun pic intérieur d'autocorrélation, à aucun angle de ±12° : pas de rangées dans l'encre du modèle |
| encre sur un rendu où les fibres se voient | **atteinte** | 20250702235910-auto_grown_20250702235910292_encre.png |
| montrer que le texte n'est pas halluciné | **non atteinte** | le mélange des mêmes pixels perd l'interligne ; la région tenue à l'écart est mesurée à part ; aucune vérité de terrain sur ce rouleau |

## Les étages

### F0 — l'objet et son régime (B1) : fait

- **[F31] le nombre de Fresnel** (`R6-F08`) : $`F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}`$

  pixel_um = 8.64, distance_m = 1.2, energie_kev = 116 → **0.414506**

- **[F31] le nombre de Fresnel** (`R6-F08`) : $`F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}`$

  regime = production, pixel_um = 2.4, distance_m = 0.2, energie_kev = 78 → **0.742916**

- `le_volume` : 20250521151220
- `le_rapport_au_regime_de_production` : 0.558
- `la_consequence` : un scan de repérage : les modèles d'encre publiés ont été entraînés au régime de production, et au régime du prix leur accord avec la carte publiée est plat (`R1-F20`). Leur sortie ici est une vue, pas une preuve.

### F1 — la surface (B1) : fait

- `les_couches` : 31
- `la_couche_mediane` : 15
- `la_forme` : [2980, 3240]
- `le_type` : uint8
- `la_part_de_papyrus` : 0.5254
- `le_maillage` : 20250702235910-auto_grown_20250702235910292
- `le_maillage_existe` : true

### F2 — la fenêtre de 4 cm² (B1) : fait

- `le_cote_px` : 2315
- `le_cote_mm` : 20.0
- `la_fenetre` : {"r0": 208, "c0": 528, "cote": 2315, "papyrus": 3825969, "la_part_de_papyrus": 0.7139}
- `la_fenetre_tenue_a_lecart` : {"r0": 2064, "c0": 0, "cote": 523, "papyrus": 240429, "la_part_de_papyrus": 0.879, "le_cote_reduit": true}
- `la_regle` : choisies sur la SEULE couverture de papyrus, jamais sur l'encre : une fenêtre élue là où l'encre paraît forte ferait des lettres avec n'importe quel bruit

### F3 — le rendu où les fibres se voient (B1) : fait

- `limage` : 20250702235910-auto_grown_20250702235910292_fibres.png
- `la_regle` : la couche médiane étirée entre 1 et 99 % (`couche_de_rendu.py:35`)

### F4 — l'encre sans modèle (B1) : fait

- `limage` : 20250702235910-auto_grown_20250702235910292_sans_modele.png
- `les_couches` : [12, 13, 14, 15, 16, 17, 18]
- `la_regle` : « sometimes ink is visible directly in the flattened render, with no model at all — usually bright areas » : la projection maximale des sept couches centrales. Une vue, pas un détecteur.

### F5 — l'encre du modèle (B3) : fait

- `la_carte` : /home/masterlaplace/LplVesuvius/data/out/ink_PHerc1447_complet.npy
- `sa_provenance` : une carte inférée par ailleurs, fournie avec --carte
- `la_part_vue` : 1.0
- `la_part_au_dessus_de_0` : 0.042

### F6 — les témoins (B3) : fait

- `les_rangees` : {"le_reel": {"periode_px": null, "nettete": 0.0, "angle_deg": null, "plancher": null, "periodique": false}, "le_melange": {"periode_px": 76, "nettete": 0.14880421447260087, "plancher": 0.17865619976519528, "angle_deg": 10.0, "periodique": false}, "la_region_tenue_a_lecart": {"periode_px": null, "net …
- `les_rangees_tracees` : 0
- `limage` : 20250702235910-auto_grown_20250702235910292_encre.png
- `la_regle` : `typographie.py` : l'encre binarisée par Otsu, la densité par rangée autocorrélée, périodique quand la netteté dépasse 2√(2 ln k)/√n ; le mélange doit perdre la période
- `le_recouvrement_dentrainement` : AUCUN : ce segment n'est pas parmi les 45 segments étiquetés du modèle de 2023

### F7 — l'emballage (B1) : fait

- `les_produits` : ["20250702235910-auto_grown_20250702235910292_encre.png", "20250702235910-auto_grown_20250702235910292_fibres.png", "20250702235910-auto_grown_20250702235910292_sans_modele.png", "fenetres.json"]
- `ce_quil_reste_a_un_humain` : lire : compter dix lettres dans la fenêtre, et vérifier qu'elles tiennent sur la région tenue à l'écart. Le pipeline dit où regarder et ce que valent ses témoins ; il ne lit pas.


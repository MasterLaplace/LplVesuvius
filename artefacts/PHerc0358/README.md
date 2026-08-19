# `PHerc0358` — la première trace d'un rouleau du Grand Prize

2026-08-19. Un des **dix** rouleaux du prix qui n'avaient **aucun segment publié**.
Produit avec la chaîne officielle VC3D, depuis les données publiées, **sans télécharger
le volume** (893 Go).

⚠⚠ **La trace est MAUVAISE** — elle coupe à travers les spires. Elle est conservée ici
parce que ce qui a de la valeur n'est pas la surface, c'est **la boucle complète et son
verdict** : trois instruments l'ont condamnée, **deux avant tout rendu**. Analyse : `docs/24`.

| fichier | quoi |
|---|---|
| `mesh.tifxyz/` | la surface tracée — **8,48 cm²**, 79 générations, 13,9 s de calcul |
| `mesh_flat.tifxyz/` | la même, aplatie par ABF++ (96,2 % des points rastérisés) |
| `seed.json` | les paramètres qui marchent. ⚠⚠ **`voxelsize` est obligatoire** : à 0 (le défaut) l'aire en cm² est nulle *par construction* et toute surface est rejetée |
| `selfcross_a.json` | le verdict de `vc_tifxyz_selfcross` — **240 contacts transverses**, pénétration max 200 µm |
| `rendu_vue_ensemble.png` | le rendu complet réduit, 29,4 × 29,2 mm — *aussi dans `docs/images/24_rendu_ensemble.png`* |
| `rendu_detail_9x9mm.png` | ⭐ un détail à **pleine résolution** (1000×1000 px = 9,4 × 9,4 mm) : on y voit **plusieurs feuilles par la tranche**, pas les fibres d'une seule — *aussi dans `docs/images/24_rendu_detail.png`* |

## La graine

```
-s 1544 1544 7768        # ordre x y z ; ⚠ le zarr est indexe (z,y,x)
```
trouvée par `analysis/src/trouver_graine.py` sur la prédiction de surface publiée, à
distance, sans rien télécharger.

## Reproduire

Voir `docs/24_premiere_trace_rouleau_du_prix.md` §5. ⚠ Le rendu (54 Mo) et le cache de
volume ne sont pas conservés — ils se régénèrent en ~4 minutes.

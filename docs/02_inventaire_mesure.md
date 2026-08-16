# Inventaire mesuré : ce qu'il y a, et ce qu'on peut se permettre

2026-08-16. Tous les chiffres de cette page ont été **mesurés**, pas repris d'une
page de doc. L'outil qui les produit est `tools/s3_size.py` (sortie `--json` pour
rejouer). Rien n'a été téléchargé pour les obtenir.

---

## 1. Le fait qui décide de tout : un volume ne tient pas sur cette machine

```
PHerc0332/segments/   ->  219,1 Mio  (14 objets)
PHerc0332/volumes/    ->  2,1 Tio    (1 081 602 objets)
```

**Un seul volume d'un seul rouleau pèse 2,1 Tio.** Le budget disque est de 100 Go.
La question « quel rouleau télécharger » n'a donc pas de réponse : *aucun*.

Ce n'est pas une contrainte subie, c'est la contrainte qui **désigne le bon plan de
travail**. `windcheck` l'écrit noir sur blanc : *« No GPU, no volume download and no
ML model is involved: the analysis reads only the `tifxyz` surface itself. »* Et
`herculaneum-scroll-tools` comme `vesuvius-automesh` streament depuis S3 sans copie
locale, sur un portable.

> **Règle de travail** : on travaille sur les **surfaces**, pas sur les volumes. Une
> surface tracée pèse ~10 Mio, un volume ~2 Tio — cinq ordres de grandeur. Tout ce
> qui exige le volume entier est hors de portée, et tout ce qui se juge sur la
> surface est à portée de main. C'est la même discipline que le catalogue de
> LplKnowledge : indexer sans rapatrier.

## 2. Où sont les surfaces déjà tracées

45 échantillons publiés — 35 rouleaux, 10 fragments — et **310 segments** au total.
Mais ils sont extrêmement concentrés :

| échantillon | type | segments | résolution la plus fine |
|---|---|---:|---|
| PHercParis4 | rouleau | **81** | 1,129 µm |
| PHerc0172 | rouleau | **53** | 7,91 µm |
| PHerc0139 | rouleau | **38** | 1,129 µm |
| PHerc0500P2 | fragment | **38** | 0,55 µm |
| PHerc1667 | rouleau | 20 | 1,129 µm |
| PHerc0814 | rouleau | 19 | 1,129 µm |
| PHerc0009B | fragment | 19 | 2,401 µm |
| PHerc1447 | rouleau | 15 | 8,64 µm |
| PHercMANBp | fragment | 11 | 1,129 µm |
| PHerc0343P | fragment | 8 | 2,215 µm |
| PHerc0800 | rouleau | 6 | 8,64 µm |
| PHerc0332 | rouleau | 2 | 2,399 µm |
| **33 autres** | — | **0** | 8,64 à 9,362 µm |

⚠ **33 échantillons sur 45 n'ont aucune surface tracée.** Les quatre premiers en
concentrent 210 sur 310, soit deux tiers.

### Correction d'une hypothèse de travail

L'hypothèse de départ était que les **petits** échantillons sont plus friables, donc
plus durs à dérouler. Les données ne la soutiennent pas, et ce qu'elles montrent est
plus utile : **ce qui sépare un échantillon tracé d'un échantillon vierge est la
résolution de son scan**, pas sa taille ni son état.

Tous les échantillons à 0 segment sont scannés à **8,64 ou 9,362 µm** — des scans de
survol. Tous ceux qui portent beaucoup de segments sont à **1,129 µm** ou mieux.
Aucun échantillon fin n'est à zéro ; aucun échantillon grossier n'est bien tracé.

Ça inverse la lecture du problème : le goulot n'est pas « quel rouleau est le plus
dur », c'est que **presque tout le corpus n'a jamais été touché**, faute d'un scan
assez fin ou faute de temps humain. Et c'est cohérent avec ce que dit le concours :
le coût est l'intervention humaine, pas la difficulté intrinsèque d'un rouleau
particulier.

⚠ À ne pas surinterpréter : la corrélation ne dit pas le sens. Il est tout aussi
plausible qu'on ait **choisi de rescanner finement** les rouleaux jugés prometteurs.
Les deux lectures conduisent au même plan de travail, donc trancher n'est pas
urgent — mais l'écrire évite de croire plus tard qu'on l'avait établi.

## 3. Conséquence sur la couverture de `windcheck`

`windcheck` annonce **284 traces** recensées et terminalement statuées, 274 avec
référence propre. Le corpus publié en compte **310**. Autrement dit son recensement
couvre l'essentiel de ce qui existe — ce n'est pas un échantillon, c'est presque
l'exhaustif.

**Conséquence directe pour nous** : il n'y a rien à gagner à refaire ce recensement.
Ce qui n'est pas fait, et que son README nomme lui-même, c'est de savoir si
**corriger** les défauts recensés change quoi que ce soit en aval.

## 4. Budget retenu

| poste | volume | justification |
|---|---|---|
| Miroir du site | 228 Mio | fait |
| Dépôts | 2,4 Gio | fait |
| Surfaces `tifxyz` (échantillon `windcheck`) | ~409 Mio | 212 fichiers, épinglés par SHA-256 |
| **Total à ce stade** | **~3 Gio** | soit **3 %** du plafond de 100 Go |

On est deux ordres de grandeur sous le budget, et c'est le bon endroit où être : la
première question ne demande pas de données massives, elle demande un instrument.

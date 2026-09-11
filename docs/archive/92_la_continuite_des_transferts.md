# 92 — Les transferts que l'humain a réussis sont continus au cœur, brisés au bord

> ⭐⭐⭐ **Le plus grand saut entre deux cellules voisines d'une même ligne de grille, rapporté au
> pas d'échantillonnage, vaut 1,7 au cœur, 5,9 au milieu et 31,0 au bord. Là où le rouleau est
> intact, un humain trace continûment ; là où il ne l'est pas, MÊME UN HUMAIN rend une surface
> discontinue.**

![la continuité des transferts](../images/92_la_continuite_des_transferts.png)

## 1. La question, et pourquoi elle est celle du goulot

[`91`](91_le_pas_lu_sur_les_transferts.md) établit que les 28 bandes de `PHercParis4` sont des
**transferts de spire à spire déjà faits à la main**, et que leur étendue déclarée *est* leur
nombre de tours. Reste à savoir ce que l'humain a **réellement produit** : une nappe continue qui
dérive de feuille en feuille, ou une couture de morceaux ?

## 2. ⭐⭐⭐ La dégradation, en tiers du corpus

| tiers | rapport médian | max | bandes |
|---|---:|---:|---:|
| **cœur** | **1,7** | 2,4 | 9 |
| **milieu** | **5,9** | 22,1 | 9 |
| **bord** | **31,0** | 41,1 | 10 |

⭐ Les tiers sont une **découpe de la matière** et non un choix : les bandes sont déjà ordonnées du
cœur vers le bord. Et le verdict porte sur le **rapport au pas d'échantillonnage**, qui n'a aucune
unité à choisir — une surface continue échantillonnée régulièrement rend un rapport proche de 1,
quelle que soit la finesse du maillage.

## 3. ⭐⭐ Ce que ça borne pour le remplaçant de l'humain

**Un automate ne peut pas être jugé sur les bandes externes comme sur les internes.** Là où même un
humain rend une surface discontinue, exiger la continuité d'une machine serait exiger ce que
personne n'a produit.

⭐ Et ça **complète** l'explication de [`84`](84_une_surface_combien_de_spires.md) : l'étendue qui
tombe de 18 à 2 spires n'est pas seulement la circonférence qui croît
([`85`](85_le_sens_du_rang.md)) — c'est aussi **la continuité qui casse**.

## 4. ⚠⚠ Une première lecture, fausse, gardée dans le fichier

J'ai vu les sauts sur les lignes **3, 4 et 181** d'une grille de 198 et conclu **« effilochage du
bord du maillage »**.

⭐ Le test structurel les **garde** : une cellule est dite *intérieure* quand ses **quatre**
voisines de grille sont valides — définition qui ne dépend d'aucune marge choisie — et les sauts de
trente millimètres y survivent. Ils sont donc dans de la **matière réellement maillée**.

## 5. ⚠⚠⚠ Et une seconde, réfutée par le test direct

Les sauts corrèlent fortement avec le gonflement de pente que `91` n'expliquait pas : **r = 0,797**
(0,870 en log-log). Les bandes à saut < 5 mm rendent **173 µm** de pente médiane, les autres
**393 µm**. **J'ai failli publier la cause.**

⭐ Le test direct la tue : **retirer les lignes qui contiennent un saut change la pente de 0,2 % en
médiane et 1,5 % au pire**, sur 15 bandes.

> **Une corrélation de 0,80 entre deux quantités qui montent ensemble n'est pas un mécanisme.**
> Retirer la cause supposée et regarder si l'effet bouge, si.

⚠ Donc la cause du gonflement de `91` reste **non trouvée**, avec désormais **trois** candidats
réfutés — la section ovale (elle *dégonfle*), le centre décalé (dix fois trop faible), et les sauts
(moins de 2 % d'effet). Le contrôle de fenêtre de `91` tient toujours **sans elle**.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/la_continuite_des_transferts.py --verifier
uv run python src/nappe/la_continuite_des_transferts.py \
    --json docs/mesures/la_continuite_des_transferts.json
uv run python src/figures/figure_la_continuite_des_transferts.py --verifier
```

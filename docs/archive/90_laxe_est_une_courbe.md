# 90 — L'axe du rouleau est une courbe, et `85` a payé cette hypothèse

> ⭐⭐⭐ **Le centre d'enroulement se déplace de 12,6 mm en x et 19,8 mm en y sur 144 mm de z,
> EN REVENANT SUR SES PAS, et s'écarte de sa propre droite de 11,6 mm — soit 63,9 épaisseurs de
> feuille. Tout marcheur qui suppose un repère cylindrique global se trompe de deux centimètres.**

![l'axe du rouleau est une courbe](../images/90_laxe_est_une_courbe.png)

## 1. Le contrôle que je n'avais pas fait

[`85`](85_le_sens_du_rang.md) estime l'axe comme **un** point (x, y) — la médiane de tous les
points de toutes les bandes — et en tire un rayon par bande. Un contrôle simple le réfute :

| | |
|---|---|
| étendue radiale d'une bande, mesurée | 8 à 14 mm |
| ce que `étendue × période` prédit | 0,36 à 3,3 mm |
| rapport | **×2,4 à ×38**, et il **croît** quand l'étendue diminue |

Une bande de deux spires couvrirait quatorze millimètres de rayon, soit l'équivalent de
**soixante-dix-sept** spires. Le modèle était faux.

## 2. ⚠⚠ Et le confondant est levé, pas supposé

Si une tranche de z ne contenait pas un **tour complet**, sa médiane serait tirée vers le secteur
présent — et si le secteur couvert changeait avec z, on lirait ce changement comme une **courbure**.

⭐ Mesuré : **100 % des 36 secteurs occupés dans chaque tranche**, 127 000 à 159 000 points par
tranche. La dérive n'est donc pas un artefact d'échantillonnage. C'est **une sonde fabriquée qui
m'a appris à poser cette question, en échouant** — elle déclarait « courbe » un rouleau
parfaitement droit dont les tranches ne contenaient qu'un demi-tour.

## 3. ⭐⭐ Ce qui survit, et il survit mieux

| | axe plat (`85`) | axe **courbe** |
|---|---|---|
| classement des rayons | 27/27 | **27/27** |
| longueur par passe, médiane | 384 mm | **362 mm** |
| bornes | 283 à **838** mm (**×2,97**) | **273 à 460** (**×1,68**) |
| hors le cœur | ×1,89, étr 17 % | ×**1,51**, étr **12,7 %** |

⭐ **Trois modèles d'axe rendent le même ordre** — plat, courbe, et l'ancienne révision. « Le rang
monte vers le dehors » n'était donc pas un artefact.

## 4. ⚠⚠⚠ Ce qui est retiré : le « second régime »

`85` publiait la bande du cœur à **838 mm** comme une population à part. Sous l'axe courbe elle
vaut **460 mm** et rentre dans la distribution.

**Il n'y avait pas deux régimes** : il y avait mon erreur d'axe, **concentrée sur la bande la plus
proche de l'axe** — donc la plus sensible à s'être trompé dessus. La rétractation est portée en
tête de `85`, là où le chiffre faux a été publié.

⚠ Ce qui **reste** réfuté : « l'étendue radiale d'une bande vaut son étendue fois la période ».
Même sous l'axe courbe les rapports vont de **1,5 à 25,9**. Une bande n'est pas un ruban
d'épaisseur constante — c'est une nappe qui court sur toute la longueur du rouleau, et dont la
section n'est pas un cercle.

## 5. ⭐⭐⭐ Pourquoi ça compte pour le graal

Le goulot est le **transfert de spire à spire**. Un marcheur qui supposerait un axe droit se
trompe de **deux centimètres**, soit une **centaine d'épaisseurs de feuille** : un tel cadre
placerait une spire à la place d'une autre, ce qui **est** exactement l'erreur que l'humain
corrige à la main.

⭐ **La courbure n'est donc pas un détail de mesure, c'est une propriété de l'objet** — et elle
dit qu'aucun repère global ne remplacera cet humain. Ce qui le remplacera devra être **local**,
comme la marche l'est déjà.

## 6. ⚠⚠ Trois seuils que j'aurais réglés sur ce qui passe

Mes premières sondes ont échoué sur **mes propres bornes** : « ×10 » quand la sonde donnait 7,4,
« <5 % » quand elle donnait 6,3. Le remède n'est pas de régler la borne — c'est de comparer **à ce
que l'autre méthode donne** :

- le verdict de courbure passe de `np.all(diff >= 0)` — que le moindre bruit casse — à l'**écart à
  sa propre droite**, rendu en **épaisseurs de feuille**, une unité mesurée ailleurs. Séparation :
  **1,0** pour un rouleau droit, **14,1** pour un courbé ;
- « le rayon par tranche redresse l'inclinaison » devient « il est **bien plus serré qu'un centre
  unique** », plus un contrôle que la fixture connaît — le rayon vrai de 40 voxels.

⚠ Et le troisième échec cachait une vérité que ma revendication ignorait : **une tranche a une
épaisseur, donc l'axe bouge dedans**. « Le rayon par tranche est parfait » n'a jamais été vrai et
ne devait pas être asserté.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/laxe_est_une_courbe.py --verifier
uv run python src/nappe/laxe_est_une_courbe.py --json docs/mesures/laxe_est_une_courbe.json
uv run python src/figures/figure_laxe_est_une_courbe.py --verifier
```

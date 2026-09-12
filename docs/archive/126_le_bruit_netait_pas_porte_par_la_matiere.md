# 126 — Le bruit n'était pas porté par la matière, et la nappe se déchire douze fois sur douze

> ⚠⚠⚠ **LA PILE FABRIQUÉE N'ÉTAIT PAS UN OBJET.** `VolumeFabrique` tirait son bruit **à chaque
> lecture** : le même point rendait deux valeurs différentes. Ça ne se voit pas sur une marche
> isolée — elle ne repasse pas — mais ça fausse **tout ce qui compare deux marches sur la même
> matière**, c'est-à-dire exactement ce que `124` mesure.
>
> ⭐⭐⭐⭐ **ET LA CORRECTION REND LE RÉSULTAT PIRE, PAS MEILLEUR.** J'avais raisonné qu'un bruit
> par lecture rendait les marches artificiellement moins couplées. C'est l'inverse : avec le bruit
> porté par le voxel, la nappe se déchire **12 fois sur 12** au lieu de 9, et **aucun lot ne reste
> sous la demi-feuille** — le minimum passe de **0,116** à **0,777**.
>
> ⭐⭐⭐ **LA RAISON EST QUE LE BRUIT CESSE DE SE MOYENNER.** Un bruit retiré à chaque lecture est
> lavé par les 68 921 voxels du cube que le marcheur lit à chaque pas. Un bruit porté par le voxel
> ne l'est pas : il devient une **structure persistante** qui dévie la marche toujours dans le même
> sens. C'est plus dur, et c'est ce que fait un vrai volume.
>
> ⭐ **Zéro lecture distante.**

## 1. Le défaut, et comment il se voit

```python
v = VolumeFabrique(pas, bruit=8.0, graine=3)
v.lire(p)   # [91.25, 56.77]
v.lire(p)   # [78.27, 72.67]   ⚠ le même point
```

⚠⚠ Un vrai volume relit un voxel à l'identique : le bruit vit dans la donnée, pas dans l'acte de
lire. Une fixture qui redistribue son bruit à chaque appel n'est pas une pile, c'est un processus.

⚠ Le défaut est **invisible** pour tout ce qui a été mesuré avant `124` : `119` et `123` suivent
une marche unique, qui ne repasse jamais par le même point. C'est la première fois que deux marches
devaient lire la même matière.

## 2. La correction

Le bruit devient une fonction déterministe du **voxel** : un mélange de type splitmix64 sur
`(z, y, x, graine)` arrondis, deux avalanches, puis Box-Muller sur deux uniformes tirées du même
mélange.

| contrôle | |
|---|---|
| le même point relu rend la même valeur | ✅ |
| deux graines rendent deux matières | ✅ |
| écart-type obtenu pour **8,0** demandé | **7,948** |
| moyenne du bruit | **+0,174** |
| une pile sans bruit est inchangée | ✅ |

⚠ Les coordonnées sont **arrondies au voxel** : un voxel porte une valeur, pas un continuum. C'est
aussi ce que fait le vrai lecteur, qui indexe un tableau.

⚠⚠ L'ancien modèle reste atteignable (`bruit_porte_par_la_matiere=False`) **pour que la sonde
puisse échouer** : la batterie vérifie qu'il relit bien autre chose. Sans ce contraste, le contrôle
« le même point rend la même valeur » serait vrai de n'importe quelle implémentation.

⚠ Le débordement du mélangeur est **voulu** — c'est l'arithmétique modulo 2⁶⁴ — donc il est tu
explicitement plutôt que laissé crier à chaque lecture. Le taire sans le dire cacherait un
débordement accidentel le jour où il y en aurait un.

## 3. ⭐⭐⭐⭐ Ce que `124` devient

| | `124`, fixture défectueuse | corrigé |
|---|---:|---:|
| lots qui se déchirent | 9 / 12 | **12 / 12** |
| saut médian entre voisines | 1,020 | **1,0838** |
| saut minimum | 0,116 | **0,7769** |
| saut maximum | 20,59 | 11,9866 |
| lots couplés à la matière | 7 / 12 | 9 / 12 |
| rho au pas 16 | +0,4545 (p 0,1377) | **+0,5315** (p **0,0754**) |

Sauts triés : 0,777 · 0,906 · 0,950 · 1,011 · 1,056 · 1,078 · 1,089 · 1,095 · 1,943 · 2,469 ·
10,493 · 11,987.

⭐ **Aucun lot ne tient plus.** Sur la fixture défectueuse, trois lots restaient sous la
demi-feuille ; il n'en reste **aucun**. Huit lots se regroupent entre 0,78 et 1,10, et quatre
explosent.

⚠ Et le regroupement autour d'**une feuille** n'est pas un hasard : c'est la distance à laquelle
deux voisines basculent sur deux feuilles adjacentes. La déchirure la plus fréquente est d'exactement
une feuille.

⚠⚠ Le lien précoce se renforce sans devenir établi : rho passe de +0,4545 à **+0,5315**, p de
0,1377 à **0,0754**. Sur douze lots, ça **cesse un peu moins** de rejeter, ça ne prouve toujours
rien. Un automate ne peut toujours pas prédire la déchirure au pas 16.

## 4. ⚠⚠ Ce que ça dit de la méthode

`125` a établi qu'une fixture à réponse **unique** ne peut pas produire la panne d'une boucle. Celle-ci
en ajoute une autre, différente : **une fixture dont le bruit n'est pas porté par l'objet ne peut
pas produire les pannes qui viennent de deux lecteurs sur la même matière.**

⭐ Les deux se ressemblent et ne sont pas la même : la première manque une **ambiguïté**, la
seconde manque une **persistance**. Ce qu'elles ont en commun est qu'une fixture peut être juste
sur tout ce qu'elle a été écrite pour montrer et fausse sur la question suivante.

⚠ Et le prix payé est concret : les deux facteurs publiés par `124` sont faux d'un tiers sur le
compte des déchirures, et d'un facteur sept sur le saut minimum.

## 5. Ce que ça change pour le graal

- Le constat de `124` **tient et se durcit** : une marche seule ne dérive pas (`119`, `123`), la
  nappe se déchire toujours. Et maintenant elle se déchire **partout**.
- ⚠ Ce qui n'a pas bougé : la déchirure ne s'annonce pas au pas 16, donc un automate ne peut que
  constater les dégâts. `R4-P25` reste la porte.

## 6. Les registres

`R4-F52` et `R4-F53` sont **corrigés** dans leur valeur — la mesure change, pas leur énoncé. Fait
`R5-F23` (une fixture dont le bruit n'est pas porté par l'objet ne peut pas produire les pannes de
deux lecteurs sur la même matière). Aucune porte ouverte.

## Reproduire

```bash
uv run python src/nappe/la_nappe_se_dechire_t_elle.py \
    --json docs/mesures/la_nappe_se_dechire_t_elle.json   # douze graines, ~30 min
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier
```

⚠ **Tout est analytique.** La correction vit dans `VolumeFabrique`, donc dans le module qui porte
la fixture, et pas dans les tranches qui s'en servent — une seconde pile serait deux matières
libres de ne pas s'accorder.

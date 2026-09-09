# 97 — Deux humains sur la même matière divergent de plus d'une demi-feuille, partout

> ⭐⭐⭐ **Le plancher que `95` et `96` nommaient sans pouvoir le chiffrer.** Chaque bande de
> `PHercParis4` existe en **deux révisions**, soit deux tracés humains **indépendants** de la même
> matière. Leur désaccord vaut **121,7 µm au cœur, 110,9 au milieu, 106,6 au bord** — pour une
> demi-feuille de **82 à 91 µm** (`91`). Les deux humains sont donc à **plus d'une demi-feuille**
> l'un de l'autre, **partout**, et **34 %** des points à plus d'une feuille **entière**.

![deux humains sur la même matière](images/97_deux_humains_sur_la_meme_matiere.png)

## 1. Pourquoi ce fichier, et c'est `96` qui l'a demandé

Trois observables de confiance ont été testées : le **pli** (`94`) et la **pose sur la matière**
(`95`) sont anti-prédictifs ; la **fermeture d'un tour** (`96`) a enfin le bon signe mais ne peut
pas être **calibrée**, les maillages humains ne fermant pas eux-mêmes à la demi-feuille près.

Ce qui manquait n'était donc pas l'instrument mais un **référent** — et le dépôt en télécharge un
depuis le début sans l'avoir employé. Là où les deux révisions s'accordent, la matière a dicté la
réponse ; là où elles divergent, au moins l'une des deux se trompe. **Aucun oracle n'est requis.**

⚠ Ce n'est pas ce que `85` a mesuré. `85` compare les **couvertures** — 78 453 cellules contre
50 877, des rayons médians qui diffèrent jusqu'à 15,9 % — et assère que le **classement** survit.
Une médiane de rayons ne peut pas dire **où** les deux humains ont placé la feuille différemment.

## 2. ⭐⭐⭐ Le résultat, et il est PLAT

| tiers | au plan local | au plus proche voisin ⛔ | hors ½ feuille | > 1 feuille | continuité |
|---|---:|---:|---:|---:|---:|
| cœur (9 bandes) | **121,7 µm** | 270,8 µm | 0,629 | 0,339 | ×1,7 |
| milieu (9) | 110,9 µm | 276,9 µm | 0,622 | 0,303 | ×5,9 |
| bord (10) | **106,6 µm** | 315,4 µm | 0,609 | 0,301 | ×31,0 |

Corrélation avec le rayon : **+0,081**. ⭐ **Ce n'est donc pas un problème de bord, c'est
partout** — et c'est ce qui en fait un plancher plutôt qu'une difficulté locale.

## 3. ⛔ Et la fermeture n'est pas calibrée par ce référent non plus

Le désaccord entre les deux humains ne suit **ni** le rayon (+0,081), **ni** la rupture de
continuité (−0,097), **ni** la fermeture de `96` (**+0,079**).

⛔ **Là où les deux humains divergent n'est donc pas là où la fermeture échoue.** L'observable de
`96` reste sans étalon, et ce référent-ci ne le lui fournit pas.

## 4. ⛔⛔ L'estimateur réfuté, gardé — et c'est le facteur qui compte

Au plus proche voisin, le désaccord rend **270 à 315 µm** contre **107 à 122 µm** au plan local,
soit un facteur **2,2 à 3,0**.

Les rangs de l'ancienne révision sont espacés d'environ **800 µm**, donc un point à mi-chemin entre
deux rangs en est loin **même si les deux surfaces coïncident exactement**. La fixture le montre
directement : sur deux surfaces **identiques**, le plus proche voisin rend déjà une distance non
nulle, tandis que la distance au plan rend zéro.

> ⭐ **Publier le premier nombre aurait été publier une limite de GRILLE comme une limite de
> MATIÈRE** — le péché nº 1 de ce dépôt.

⚠ Le plan local est l'ajustement par plus petite valeur propre de la covariance des douze plus
proches points : la normale est le vecteur propre du plus petit écart, donc la distance rendue est
celle à la **surface** et non à un échantillon d'elle.

## 5. ⚠⚠⚠ Une garde à moi qui supprimait ce qu'elle devait laisser mesurer

Mon critère de bord — *« mes voisins sont-ils tous du même côté ? »* — était d'abord mesuré dans
l'**espace**. Or là il mélange deux choses : être au **bord** d'une couverture, et être **loin** de
la surface.

Mesure du défaut : sur deux plans séparés de 2 avec des voisins à 2,4 de distance moyenne, le
rapport **ne descendait jamais sous 0,354**. Appliqué au réel, il aurait donc écarté **exactement**
les points où les deux humains divergent le plus.

> **Une garde qui supprime ce qu'elle doit laisser mesurer est pire qu'aucune garde.**

Mesuré dans le **plan tangent**, il ne voit plus que le bord — et le désaccord publié **double**,
de 53 à 122 µm.

⚠ Le critère est **borné dans [0, 1]** par construction, et son défaut est **mesuré sur fixture**
et non choisi : 0,13 à l'intérieur d'un nuage, 0,49 sur sa bordure, donc 0,35 tombe entre les deux.
Le balayage est publié.

## 6. ⚠⚠ Le confondant de couverture, traité avant tout le reste

L'ancienne révision ne couvre que **65 %** de l'étendue en z de la récente (119 rangs contre 184).
Sans restriction, le vecteur moyen de A vers B valait **5918 µm**, dominé par **5567 en z** —
c'est-à-dire qu'on mesurait la couverture et non le désaccord.

Restreint au recouvrement en z, il tombe à **8 à 38 µm** : ⭐ **il n'y a donc aucune translation
systématique entre les deux tracés.** Le désaccord est réel et local.

⚠ C'est une restriction de **couverture dans un paramètre naturel**, pas un seuil sur la quantité
mesurée — la différence compte, un seuil sur la mesure serait circulaire.

## 7. ⭐⭐⭐ Ce que ça change pour le graal, et c'est plus lourd que la calibration cherchée

Le prix demande d'automatiser un travail dont **l'état de l'art ne reproduit pas sa propre sortie à
une feuille près** : deux passes humaines sur la même matière divergent d'une demi-feuille en
médiane et d'une feuille entière sur un tiers des points.

> ⛔ **La cible d'un automate ne peut donc pas être « égaler le maillage humain » — cette cible n'a
> pas de valeur unique.** Elle doit être un critère que la **matière** tranche, pas un maillage.

⭐ Et ça donne un sens neuf aux trois échecs précédents : `94` et `95` cherchaient un signal qui
prédise l'écart **à un maillage humain**, et `96` un signal calibré **contre** lui. Les trois
mesuraient contre une règle dont on sait maintenant qu'elle bouge de plus d'une demi-feuille selon
qui la tient.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger --toutes-revisions
uv run python src/nappe/deux_humains_sur_la_meme_matiere.py --verifier
uv run python src/nappe/deux_humains_sur_la_meme_matiere.py \
    --json docs/mesures/deux_humains_sur_la_meme_matiere.json
uv run python src/figures/figure_deux_humains_sur_la_meme_matiere.py --verifier
```

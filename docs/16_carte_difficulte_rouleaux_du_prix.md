# Quel rouleau du Grand Prize attaquer en premier ? — la géométrie répond

2026-08-18. Première mesure de ce dépôt portant sur **les rouleaux du prix eux-mêmes**.

---

## 1. La question, et pourquoi elle était sans réponse

Le **Grand Prize 2027** (800 000 $ en première place, 25 juin 2027) porte sur **13
rouleaux**, et **aucun n'a de trace publiée** — vérifié : `PHerc0358/segments/` est vide.
Nos autres instruments jugent une trace contre le volume ; sur un rouleau non tracé ils
n'ont rien à mesurer.

Mais `00` §1 nomme la difficulté centrale en une phrase :

> *« Deux spires voisines sont à 300 µm ; une feuille fait 40 µm. Là où le rouleau est
> comprimé, cet écart tombe à zéro. »*

Cet écart-là se mesure **sans trace**, sur les **prédictions de surface** que les 13
publient. Et il répond à une question que personne n'a posée publiquement avec un
chiffre : **par lequel commencer ?**

## 2. La mesure

`analysis/src/espacement_spires.py`. Le long d'une ligne qui traverse les spires, les
surfaces prédites forment des groupes ; l'écart entre groupes successifs **est** l'écart
inter-spires.

⚠ **Une « surface » est un groupe de voxels, pas un voxel** : à 18,7 µm une feuille en
fait un ou deux, et compter chaque voxel rendrait des écarts de 1 partout — une mesure
de la résolution, pas du rouleau.

⚠ **L'estimateur n'a pas besoin de l'ombilic.** Une ligne oblique voit un écart *plus
grand* que le vrai ; seule la perpendiculaire voit le vrai. On mesure donc le long de x
**et** de y et on garde **le plus petit**. Ça évite de dépendre de l'axe d'enroulement,
que `06` §2.3 n'a toujours pas établi.

⚠ **Niveau 1 de la pyramide et pas 2** : au niveau 2 (37,4 µm) toute la plage utile tient
dans **8 voxels**, et les trois seuils rendaient trois lignes identiques. Au niveau 1
(18,7 µm) l'écart fait 8 à 16 voxels — encore quantifié, mais lisible.

⚠ **La prédiction publiée est BINAIRE** (valeurs 0 et 255 : le seuil est déjà appliqué,
`th0.2` figure dans le nom du fichier). Balayer le seuil ne peut donc rien dire, et
l'outil le **signale** au lieu d'imprimer N lignes identiques qui ressembleraient à une
robustesse.

⚠⚠ **Les 13 partagent la même prédiction de surface** — modèle `m7`, seuil 0,2, même
date d'entraînement — donc la comparaison entre eux ne mélange pas les modèles. Et le
témoin l'a aussi.

## 3. 🎯 Le tableau, avec son témoin

Témoin : **`PHercParis4`**, un rouleau qu'on a su **dérouler ET lire**, même prédiction,
pas physique quasi identique (19,2 µm contre 17,3–18,7).

| rouleau | écart médian | p10 | min | **< 150 µm** |
|---|---:|---:|---:|---:|
| **PHerc0125** | **150 µm** | 132 | 131 | **59 %** |
| **PHerc1218** | 156 µm | 121 | 121 | **43 %** |
| PHerc0257 | 169 µm | 150 | 131 | 21 % |
| PHerc1545 | 169 µm | 150 | 131 | 42 % |
| PHerc1447 | 173 µm | 138 | 121 | 30 % |
| **⭐ PHercParis4 — LU** | **173 µm** | **134** | **134** | **18 %** |
| PHerc0191 | 187 µm | 150 | 131 | 15 % |
| PHerc0211 | 187 µm | 150 | 131 | 30 % |
| PHerc0358 | 187 µm | 150 | 140 | 18 % |
| PHerc0813 | 187 µm | 150 | 140 | 16 % |
| PHerc0826 | 187 µm | 150 | 131 | 19 % |
| PHerc1203 | 187 µm | 150 | 131 | 28 % |
| **PHerc0800** | 190 µm | 173 | 138 | **2 %** |
| **PHerc0268** | **225 µm** | 173 | 156 | **0 %** |

## 4. Ce que ça dit

**⚠⚠ Neuf des treize sont aussi lâches ou plus que le rouleau déjà lu.** La compression
n'est donc **pas** ce qui les a empêchés d'être tracés — pas pour ceux-là.

> Un rouleau plus lâche que celui qu'on a su lire n'a pas d'excuse géométrique.

Ce qui reste comme causes candidates, non départagées ici : la **qualité du scan**
(énergie et contraste diffèrent : 113 keV et 116 keV contre 78 keV pour le témoin), la
qualité de la **prédiction** sur ces volumes-là, ou simplement que **personne n'a
essayé** — 33 échantillons sur 45 n'ont aucune surface tracée (`00` §6).

**🎯 Et la réponse actionnable :** **`PHerc0268` et `PHerc0800`** sont les plus lâches —
**0 % et 2 %** de zones sous 150 µm, contre 18 % pour le témoin. Ce sont eux qu'on
attaquerait en premier si la géométrie était le seul critère.

⚠ À l'autre bout, **`PHerc0125`** a **59 %** de ses zones sous 150 µm : c'est le seul du
lot nettement plus comprimé que le témoin, et le seul pour lequel « c'est trop serré »
est une explication plausible.

## 5. ⚠ Ce que la mesure ne dit PAS

1. **Elle est quantifiée** : au niveau 1 les valeurs tombent sur 121 / 131 / 138 / 150 /
   156 / 169 / 173 / 187 / 190 / 225 µm, c'est-à-dire 7 à 12 voxels. Le **classement
   fin** entre deux rouleaux à 187 µm n'a pas de sens ; les **extrêmes** en ont un.
2. **27 chunks par rouleau**, pris dans le tiers central en z et la moitié centrale en
   x/y. C'est un sondage, pas une carte complète — les bords et le cœur ne sont pas
   couverts, et c'est justement au cœur qu'un rouleau s'effondre.
3. ⚠ **La médiane et la queue ne classent pas pareil** : `PHerc1545` et `PHerc0257` ont
   la même médiane (169 µm) et **42 % contre 21 %** de zones serrées. La colonne
   « < 150 µm » porte plus d'information que la médiane, et il faut lire les deux.
4. Elle mesure ce que la **prédiction** voit, pas le papyrus. Une prédiction qui rate
   des feuilles rendrait des écarts trop grands — et c'est le sens qui flatte le
   rouleau.

## Reproduire

```bash
./tools/carte_difficulte.sh docs/carte_difficulte
cd inference_xpu
uv run python ../analysis/src/table_difficulte.py ../docs/carte_difficulte
```

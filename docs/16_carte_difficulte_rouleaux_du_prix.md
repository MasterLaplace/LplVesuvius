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

---

## 6. 🎯 La qualité de scan : mesurée, et elle n'excuse pas non plus

`analysis/src/separabilite_scan.py`. Le tableau des goulots de `2026_open_problems`
nomme littéralement ce qui manque — *« What would help : **scan-quality metrics** »* —
et définit le défaut dans ses propres mots : *« some regions lose **effective
separability** between layers »*.

**La mesure est un d′**, l'indice de discriminabilité entre les sommets (feuille) et les
creux (interstice) d'une ligne traversant les spires. Sans dimension, donc indépendant
du gain du détecteur.

### Le témoin est le bon

`PHerc0139` a été **tracé, et son titre retrouvé** — et il possède un scan au
**protocole exact des 13** (9,362 µm / 1,2 m / 113 keV).

| rouleau | d′ médian | p10 | min | **sous 1,0** |
|---|---:|---:|---:|---:|
| PHerc0125 | 1,62 | 0,83 | 0,52 | 24 % |
| PHerc0211 | 1,55 | 1,13 | 0,89 | 5 % |
| PHerc1447 | 1,53 | 1,28 | 0,92 | 6 % |
| PHerc0358 | 1,53 | 1,15 | 0,88 | **4 %** |
| PHerc1218 | 1,52 | 0,95 | 0,92 | 24 % |
| PHerc0257 | 1,50 | 1,15 | 0,79 | 11 % |
| **⭐ PHerc0139 — TRACÉ ET LU** | **1,45** | **1,15** | **1,00** | **0 %** |
| PHerc0813 | 1,43 | 0,97 | 0,85 | 15 % |
| PHerc1203 | 1,42 | 0,90 | 0,68 | 19 % |
| PHerc0191 | 1,42 | 0,94 | 0,68 | 23 % |
| PHerc1545 | 1,40 | 0,96 | 0,78 | 12 % |
| PHerc0826 | 1,40 | 0,86 | 0,74 | 13 % |
| PHerc0268 | 1,39 | 1,10 | 0,48 | 9 % |
| PHerc0800 | 1,37 | 0,97 | 0,93 | 20 % |

**Six des treize ont une séparabilité médiane égale ou meilleure que le témoin.**

### ⚠⚠ Mais c'est la QUEUE qui sépare, pas la médiane

Le témoin a une propriété qu'**aucun** des treize ne partage : **0 % de zones sous
d′ = 1,0**, et son minimum vaut exactement 1,00. Les treize en ont **4 % à 24 %**.

> La médiane dit qu'ils se valent. La queue dit que le rouleau qu'on a su lire n'avait
> **aucune** région indissociable, et que tous les autres en ont.

⚠ Réserve honnête : **15 à 35 chunks par rouleau**. Un « 0 % » sur 24 chunks est
compatible avec une petite fraction de mauvaises régions non tombée dans le sondage. Ce
qui se défend est l'**ordre de grandeur** — 0 contre 4–24 % — pas le zéro exact.

### 🎯 Ce que les deux cartes disent ensemble

| cause supposée pour les 13 | verdict |
|---|---|
| les spires sont trop serrées | ❌ 9 sur 13 sont **plus lâches** que le rouleau lu |
| le scan est trop voilé (médiane) | ❌ 6 sur 13 sont **aussi séparables** ou mieux |
| ⚠ le scan a des **poches** indissociables | ⭐ **oui** — 4 à 24 % contre 0 % pour le témoin |

**La difficulté n'est pas globale, elle est locale.** C'est exactement ce que la page
dit — *« scan quality is local. A scan can hold excellent regions and
nearly-impossible-to-unwrap ones in the very same volume »* — et c'est maintenant
chiffré par rouleau.

⭐ **Actionnable** : `PHerc0358` a la meilleure combinaison — d′ médian 1,53 (au-dessus
du témoin) et seulement **4 %** de zones indissociables, le minimum des treize. C'est
lui qu'on attaquerait en premier.

### ⚠⚠ Et une limite qui vaut pour NOS DEUX instruments

Le d′ **et** l'écart feuille↔trace comparent des scans **à résolution égale**, jamais
entre résolutions. Mesuré sur le même rouleau, mêmes segments :

| campagne | profondeur de pile | écart médian à la trace | tiers central |
|---|---:|---:|---:|
| 9,362 µm (28 couches) | 262 µm | 28 µm | 66 % |
| 2,399 µm (109 couches) | 261 µm | 44 µm | 49 % |
| 1,129 µm (116 couches) | **131 µm** | 18 µm | 59 % |

Le scan grossier semble « meilleur ». Il ne l'est pas : à 28 couches l'écart se mesure
par pas de 9,4 µm, donc un pic à une couche du centre **lit** 9 µm là où le scan fin
lirait sa vraie valeur. Et la pile à 1,129 µm ne couvre que **131 µm** — la moitié des
autres — donc elle **tronque**, et son 18 µm est une borne inférieure.

> **Deux instruments, une même règle : ils classent des rouleaux à qualité de scan
> comparable. Ils ne disent rien sur « faut-il scanner plus fin ».** Le prétendre
> serait lire un artefact de quantification comme un résultat.

# 94 — Le froissement désigne-t-il où le transfert échoue ? Non — il désigne l'inverse

> ⛔⛔⛔ **Il manque au marcheur un signal qui lui dise, SANS SUPERVISION, qu'il est dans la zone
> où le pas géométrique ne suffit plus. Le pli était le candidat évident. Mesuré sur les 28 bandes
> humaines de `PHercParis4` : il est ANTI-prédictif. 15,2 µm au cœur, 3,8 au bord — le plus faible
> exactement là où le transfert casse (×31). Un marcheur qui s'en servirait signalerait le cœur,
> où tout est propre, et se tairait au bord.**

![le froissement mesure la rugosité](../images/94_le_froissement_mesure_la_rugosite.png)

## 1. Pourquoi cette question est celle du graal

`93` établit **où** le pas géométrique échoue : au bord, où la surface est brisée (`92`, ×31) et
les spires désalignées (×4,18). Ce qui manque n'est plus la carte, c'est un **signal que le
marcheur peut lire tout seul**. Le **pli** est le candidat que le dépôt a déjà **mesuré** :
[`75`](75_registre_des_taches.md), section « Une cellule peut-elle savoir qu'elle a tort », le
trouve prédictif de l'erreur **par cellule** — 8 bras sur 8 chez le raccrochage, et **un bras
sauvé** en jetant les dix pour cent les plus pliées, là où le témoin au hasard n'en sauve aucun.
Ce fichier le teste là où la carte d'échec existe.

⚠⚠⚠ **Et cette tranche-là bornait déjà sa portée**, ce que ma première version de ce document
avait effacée. Elle écrit : *« ce que ça ne dit pas, c'est que le pli soit une bonne confiance **en
général** ; il l'est là où il y a des plis »* — et le pas normal **lissé** en a si peu que son
classement fait **pire que le hasard** (+7,1 µm contre le témoin). Ce document ajoute la seconde
borne, sur l'autre axe : **à travers les rayons, le signe s'inverse**.

⚠ Et une erreur à moi, gardée : j'avais attribué ce résultat à `78`, qui est *Cinq rouleaux
publient leur axe*. ⭐ **Une citation qu'on ne vérifie pas est une citation qu'on invente**, et
elle rendait ce résultat négatif plus spectaculaire qu'il n'est.

## 2. ⛔⛔⛔ La réponse est non, et c'est pire que neutre

| tiers | froissement | désalignement | continuité |
|---|---:|---:|---:|
| cœur (9 bandes) | **15,2 µm** | ×1,88 | ×1,7 |
| milieu (9) | 10,1 µm | ×1,80 | ×5,9 |
| bord (10) | **3,8 µm** | ×3,67 | **×31,0** |

Corrélations : **−0,957** avec le rayon, −0,470 avec le désalignement, **−0,825** avec la rupture
de continuité.

⚠⚠ Normaliser par la sagitta retire le rayon (−0,957 → **−0,404**) mais **pas le signe**
(−0,678). Ce n'est donc pas un artefact d'échelle qu'on pourrait diviser.

## 3. ⭐⭐⭐ Ce que le champ mesure, établi par FIXTURE et non par corrélation

`champ_de_froissement` prend la **médiane** d'un voisinage 3×3, et une médiane rend la valeur
centrale sur un voisinage symétrique. Le champ est donc **exactement aveugle à la courbure
lisse**. Mesuré sur des cylindres fabriqués, dont on connaît la réponse :

| cas | R = 5 mm | R = 20 mm | rapport |
|---|---:|---:|---:|
| cylindre parfait | **0,00 µm** | **0,00 µm** | — |
| + axe courbe (celui que `90` mesure) | **0,00 µm** | **0,00 µm** | — |
| + bruit 5 µm | 7,54 | 6,87 | **×1,10** |
| + bruit 20 µm | 29,10 | 27,06 | ×1,08 |

⭐⭐ **Donc le champ mesure la rugosité locale du maillage, et presque sans dépendre du rayon.**

## 4. ⭐⭐ Et le verdict devient plus fort, pas plus faible

Le réel tombe d'un facteur **×5,2** entre 4,1 et 23,8 mm là où la rugosité seule n'en donnerait
que **×1,1**. Les maillages humains sont donc **cinq fois plus lisses au bord qu'au cœur**.

Or un maillage localement lisse qui porte des **sauts de trente millimètres** (`92`) et des spires
**désalignées** (`93`) est un maillage qui a **enjambé ce qu'il ne pouvait pas suivre**.

⭐⭐⭐ **La douceur au bord n'est pas de la qualité : c'est la signature d'un pontage.** Un signal
de confiance bâti dessus classerait l'abandon comme une réussite — le pire mode de panne possible
pour un automate qu'on lance sans surveillance.

## 5. ⚠⚠⚠ Une cause que j'ai publiée puis rétractée avant de la committer

J'avais expliqué la chute en 1/R par la **sagitta** d'un cercle échantillonné au pas `s`,
`s²/(8R)`. L'accord numérique était frappant : rapport mesuré/prédit de **1,11 en médiane** sur
vingt-huit bandes (0,68 à 1,81).

**C'était une coïncidence, et la fixture la réfute d'un coup** : la sagitta prédit **20,2 µm** à
R = 5 mm là où le champ rend **zéro**.

⭐ **Une corrélation sur vingt-huit points ne vaut pas une fixture dont on connaît la réponse.**

⚠ La sagitta est **gardée** dans le code, réfutée et nommée, avec son rapport toujours publié :
un accord de cet ordre réapparaîtra à qui refera la mesure, et le trouver sans trouver sa
réfutation à côté conduirait à le republier. Une coïncidence nommée coûte moins cher qu'une
coïncidence redécouverte.

## 6. ⚠⚠ Avertissement de niveau — ceci ne rétracte pas `75`

`75` compare des **cellules** à l'intérieur d'une même marche, à rayon presque constant ; ce
fichier compare des **bandes** entre elles, à travers les rayons. **Les deux peuvent être vrais.**

⭐ Et ça compte pour l'objectif : une marche de 31 spires change le rayon d'un **facteur six**.
Tout signal de confiance qu'elle emploie doit donc être **vérifié à travers les rayons**, ou il
classera par rayon en croyant classer par difficulté.

## 7. ⚠⚠ Deux angles morts d'outillage attrapés dans cette tranche

**La revendication porteuse n'était pas publiée.** La fixture ne vivait que dans `verifier()`,
donc ses nombres n'étaient pas citables par un document : la conclusion « le champ mesure la
rugosité » aurait dû être crue sur parole. `ce_que_le_champ_voit()` est désormais appelée par
`mesurer()`, par la batterie **et** par la figure — un seul calcul pour les trois usages.

**Le garde de largeur ne lisait que la prose du bas.** Une ligne de **verdict** écrite dans un
panneau pouvait sortir du cadre et se faire **couper à mi-mot** sans que rien ne le dise. C'est
l'angle mort que le garde de glyphes avait déjà révélé, un cran plus loin. `Tracee` retient
maintenant la **position** avec le texte, et `textes_debordants` en fait un contrôle — qui a
attrapé **une seconde ligne coupée que l'œil avait laissée passer**, parce qu'elle finissait pile
au bord.

⚠ Ce que ce garde voit et ce qu'il ne voit pas est écrit dans sa docstring : il mesure contre le
bord de la **toile**, pas contre celui du panneau qui contient le texte, parce qu'une position ne
dit pas dans quel cadre elle vit.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/le_froissement_mesure_la_rugosite.py --verifier
uv run python src/nappe/le_froissement_mesure_la_rugosite.py \
    --json docs/mesures/le_froissement_mesure_la_rugosite.json
uv run python src/figures/figure_le_froissement_mesure_la_rugosite.py --verifier
```

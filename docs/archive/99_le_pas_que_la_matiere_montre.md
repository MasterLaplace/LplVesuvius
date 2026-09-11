# 99 — Quel pas la matière montre-t-elle ? `98` cesse d'auditer et se met à décider

> ⭐⭐⭐ **Le pas que la matière montre n'est pas le pas nominal, et l'écart n'est pas marginal :**
> **198,9 µm au cœur et 214,05 au bord** contre **173** publié, et **plus de 81 %** des cellules
> diffèrent de plus d'un dixième du nominal. Un automate qui avancerait d'un pas constant se
> tromperait donc quatre fois sur cinq.
>
> ⭐⭐ **Et la part de cellules où la matière répond corrèle à −0,845 avec la rupture de
> continuité** — le signal au bon signe le plus fort de toute la campagne.

![le pas que la matière montre](../images/99_le_pas_que_la_matiere_montre.png)

## 1. Pourquoi ce fichier, et c'est l'item A du bloc de reprise

`98` a livré le premier critère dont le seuil ne vient ni d'un maillage ni d'un réglage. Mais il
**audite** : il vérifie un pas qu'on lui donne. Un automate a besoin de l'inverse — qu'on lui
**dise** le pas. Le même filtre le fait en **balayant** la distance et en gardant celle que la
matière accorde le mieux.

⚠ La dégénérescence est levée en fixant **k = 1** : un segment de `2p` traversé par deux
interstices est indiscernable d'un segment de `p` traversé par un, c'est la même matière lue deux
fois. Chercher `p` **à k fixé** rend la distance à la feuille **voisine**, qui est la question de
l'automate.

⚠⚠ La fenêtre est **dérivée** : de la **moitié au double** du nominal. En deçà on retrouverait la
feuille de départ, au-delà on peut sauter la voisine. C'est le raisonnement que
`la_longueur_locale_du_pas` tient déjà sur l'autre objet — ⭐ et c'est pourquoi ce fichier ne le
réécrit pas : il porte le balayage là où sont les **92 vrais transferts**, avec la barre de `98`.

## 2. ⭐⭐ Ce qui rend le balayage abordable, et c'est exact plutôt qu'approché

Les candidats sont **emboîtés** : le segment du plus long les contient tous, donc **un seul aller**
au volume suffit et chaque candidat se relit dedans. Lire 31 segments séparément coûterait
**dix-neuf fois** `98` pour la même information.

⚠ Et chaque candidat est rendu sur le **même nombre d'échantillons**. Ce n'est pas un détail : le
modèle nul ne dépend que de ce nombre, donc c'est ce qui garantit que la barre est la même pour
toutes les longueurs.

## 3. ⛔⛔⛔ Le premier résultat était un artefact, et le nul l'a montré

La première version rendait un pas médian de **147 µm** sur le vrai volume. Contrôle : la **même
recherche sur du bruit pur** rendait **147 µm** aussi.

> ⭐ **Le « pas que la matière montre » était donc indiscernable du biais de la recherche.**

La cause est mesurable : un segment court rééchantillonné sur le même nombre de points est
**sur-échantillonné**, donc plus lisse, donc il corrèle mieux avec un gabarit lisse. Le nul par
candidat le chiffre : **0,1582** au plus court contre **0,0925** au plus long, soit **×1,71**.

⭐⭐⭐ **Et la leçon se généralise :**

> **Un modèle nul doit s'appliquer à CHAQUE quantité qu'une recherche rapporte, pas seulement à sa
> confiance.** Le nul du score existait et était juste ; celui de la longueur **choisie** manquait,
> et c'est là que vivait l'artefact.

Après calibration par candidat, la même recherche sur du bruit pur choisit **207,6 µm** pour une
fenêtre centrée à 216, avec un histogramme quasi plat.

## 4. ⚠⚠⚠ Et une seconde erreur de nul, corrigée avant celle-là

La barre comparait le **maximum sur 62 essais** (31 candidats × 2 polarités) au nul d'**un seul**
test. C'est l'erreur des comparaisons multiples, et elle rend la mesure **incapable d'échouer** :
avec la mauvaise barre, la part lue sautait à **0,98**.

| barre | valeur |
|---|---:|
| nul d'un seul essai (`98`) | 0,3311 |
| nul du balayage, non calibré | 0,512 |
| **nul du balayage, calibré** | **4,357** (en écarts-types) |

⚠ Les trois sont publiées, parce que leur **écart** est ce qui montre l'ampleur de chaque
correction.

## 5. ⭐⭐⭐ Le contrôle qui décide si la longueur est une mesure

La distribution des longueurs retenues est confrontée à celle que le **même** balayage retient sur
du **bruit pur**, au-dessus de la **même** barre et avec le même rejet des butées.

| | mesuré |
|---|---:|
| part du nul au-dessus de la barre | **1,03 %** |
| médiane réelle | **198,9 µm** |
| médiane du nul | 276,8 µm |
| Kolmogorov-Smirnov | **D = 0,603, p = 1,4·10⁻⁵** |

⭐ **Les deux distributions diffèrent décisivement**, donc la longueur porte de l'information — ce
qui n'était pas le cas avant calibration, et que seule cette comparaison-là pouvait établir.

## 6. ⭐⭐⭐ Le résultat

| tiers | utilisable | butée | pas µm | / nominal | > 10 % | sur la feuille | continuité |
|---|---:|---:|---:|---:|---:|---:|---:|
| cœur (9 bandes) | **0,750** | 0,142 | **198,9** | 1,15 | 0,837 | 0,538 | ×1,7 |
| milieu (9) | 0,742 | 0,100 | 198,9 | 1,15 | 0,811 | 0,511 | ×5,9 |
| bord (10) | **0,542** | 0,117 | **214,05** | 1,24 | 0,824 | 0,429 | ×31,0 |

⭐⭐ **La part de cellules où la matière répond corrèle à −0,845 avec la rupture de continuité** —
0,750 au cœur contre 0,542 au bord. C'est le signal au bon signe le plus fort de la campagne, et
il est **au niveau de la bande**, donc utilisable pour dire où un automate doit ralentir.

⭐ **Et le pas montré dépasse le nominal de 15 à 24 %**, avec **plus de 81 %** des cellules à plus
d'un dixième du nominal. Un pas constant est donc faux quatre fois sur cinq.

⚠⚠ **Ce que ça ne dit pas.** Le pas montré (199 µm) dépasse aussi celui que `91` lit sur les
transferts humains (**164 µm**) et celui de l'atlas (**182,4**), de 9 à 21 %. `97` a établi que le
maillage humain n'a pas de valeur unique, donc un désaccord est attendu — mais son **ampleur** n'est
pas expliquée ici, et il faut le dire plutôt que choisir le chiffre qui arrange.

## 7. ⚠⚠ Une butée n'est pas une mesure

Quand l'optimum tombe sur une extrémité de la fenêtre, la matière dit *« au moins ceci »*, pas
*« ceci »*. Ces cellules — **10 à 14 %** — sont comptées à part et retirées de l'utilisable, sinon
une limite de **fenêtre** se publierait comme une limite de **matière**.

## 8. ⛔⛔⛔ Ce que `105` corrige ici : le sélecteur de ce fichier est biaisé haut

Le nombre publié plus haut — **198,9 µm** — a été obtenu par `pas_montre_calibre`, et
[`105`](105_le_balayage_rend_il_le_pas_injecte.md) mesure que **ce sélecteur ne rend pas la période
qu'on lui injecte** : sur des profils fabriqués dont la réponse est exacte il lit **+5,0 %** trop
haut, jusqu'à **+11,2 %**, et sur le vrai volume — 28 bandes × 120 cellules, **mêmes lectures** — il
lit **194,6 µm** là où le sélecteur brut lit **164,3**, soit **+18,4 %**.

⛔⛔ **Et le contrôle aller-retour de ce fichier ne pouvait pas le voir** : il relit par
`pas_montre`, le sélecteur **brut**, alors que `mesurer` appelle `pas_montre_calibre`. *Une
vérification qui n'emprunte pas le chemin de la production.*

⭐⭐ **Le mécanisme** : le nul par candidat décroît avec la longueur (µ de **0,1582** à **0,0925**),
donc la calibration favorise les candidats longs — sur 173 µm injectés elle retient **181,7** avec
un accord brut de **0,9882** contre **1,0000** pour le choix brut. Elle est juste pour *« ce
candidat dépasse-t-il le bruit ? »* et fausse pour *« lequel colle le mieux ? »*.

⚠ **La calibration reste indispensable comme GARDE** — sans elle ce fichier lisait 147 µm sur le
vrai volume comme sur du bruit pur. Ce qui change est le **choix** parmi les candidats admis, pas la
garde. ⚠⚠ Le nombre publié ici n'a **pas** été recalculé : le relire demande de relancer la mesure,
pas de le diviser par un facteur.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/le_pas_que_la_matiere_montre.py --verifier
uv run python src/nappe/le_pas_que_la_matiere_montre.py \
    --json docs/mesures/le_pas_que_la_matiere_montre.json
uv run python src/figures/figure_le_pas_que_la_matiere_montre.py --verifier
```

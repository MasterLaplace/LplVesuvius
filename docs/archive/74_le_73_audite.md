# 74 — `73` audité : ce qui tient, ce qui se corrige, et le rouleau qu'il a écarté

> Écrit le 2026-09-03, après lecture intégrale de `73`. Même méthode que `71` : chaque
> revendication porteuse est **rejouée contre la source**, pas contre le résumé qui en parle.
> Mesure dans l'arbre : `src/excision/les_indices_de_spire.py` (11 contrôles).

---

## 0. Le verdict en une ligne

`73` a fait ce que `69` n'avait pas fait : **il a lu le dépôt.** Ses quatre livrables portent,
ses attaques sur l'article sont largement fondées, et sa découverte de tête est réelle.

Ce qui suit corrige trois choses, dont **une qui change la cible du plan**.

| revendication de `73` | verdict |
|---|---|
| §0 — `windcheck` compte des auto-intersections | ✅ **confirmé à la source** |
| §2.6 — les 15 segments de l'article §5.7 sont des `auto_grown_*` | ✅ **confirmé, 14 + 1 `z_dbg`** |
| §2.7 — l'article dit « 13 of 16 » et « 14 of 16 » | ✅ **confirmé, et les deux sont dans le fichier** |
| §2.3 — 113 µm n'est pas centre à centre | ✅ **conclusion juste**, ⚠ **mécanisme périmé** |
| §4 — les segments publiés portent leur numéro de spire | ✅ **réel**, ⚠⚠ **sous-compté ×1,8** |
| §3.3 — extraire sur `PHerc0800` ou `PHerc1447` | ⚠⚠⚠ **ces deux-là n'ont aucun référent d'identité** |

---

## 1. Les trois confirmations, sans réserve

**`windcheck` compte bien des auto-intersections.** Son README s'ouvre sur
*« Self-intersection checks for Herculaneum surface traces »* et sur *« A tifxyz surface trace
can cross itself: non-adjacent parts of the traced sheet pass through one another »*. Donc
`17` a bien testé « marche de phase locale contre **auto-intersections** », et son négatif ne
porte pas sur « résidus contre **sauts de spire** ». **La réhabilitation de H5 tient**, et
c'est le point le plus utile du livrable 1 : un résultat négatif propre avait été lu comme
fermant une question qu'il n'avait pas posée.

**Les quinze segments de `PHerc1447` sont des sorties de traceur automatique** : 14
`auto_grown_<horodatage>` + 1 `z_dbg_gen_00320`, et **zéro** segment indexé. La reformulation
que `73` §2.6 propose — nommer les segments pour ce qu'ils sont — rend le résultat de §5.7
plus petit et inattaquable. À faire.

**Les deux comptes de l'article sont tous deux dans `derive_profondeur.json`**, avec des
définitions différentes : `censurees_en_bas = 13` (censurées au plafond du rendu le moins
profond) et, sous `derives`, `critere: "ecart_um"` → `n_censurees = 14` (censurées à l'une au
moins des deux profondeurs, sur `n_compare = 2`). L'article emploie les deux comme un seul
nombre. **Correctif : dire lequel est lequel**, en une incise.

---

## 2. ⚠ `73` §2.3 a raison, et pour une raison plus forte que la sienne

Sa thèse : les 113 µm de l'article ne sont pas un écart centre à centre. **C'est juste.**
L'article §5.5 le dit lui-même — *« the median gap between consecutive surfaces »* — et `44`
§4 le nomme *« une distance au plus proche voisin »*. C'est la ligne 201 de l'introduction qui
le relabellise en *« median centre-to-centre spacing between neighbouring sheets »*.

⚠⚠ **Mais son mécanisme est une phrase que `43` corrige plus loin dans le même document.**
`73` cite `43` §6quater — *« `gen_neighbor` arrête son rayon au premier échantillon au-dessus
du seuil »* — et en déduit un placement sur la **face proche de la feuille suivante**, donc
113 + épaisseur = 137–173 µm centre à centre. Or `43` va ensuite chercher le mécanisme **dans
la source** (`vc_grow_seg_from_seed.cpp`) et écrit :

> *Le rayon ne s'arrête pas au premier échantillon au-dessus du seuil : il doit d'abord
> **quitter** la nappe de départ.*

Et la conséquence mesurée est pire pour l'article que ce que `73` avance :

> *À pas fin, un seul échantillon sous-voxel interpolé sous le demi-seuil suffit pour déclarer
> « j'ai quitté la nappe ». Le rayon peut donc sortir puis **rentrer dans la même feuille**, et
> se poser sur la face proche de **sa nappe de départ**.* — écart mesuré **116 → 109 → 107 →
> 102 µm** quand `neighbor_step` est halvé trois fois.

Donc **113 µm n'est pas une propriété du rouleau : c'est la valeur d'une grandeur qui dépend
d'un réglage**, et qui varie de 14 µm sur la plage de réglages que le dépôt a explorée. La
plage annoncée par l'article, « 100–138 », **contient** cette variation.

⭐ Le correctif est donc plus large que celui de `73` : ce n'est pas seulement une étiquette à
changer, c'est un nombre à assortir de son réglage. Trois endroits :

- ligne 201 — *centre-to-centre spacing between neighbouring sheets* → **gap between
  consecutive surfaces at `neighbor_step` = …**, et « about 13 voxels » à revoir ;
- ligne 352 — *whether the sheets are 113 µm apart or 300* : l'argument (α ne dépend pas de
  l'échelle) survit, mais l'exemple doit cesser de présenter 113 comme l'écart des feuilles ;
- §5.5 — la phrase *« which is one sheet »* devient une **inférence** et non une lecture, et
  elle mérite le renvoi vers `16` (156 µm médian, p10 138) et l'atlas.

⚠ Et une réserve **contre** `73` sur son propre appui : il cite l'atlas de `winding-ruler` à
**172,8 µm** pour `PHerc1447`. Ce nombre est `lambda_med_lvlvox = 10.0` **voxels entiers de
niveau 1**, soit un pas de quantification de 17,28 µm, et son IQR publié va de **121 à
250,6 µm**. Il ne contredit 113 que par son p25. L'appui solide est `16` (156 µm médian sur le
même rouleau), pas la médiane de l'atlas.

---

## 3. ⚠⚠ La découverte de tête est réelle, et sous-comptée

`73` §4 : *« les segments publiés portent leur numéro de spire dans leur nom, et aucun
instrument du dépôt ne le lit »*, sur **57 segments, 56 spires, deux rouleaux**.

**Le fait est vrai. Le compte ne l'est pas** (`src/excision/les_indices_de_spire.py`) :

| rouleau | segments | indexés | spires | course | trous | plages | `d′ < 1` |
|---|---:|---:|---:|---|---:|---:|---:|
| **PHerc0139** | 38 | **37** | **37** | `w023`–`w059` | **0** | 0 | **4,4 %** |
| **PHerc0172** | 53 | **44** | **44** | `w052`–`w095` | **0** | 0 | — |
| PHerc1667 | 20 | 20 | 19 | `w011`–`w041` | 3 | 0 | — |
| PHercParis4 | 81 | 0 | 0 | — | — | **58** | — |
| PHerc1447 | 15 | 0 | 0 | — | — | 0 | 7,0 % |
| PHerc0800 | 6 | 0 | 0 | — | — | 0 | 2,6 % |

**101 segments indexés sur 3 rouleaux**, pas 57 sur deux. `PHerc0172` — 44 segments, plus
que `PHerc0139` — est absent de son inventaire. Et `PHercParis4` en publie 58 de plus, mais
d'une autre espèce : des **plages** (`w010-027`, `w028-037`, …), 28 distinctes, couvrant les
spires 10 à 129. Une plage nomme un intervalle, pas une feuille ; les compter avec les autres
gonflerait le référent d'un facteur cinq sur ce rouleau.

⭐⭐ **Et la propriété qui compte n'est pas le compte, c'est la continuité.** `73` §5 déclare
`[je ne sais pas]` si les indices sont consécutifs, et bâtit H1′ — *« un entier constant par
spire, consécutif entre `w_k` et `w_{k+1}` »* — en nommant `PHerc1667`, qui **saute** 13→18,
18→23, 23→28. Deux rouleaux portent au contraire une course **sans aucun trou** :
`PHerc0139` (37 spires) et `PHerc0172` (44), soit **81 spires consécutives**. « Consécutif
entre deux spires consécutives » n'est une question que là où deux spires consécutives sont
publiées : H1′ est testable, sur ces deux-là et pas sur celui qu'il a choisi.

⚠ Ce que la mesure n'établit pas, et `73` a raison de le déclarer : que `w` compte dans le
même sens sur les quatre rouleaux. « Consécutif » est ici une propriété des **noms**. Ça se
tranche en mesurant le rayon médian de `w_k` contre `w_{k+1}` sur les `tifxyz` transformés —
première ligne du lecteur, comme `73` §4 le dit.

---

## 4. ⚠⚠⚠ Le plan déploie là où le référent n'existe pas — et le bon rouleau était dans ses données

`73` §3.3 fait deux choix qui ne tiennent pas ensemble :

- **mois 1–2** : construire le prédicat d'**identité** sur les indices de spire ;
- **mois 4–7** : extraire toutes les spires sur **`PHerc0800`** (2,6 %) ou **`PHerc1447`**
  (7,0 %), choisis sur la queue de la carte dense.

Or `PHerc0800` publie **6 segments, tous `auto_grown`**, et `PHerc1447` **15, dont 14
`auto_grown`**. **Aucun des deux ne porte un seul indice de spire.** Le prédicat serait donc
validé sur un rouleau et déployé sur un autre, et ce transport est une hypothèse que le plan
n'énonce pas.

⭐⭐⭐ **Un rouleau porte les deux, et c'est `PHerc0139` :**

- **37 spires consécutives sans trou**, approuvées par des humains — le référent d'identité ;
- une carte dense sur **91 fenêtres**, au-dessus des 50–100 que `33` exige pour que le
  classement tienne ;
- une queue à **4,4 %**, **deuxième des quatorze**, devant `PHerc1447` (7,0 %) que `73`
  retenait ;
- et il est **déjà transformé dans le repère du régime du prix** (`68` §4).

**Pourquoi `73` ne l'a pas vu** : son fichier de carte dense s'appelle
`_TEMOIN_PHerc0139.json`. Il l'a lu comme un témoin, donc l'a écarté de son classement de
candidats — alors que le préfixe dit son rôle dans **une autre** mesure, pas sa qualité.

⚠ Une réserve honnête, qui est la sienne (`73` §5) et que je reprends : rien ne montre encore
qu'un rouleau à 4,4 % se trace mieux qu'un rouleau à 22,8 %. `55` dit que le mur 1 vient de la
graine, pas du scan. Choisir `0139` ne se justifie donc **pas** par sa queue seule — il se
justifie parce que c'est le seul endroit où l'on peut **mesurer si le prédicat marche**.

---

## 5. ⚠ Ma propre erreur, corrigée par le contrôle et non par une relecture

La première version de `les_indices_de_spire.py` assertait que *« aucun rouleau ne porte à la
fois un référent d'identité et une carte dense »* — les deux ensembles seraient disjoints.
**Le contrôle a échoué**, et il avait raison : `PHerc0139` porte les deux, et c'est toute la
conclusion du §4 ci-dessus.

J'allais écrire une recommandation (« validez ici, déployez là-bas, et déclarez le
transport ») **strictement plus faible** que celle que la mesure impose (« un seul rouleau
permet de faire les deux au même endroit »). C'est le motif habituel de ce dépôt, et il vaut
d'être noté une fois de plus : **une assertion qui échoue est la seule chose qui sépare une
conclusion d'une conviction.**

---

## 6. Ce qui reste ouvert de `73`, non vérifié ici

- **§2.2** (une surface dans l'interstice donne α ≈ 0) — `73` le dit lui-même : ça repose sur
  une lecture de §3.6, pas sur une mesure. La translation d'un demi-pas tranche en un rendu,
  et l'outil existe (`44`, « plancher du hasard »).
- **§2.4** (le témoin négatif de §6.5 traverse des faces, donc de l'encre) — l'argument
  géométrique est solide sur le papier ; il se mesure en comptant les rubans traversés.
- **§2.8** (α n'a jamais vu de courbe ROC) — juste, et la ROC qu'il propose sur 57 positifs
  devient **101** avec le compte corrigé.
- **§2.5** (la flèche axiale) — `laxe_nest_pas_une_ligne.py` donne la dérive sur Scroll 1 ; la
  réserve se déclare, elle ne se mesure pas sur le rouleau de §5.5.

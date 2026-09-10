# 102 — Combien de pas la matière porte : le premier acquis positif, et sa borne

> ⭐⭐⭐ **Interroger la matière porte 2,00 pas là où l'automate naïf en porte 0,00**, sur les 28
> bandes. C'est la première fois de la campagne que la voie « interroger la matière » **bat**
> l'état de l'art, au lieu de simplement ne pas être réfutée.
>
> ⚠⚠⚠ **Mais la portée est CENSURÉE, et ça se dit avant le résultat** : **17 bandes sur 28**
> (61 %) ont au moins une cellule qui atteint le plafond de **6 pas**. « 2,00 » est donc une
> **borne inférieure**, pas une valeur.

![combien de pas la matière porte](images/102_combien_de_pas_la_matiere_porte.png)

## 1. Pourquoi ce fichier, et c'est le graal en une phrase

`99` rend le **pas** que la matière montre, `101` la **direction**. Les deux ensemble sont
exactement ce qu'un automate doit savoir pour franchir une feuille : *avance de `p(matière)` le
long de `n(matière)`*. Mais dérouler n'est pas faire **un** pas, c'est les **enchaîner** — et la
question qui décide est *au bout de combien de pas la matière cesse de confirmer*.

Le prix tolère **8 h d'humain** là où l'état de l'art en dépense **775** sur la correction du
transfert de spire à spire. Ce fichier mesure jusqu'où on va sans lui.

⭐⭐⭐ **Et il n'y a aucun référent humain dans la boucle.** La direction vient du tenseur de
structure (`101`), le pas du balayage calibré (`99`), la vérification du critère de `98`. Les
quatre candidats de `94` à `97` ont tous été fermés parce qu'ils se calibraient contre un maillage
dont `97` a mesuré qu'il n'a pas de valeur unique. Ici le maillage ne sert qu'à dire **où
commencer**.

⚠ **Les deux seuls bits de supervision sont déclarés** : la cellule de **départ** (un automate
réel la recevrait d'une graine, et `77` a mesuré que les graines publiées existent) et le **sens**,
fixé **une fois** au premier pas parce que le signe d'un vecteur propre est arbitraire. Le choisir
à chaque pas en regardant la cible reviendrait à souffler la route au marcheur.

## 2. ⭐⭐⭐ Le lecteur est un seam, et c'est ce qui rend la fixture utile

Le marcheur ne connaît qu'un objet qui sait `lire(points)` et `dans_le_volume(points)`. Le **même**
marcheur tourne donc sur un volume **fabriqué** dont on connaît la réponse et sur le vrai volume
fin. Sans ce seam, la fixture testerait un autre code que la mesure — et une fixture qui n'exerce
pas le chemin réel ne prouve rien.

## 3. ⭐⭐⭐ Le résultat

| | mesuré |
|---|---|
| pas confirmés, médiane, en **interrogeant la matière** | **2,00** |
| pas confirmés, médiane, **automate naïf** | **0,00** |
| avantage | **+2,00 pas** |
| distance médiane portée | **583,9 µm**, soit **3,4** feuilles nominales |
| sorties du volume | **0** sur les 28 bandes |
| pas confirmés contre le rayon | **−0,388** |
| pas confirmés contre la rupture de continuité | **−0,167** |

⚠ **Les pas sont comptés CONSÉCUTIFS**, jamais en total : un marcheur qui perd la feuille au pas 3
écrit du faux ensuite, même si la matière répond de nouveau au pas 5. Compter le total
surestimerait exactement ce que l'automate sait faire.

⚠⚠ **Et la distance portée se lit avec son sous-ensemble** : elle est calculée sur les seules
cellules qui ont porté **au moins un pas**. Une bande peut donc afficher **zéro** pas médian
**et** une distance non nulle — ce sont deux populations, et les lire côte à côte sans le dire les
confondrait. C'est la faute que `99` a payée en comparant une population filtrée à une population
brute.

## 4. ⭐⭐⭐ Le témoin n'est pas un homme de paille, et c'est la condition pour que son zéro compte

| empilement fabriqué | matière | naïf |
|---|---|---|
| obliquité **0°** — pas nominal et rayon **justes** | **6** (plafond) | **6** (plafond) |
| obliquité **35°** — ce que `100` et `101` ont mesuré | **6** (plafond) | **1** |

> ⭐ **À 0°, le naïf atteint le plafond exactement comme la matière.** Son échec ailleurs vient
> donc de l'**obliquité**, pas d'un témoin cassé.

⚠ Le départ est recalé sur la famille de plans à chaque obliquité : une cellule qui tombe **entre**
deux feuilles ne correspond à aucune polarité du gabarit, et le contrôle mesurerait alors sa propre
erreur de mise en place — le défaut que la fixture de `100` a payé.

## 5. ⛔⛔ Le vérificateur a dû être refait, et le défaut vaut d'être écrit

Ma première version vérifiait chaque pas avec le **balayage** de `99`, qui cherche la meilleure
période le long de la direction donnée. Sur un empilement oblique de 35°, la période le long du
**rayon** vaut `173 / cos(35°) = 211 µm` — **dans la fenêtre de recherche** — donc le balayage la
trouve et **confirme**.

> ⛔ **Mesure du défaut : l'automate naïf passait ses 8 pas sur 8 là où il devait échouer.**

C'était une **vérification incapable d'échouer**, le péché nº 1 de ce dépôt, sous sa forme la plus
sournoise : elle testait *« la matière est-elle feuilletée ici »* — vrai partout — et non *« le pas
a-t-il franchi UNE feuille »*, qui est la seule question.

⭐⭐ **Les deux rôles sont désormais séparés, et ils doivent l'être** : `99` **décide** de combien
avancer, `98` **vérifie** à gabarit **fixe** ce que l'avance a traversé, sur le segment réellement
parcouru. Un pas trop court ne traverse pas un interstice entier, un pas trop long en traverse
deux, et aucun des deux ne peut se faire passer pour l'autre parce que **rien n'est cherché**.

Après correction, sur le même empilement oblique : **naïf 1, matière 8**.

## 6. ⚠⚠⚠ La borne, et elle se dit avant le résultat qu'elle borne

| maximum sur les cellules de la bande | bandes |
|---|---|
| 0 pas | 0 |
| 1 pas | 3 |
| 2 pas | 1 |
| 3 pas | 2 |
| 4 pas | 2 |
| 5 pas | 3 |
| **6 pas — le plafond** | **17** |

> ⚠⚠ **17 bandes sur 28, soit 61 %, ont une cellule AU PLAFOND.** « 2,00 pas » est donc une
> **borne inférieure**, pas une valeur.

Le plafond est un **budget de lecture**, pas une limite de matière : une sonde chronométrée mesure
**15,4 s pour lire un cube** de 41³ voxels dans le volume à 2,4 µm, donc les 672 cubes de cette
course font **2 h 52 de plancher incompressible** — la course entière a pris **7 h**. Publier ce
plafond comme une limite de matière serait la **butée** que `99` a enregistrée.

⚠ **Et l'automate naïf est censuré lui aussi** sur quelques bandes, ce qui est publié : son 0,00
médian n'est pas un 0 partout.

## 7. ⚠ Ce que ce document ne dit pas

- **Deux pas ne sont pas cent vingt.** Le graal demande 31 spires ; ce fichier mesure la **pente**,
  pas le total. Et la pente est censurée par le haut.
- **Combien de pas la matière porte réellement n'est pas mesuré** — seulement qu'elle en porte au
  moins deux de médiane, et au moins six sur 61 % des bandes. Relever le plafond est la marche
  suivante, et son coût est chiffré : chaque pas supplémentaire coûte ~15 s par cellule.
- ⚠ Le marcheur part d'une cellule de maillage. Il n'en a plus besoin ensuite, mais **il faut bien
  partir de quelque part**, et ce bit-là reste de la supervision.
- ⚠ **La corrélation avec la rupture de continuité est faible** (−0,167) : ce n'est pas un signal
  de confiance utilisable, et il faut le dire plutôt que de le publier comme tel.

## ⭐⭐⭐ Ce que `107` rejoue ici, et ce que la course a rendu de neuf

Le marcheur de ce fichier avance de ce que `pas_montre_calibre` rend, et
[`105`](105_le_balayage_rend_il_le_pas_injecte.md) a mesuré que ce sélecteur lit **+18,4 %** trop
haut. [`107`](107_le_marcheur_avec_le_bon_pas.md) rejoue la marche avec le sélecteur corrigé,
**appariée par le départ**, et **en gardant les étapes** — ce que ce fichier n'a pas fait, et sept
heures de course sont irrécupérables.

⛔ **Le pas corrigé ne porte pas plus loin** : 1,0 pas confirmés contre 1,0. ⚠ Les deux nombres ne se
comparent pas à la médiane de 2,00 publiée ici : `102` prend 4 cellules par bande et publie une
médiane de médianes par bande, `107` une cellule et une médiane sur cellules.

⭐⭐⭐ **Mais le risque par pas BAISSE** — précoce 0,382, tardif 0,105, ×3,63, p = 0,0418 sous un
risque constant. *La difficulté est de s'accrocher, pas de porter.* ⚠ Et il ne baisse pas assez :
$(1-0{,}105)^{120} = 2\cdot10^{-6}$.

⭐⭐⭐ **Et le registre du trajet entier sépare les marches en DEUX populations que le critère de ce
fichier ne distingue pas** : 10 trajets franchissent 6,478 feuilles pour six pas (1,08 par pas) et 14
n'en franchissent que 0,748 (0,125 par pas). ⚠⚠⚠ Le score est **plus haut pour les mauvaises**
(0,483 contre 0,371), donc un seuil de score écarterait le **bon** mode.

⚠ Les chiffres de ce document ne sont **pas** recalculés : les relire demande de relancer la mesure.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --cellules 4 --pas 6 --demi 20 \
    --json docs/mesures/combien_de_pas_la_matiere_porte.json   # ~7 h de lectures reseau
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --reagreger \
    --json docs/mesures/combien_de_pas_la_matiere_porte.json   # rederive, sans reseau
uv run python src/figures/figure_combien_de_pas_la_matiere_porte.py --verifier
```

# 149 — La pince ne meurt pas de dérive, elle meurt d'arrêt

> ⭐⭐⭐⭐ **LE COMPTE QUI DÉPLACE LE TRAVAIL, ET IL ÉTAIT DÉJÀ DANS LES DONNÉES.** `142` à `148` ont
> toutes traité l'identité de la feuille : quelle mémoire, quelle lecture, quel cap. Or les suivis
> que `148` range disent de quoi les marches meurent, et le compte est sans appel — sur **180**
> marches de la pince, **108** réussissent, **49 s'ARRÊTENT** et **13** seulement bouclent leur tour
> sur une autre feuille. **Quatre échecs sur cinq sont d'une autre nature que celle qu'on traitait.**
>
> ⭐⭐⭐ **ET C'EST LA POSE QUI ÉCHOUE, PAS LA CONTRAINTE.** Une marche arrêtée meurt à **0,067** de
> tour avec **21** refus de POSE et **0** refus de contrainte ; une marche bouclée fait **631,5** pas
> avec **0** refus de pose. La mâchoire ne trouve plus d'interstice encadré, et tout s'arrête là.
>
> ⭐⭐⭐⭐ **LA RAISON EST GÉOMÉTRIQUE ET EXACTE.** `142` a donné à la recherche une fenêtre large
> d'UNE épaisseur centrée sur l'attente : elle contient l'interstice tant qu'il n'a pas bougé de plus
> d'une **demi**-épaisseur, soit **86,5 µm**. Or le froissement le déplace — mesuré sur la fixture,
> qui le fabrique :
>
> | matière | déplacement médian | maximum | hors fenêtre | contenue ? |
> |---|---|---|---|---|
> | spirale nue | 0,0 µm | 0,0 µm | 0 ‰ | oui |
> | spirale écrasée | 0,0 µm | 0,0 µm | 0 ‰ | oui |
> | froissée 42,4 µm | 12,515 µm | **42,343 µm** | **0 ‰** | oui |
> | écrasée et froissée 42,4 µm | 12,467 µm | 42,334 µm | 0 ‰ | oui |
> | **écrasée et froissée 100 µm** | 29,949 µm | **99,836 µm** | **33 ‰** | **non** |
>
> **La matière que `140` retient est structurellement hors d'atteinte de la fenêtre de `142`**, et
> c'est pour ça que personne n'y a jamais bouclé un tour.
>
> ⚠⚠ **ET ÉLARGIR LA FENÊTRE NE RÉPARE PAS — LES DEUX FAÇONS DE LE FAIRE ÉCHOUENT, ET DE LA MÊME
> MANIÈRE.** Leur marge **sature son plafond** (86,5 µm des deux côtés), donc la fenêtre double
> partout et attrape l'interstice **voisin** — ce que la fenêtre d'une épaisseur existait précisément
> pour interdire. **54** et **52** réussites contre 108, **0 gagnée** pour 54 et 56 perdues, et elles
> arrêtent **plus** (113 et 115 contre 49).
>
> ⭐ **Mais la géométrie est confirmée là où elle s'applique** : sur la matière de `140`, la part du
> tour atteinte avant l'arrêt passe de **0,0217** à **0,0939**.

## 1. Pourquoi ce fichier

`148` a mesuré ce que la mémoire coûte et refermé le dernier chemin évident sur le cap. En rangeant
ses suivis, une question restait posée nulle part : **de quoi les marches meurent-elles ?** Un échec
peut être de deux natures, et elles n'appellent pas le même remède — la marche boucle son tour en
revenant sur une **autre feuille**, ce qui est un problème d'identité, ou elle **ne boucle pas du
tout** parce qu'elle s'est arrêtée.

⭐ La réponse ne demandait aucune marche neuve : elle est dans le JSON de `148`.

## 2. ⭐⭐⭐⭐ De quoi les marches meurent

![Les arrêts, la géométrie qui les explique, et les deux élargissements qui ne réparent pas](../images/149_ou_les_marches_sarretent.png)

| | marches |
|---|---|
| bouclées sur la bonne feuille | **108** |
| **arrêtées** | **49** |
| bouclées sur une autre feuille | 13 |

| | part du tour | refus de POSE | refus de CONTRAINTE | pas |
|---|---|---|---|---|
| une marche arrêtée | **0,067** | **21** | **0** | 79 |
| une marche bouclée | 1,0008 | 0 | 0 | 631,5 |

⚠ Les deux refus sont comptés **séparément** et c'est ce qui rend la conclusion possible : une pince
qui meurt de sa **contrainte** — le refus de `142`, « le même interstice » — et une qui meurt de sa
**fenêtre** n'ont pas le même remède. Ici la contrainte n'y est pour rien.

⚠ Trente et une des quarante-neuf marches arrêtées sont sur la matière que `140` retient, où
**aucune** n'en réchappe.

## 3. ⭐⭐⭐⭐ La géométrie qui l'explique

La fenêtre de `142` va de zéro à une épaisseur et attend l'interstice à la demi-épaisseur. Un
interstice déplacé de `d` s'y trouve donc si et seulement si `|d|` reste sous la **demi-épaisseur** —
au-delà il sort par un bord, et `linterstice` refuse à juste titre un minimum non encadré, ce que
`142` a payé pour apprendre.

Le déplacement se lit **directement sur la fixture, qui le fabrique** : aucune estimation, aucune
marche. Le tableau du haut le donne. ⭐ Et il n'y a pas de seuil là-dedans : la demi-épaisseur est
dérivée du pas, et la question « la fenêtre le contient-elle » est un fait sur des nombres.

⚠ **Le déplacement maximal d'une matière est borné par son amplitude**, et la mesure le vérifie
plutôt que de s'y fier : aucune matière ne déplace plus que ce qu'on lui a demandé.

## 4. ⚠⚠ Les deux élargissements, et pourquoi aucun ne répare

La réparation évidente ne demande aucune constante : élargir la fenêtre de ce que le suiveur a
**déjà vu** — de combien l'interstice qu'il vient de trouver s'écarte de là où il l'attendait —
plafonné à une demi-épaisseur, parce qu'au-delà la fenêtre atteindrait l'interstice voisin.

**Il y a deux façons de lire « là où il l'attendait », et elles sont contaminées chacune à sa
manière.** Les deux sont nommées avant la mesure et mesurées ensemble :

| règle | réussites | arrêtées | autre feuille | part du tour | marge employée |
|---|---|---|---|---|---|
| **fenêtre nominale (`144`)** | **108** | **49** | 13 | **1,0004** | 0,0 µm |
| élargie sur la **mesurée** | 54 | 113 | 3 | 0,3857 | **86,5 µm** |
| élargie sur la **nominale** | 52 | 115 | 3 | 0,2256 | **86,5 µm** |

Appariées sur les mêmes **180** départs : **0 gagnée pour 54 perdues**, et **0 gagnée pour 56
perdues**.

⭐⭐ **Les deux saturent leur plafond**, et c'est le fait qui les explique toutes les deux : la marge
vaut 86,5 µm des deux côtés, donc la fenêtre fait deux épaisseurs partout et atteint l'interstice
**voisin**. Une fenêtre qui attrape le voisin ne suit plus une feuille, elle en change.

**Chaque estimateur a sa contamination, et elle est nommée** :
- **la mesurée** : l'épaisseur mesurée grandit dès que la fenêtre attrape un interstice trop loin,
  donc l'écart grandit, donc la fenêtre s'élargit encore. ⚠⚠ **Toute quantité que l'élargissement
  enfle lui-même est impropre à décider de cet élargissement** — c'est une rétroaction positive, et
  elle a été payée deux fois avant d'être nommée : d'abord sur le **plafond**, qui partait à 772 µm
  pour un pas de 173, puis sur l'**attente**.
- **la nominale** : le pas nominal ne peut pas s'emballer, mais il n'est pas l'espacement **local**.
  Sur une spirale lisse simplement écrasée, où rien n'est déplacé, cet estimateur lit déjà une
  vingtaine de micromètres.

⭐ **Et la géométrie est confirmée là où elle s'applique** : sur la matière de `140`, la part du tour
atteinte avant l'arrêt passe de **0,0217** à **0,0939** et **0,0755**. La fenêtre élargie va bien
quatre fois plus loin là où la fenêtre nominale ne peut structurellement pas aller — elle casse
seulement tout le reste en chemin.

## 5. ⭐⭐ Ce que ça change pour le graal

**La question change de place.** Ce qui arrête une marche n'est pas qu'elle perde sa feuille, c'est
qu'elle ne trouve plus d'interstice à l'endroit où elle le cherche. Sur la matière du rouleau, ce
n'est même pas un accident : trente-trois millièmes de la matière sont hors d'atteinte de la fenêtre,
et une marche de six cents pas les rencontre.

**Et ce qui manque est nommé, comme dans `146`** : un suiveur ne peut pas estimer, de ce qu'il voit,
de combien l'interstice a bougé. Les deux références dont il dispose sont fausses — l'une parce que
l'élargissement la déplace, l'autre parce qu'elle n'est pas locale. ⭐ La suite n'est donc pas
d'élargir davantage mais de **chercher au bon endroit** : la fenêtre est centrée sur une attente, et
c'est l'attente qu'il faudrait corriger, pas sa largeur.

⚠ **Ce que ça ne dit pas.** Que la fenêtre soit la seule cause des arrêts. Elle explique ceux de la
matière de `140` — trente et un sur quarante-neuf — et la mesure ne dit pas ce qui arrête les
dix-huit autres, qui sont sur des matières que la fenêtre contient. Ce qui est établi est plus
étroit : **les arrêts dominent les échecs, c'est la pose qui les cause, et sur la matière du rouleau
la fenêtre ne peut structurellement pas contenir son interstice.**

## 6. ⚠ Ce que la mesure a corrigé d'elle-même

- ⚠⚠⚠ **La rétroaction positive, payée deux fois.** Le plafond de la marge portait d'abord sur
  l'épaisseur **mesurée** : une fenêtre élargie attrape un interstice trop loin, l'épaisseur mesurée
  enfle, la fenêtre suivante s'élargit d'autant, et la marge part à **772 µm** pour un pas de 173.
  Corrigé en plafonnant sur le pas **nominal** — puis le même défaut est réapparu un cran plus haut,
  dans l'**attente** contre laquelle l'écart se mesure. La règle générale est écrite dans le code :
  *toute quantité que l'élargissement enfle lui-même est impropre à décider de cet élargissement.*
- ⚠⚠ **Le premier estimateur n'était pas celui que je croyais.** J'ai d'abord pris l'écart **entre
  les appuis** d'une mâchoire pour une mesure du déplacement. Les appuis sont distants de la
  **largeur** de la mâchoire : leur dispersion mesure l'ondulation **en travers**, pas le déplacement
  **le long** de la marche, et elle saturait le plafond sur une matière que la fenêtre nominale
  contenait très bien.
- ⚠⚠ **Une sonde courte a menti, une fois de plus.** Sur trois départs et un vingtième de tour,
  l'élargissement faisait passer la marche de 1 % à 100 % de l'arc demandé. Sur la grille entière il
  perd cinquante-quatre réussites. C'est la troisième tranche d'affilée où une sonde courte ne borne
  pas une marche longue.
- ⚠ **Deux sondes de figure déplaçaient des champs que la bande ne lit plus** — elles passaient sans
  rien prouver. Et un `⭐` dessiné n'est pas dans la police déployée : c'est `★`.
- **Le compte des arrêts ne demande aucune marche neuve** : il se lit sur le JSON de `148`, et une
  tranche qui aurait remarché pour l'obtenir aurait payé une grille entière pour un tri.

## 7. Les registres

Faits `R4-F112` (la pince meurt d'arrêt et non de dérive, 49 contre 13, et c'est la pose qui échoue),
`R4-F113` (une fenêtre d'une épaisseur ne contient l'interstice que s'il n'a pas bougé de plus d'une
demi-épaisseur, et la matière de `140` la dépasse sur 33 ‰) et `R4-F114` (élargir la fenêtre de ce
que le suiveur a vu échoue des deux façons de le lire, par saturation du plafond). Porte `R4-P26` :
la demande change de place — corriger l'**attente**, pas la largeur.

## Reproduire

```bash
uv run python src/nappe/ou_les_marches_sarretent.py \
    --json docs/mesures/ou_les_marches_sarretent.json   # aucune lecture distante
uv run python src/figures/figure_ou_les_marches_sarretent.py \
    --json docs/mesures/ou_les_marches_sarretent.json \
    --sortie docs/images/149_ou_les_marches_sarretent.png
uv run python src/nappe/ou_les_marches_sarretent.py --verifier            # 29
uv run python src/figures/figure_ou_les_marches_sarretent.py --verifier   # 18
uv run python src/nappe/la_pince_tient_elle_la_feuille.py --verifier      # 72
```

⚠ Deux précédents sont lus et non recopiés : `lire_la_cause_sous_le_bruit.json` pour le témoin de
`144`, et `la_memoire_fait_elle_avancer_de_travers.json` pour le compte des arrêts. Sans eux les deux
sont **indécidables**, et la mesure le dit plutôt que de le supposer.

⚠ `--reagreger <json>` recalcule les résumés et les verdicts depuis les suivis rangés, sans
remarcher.

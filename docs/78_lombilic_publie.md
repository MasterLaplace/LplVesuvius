# 78 — Cinq rouleaux publient leur axe, et la mesure appariée n'en bouge pas

> Écrit le 2026-09-04, en cherchant de quoi construire **A2 bis** (le champ d'identité dérivé
> du volume). Mesure dans l'arbre : `src/excision/lombilic_publie.py` (5 contrôles),
> figure `src/figures/figure_ombilic_publie.py`.

---

## 0. ⚠⚠⚠ Une affirmation du dépôt, corrigée — et c'est le même angle mort pour la 3ᵉ fois

`laxe_nest_pas_une_ligne.py` écrivait :

> « La dérive mesurée est celle de **Scroll 1**. C'est le **seul** rouleau qui publie un
> ombilic — vérifié le même jour sur les cinq répertoires `umbilici/` de `dl.ash2txt.org`. »

**La vérification était juste et sa conclusion fausse.** Elle portait sur **un** serveur et
**une** convention de chemin. Sur le bucket ouvert, l'axe vit sous
`<rouleau>/representations/umbilicus/`, et **5 rouleaux en publient un** — balayés sur les
**46 préfixes de premier niveau**, pas sur une liste écrite à la main :

| rouleau | points de contrôle | voxel | annotateur |
|---|---:|---:|---|
| `PHerc0125` | 83 | 9,362 µm | — |
| **`PHerc0139`** | **391** | 2,399 µm | David Josey |
| `PHerc0211` | 87 | 9,362 µm | — |
| `PHerc0332` | 169 | 2,399 µm | David Josey |
| `PHerc0826` | 49 | 9,362 µm | — |

C'est l'angle mort de `59` — *interroger une vue du corpus et conclure sur le corpus* — commis
ici **pour la troisième fois**, et sur le **même objet** que la deuxième. La correction est
écrite dans le fichier fautif, pas seulement ici.

⚠ Et les deux serveurs se **complètent** : Scroll 1 publie bien son ombilic sur
`dl.ash2txt.org`, où il n'y en a pas d'autre. Le mot faux était « seul », pas la mesure.

---

## 1. ⭐⭐⭐ Ce que l'axe publié permet de vérifier vaut mieux que l'axe lui-même

`76` et `77` ajustent un centre par tranche **sur les spires elles-mêmes**. Un ajustement de
cercle sur un **arc partiel** est biaisé — défaut connu de la méthode, dont la mesure exigeait
un axe indépendant. On l'a : 391 points annotés **à la main**.

![Les deux axes, et ce que le biais change](article/figures/ombilic_publie.png)

*Régénérer : `uv run python src/excision/lombilic_publie.py --json docs/mesures/lombilic_publie.json
&& uv run python src/figures/figure_ombilic_publie.py`*

**Le biais est réel et il est grand** : médiane **3,01 mm**, jusqu'à **27 écarts inter-feuilles**. Les deux axes errent de la même façon — même forme, même sens — mais ne se
superposent pas.

### Et la mesure appariée n'en bouge pas

| | vers l'extérieur | écart inter-feuilles |
|---|---:|---:|
| axe **ajusté** (`76`) | **94,8 %** | **155,8 µm** |
| axe **publié** | **94,8 %** | **156,8 µm** |

**Un axe faux de 4 mm déplace le verdict de zéro point et l'écart d'un micromètre.**

C'est exactement ce pour quoi la mesure a été conçue appariée — comparer deux spires *au même
endroit, autour du même centre*, de sorte qu'un biais commun s'annule — et c'est désormais
**mesuré** au lieu d'être argumenté. Tout `76` et tout `77` reposent dessus.

### ⚠ Le contrôle vient en paire, et l'ordre compte

« La mesure ne bouge pas » serait vrai **pour la mauvaise raison** si les deux axes étaient
identiques. Le fichier asserte donc **d'abord** qu'ils diffèrent de plusieurs feuilles, et
**ensuite** que la mesure n'en bouge pas. La sonde qui rend les deux axes égaux fait tomber le
premier contrôle.

### ⚠ Et une sonde localise l'immunité, ce que je n'aurais pas su dire sans elle

Remplacer le centre par tranche par un centre **global** ne change rien non plus (94,6 %
contre 94,5 %). **L'immunité ne vient donc pas de la qualité du centre** mais du fait que les
deux spires sont comparées **dans la même cellule angulaire autour du même centre, quel qu'il
soit**. Un centre par tranche améliore les rayons **absolus** ; la comparaison, elle, était
déjà immunisée.

---

## 2. Ce que ça ouvre pour A2 bis

Le champ d'enroulement de `77` a une limite dure : il **interpole entre spires connues** et
refuse au-delà, donc il ne sort pas de la bande publiée (37 spires sur ~110). Un axe publié
change la donne, parce qu'un nombre d'enroulement se construit **à partir de l'axe et d'un
champ d'orientation**, pas à partir de spires déjà tracées.

⚠ Ce que le dépôt sait déjà et qui borne l'espoir (`26` §7) : les `.normal-grids` publiées sont
**dérivées de la prédiction de surface** que le traceur suit déjà — les lui redonner est une
tautologie, mesurée (×29 de ralentissement, trajectoire identique au centième). Un champ
d'enroulement bâti dessus hériterait donc de la prédiction, pas d'une information neuve.

Ce qui reste ouvert, et c'est A2 bis : **un nombre d'enroulement construit sur l'axe publié et
l'orientation des fibres** (`representations/predictions/fibers/`, publié pour `PHerc0139` en
`nx`/`ny`/`nz` OME-Zarr), qui répondrait partout et pas seulement dans la bande.

---

## 3. Ce que ce document N'établit PAS

1. **Que l'axe publié soit juste et l'ajusté faux.** Il établit qu'ils **diffèrent** et que la
   conclusion n'en dépend pas. L'axe publié est un jugement humain, pas une vérité — mais un
   jugement **indépendant** du nôtre, ce qu'il fallait pour tester une robustesse.
2. **Que les cinq axes soient de même qualité.** De 49 à 391 points de contrôle, et seuls deux
   nomment leur annotateur.
3. **Que la conversion de repère soit exacte.** Elle est un facteur d'échelle lu dans le champ
   `volume` du meta et **validé** contre les résolutions de scan publiées. Deux des cinq axes
   sont en 2,399 µm et trois en 9,362 µm ; les mélanger sans conversion donnerait un axe faux
   d'un facteur 3,9.

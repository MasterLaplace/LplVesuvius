# 48 — Où monter l'expérience : ce qu'on sait tracer et ce qu'on sait lire ne se recouvrent pas

2026-08-22. [`29`](29_ce_qui_reste.md) §1 porte la question dont dépend tout le reste du
dépôt — *réparer une trace sert-il à quelque chose ?* — et nomme depuis le début ce qu'il
faudrait : **une trace fautive, sa version réparée, et le même aval appliqué aux deux**.
Ce document ne répond pas à la question. Il mesure **pourquoi elle n'est pas montable sur
ce qui est en main**, et il nomme où elle le serait.

![deux ensembles disjoints](images/48_eligibilite.png)

Instrument : [`analysis/src/eligibilite_aval.py`](../analysis/src/eligibilite_aval.py)
(23 témoins hors ligne) et [`figure_eligibilite.py`](../analysis/src/figure_eligibilite.py)
(11 témoins). Il ne mesure rien de neuf : il **croise trois mesures déjà faites**.

---

## 1. ⚠⚠ L'aval doit répondre, et sur un rouleau du prix il ne répond pas

[`46`](46_le_temoin_negatif.md) mesure que sur `PHerc1447` le détecteur rend la **même
carte** (ρ = 0,9979) sur une face de papyrus et sur une surface qui coupe l'empilement.
Sa dispersion vaut **1,7 %** de ce que le modèle rend là où il atteint AUC 0,925.

> Une différence de surface **bien plus grande** que celle entre une trace fautive et sa
> réparation ne le fait pas bouger. Aucune réparation ne peut donc y montrer de gain.

⭐ Ça donne une **condition d'entrée vérifiable avant de dépenser** : σ de la sortie du
modèle sur le rouleau visé, rapporté aux **0,7712** de référence. Une inférence sur une
fenêtre suffit.

## 2. Les deux ensembles, et leur intersection

| ensemble | comment il est établi | compte |
|---|---|---:|
| **traçables** | une campagne de tirages a tourné dessus (`table_tirages.json`) | **13** |
| **lisibles** | plus de la moitié des cartes publiées ont la statistique d'une page écrite ([`45`](45_consistent_with_quantifie.md)) | **3** |
| **intersection** | | ⚠⚠ **0** |

| rouleau | cartes | écrites | part |
|---|---:|---:|---:|
| PHerc0139 | 38 | 14 | 37 % — non |
| **PHerc0172** | 53 | 49 | **92 %** |
| **PHerc1667** | 19 | 13 | **68 %** |
| **PHercParis4** | 80 | 44 | **55 %** |

⚠ **« Pas dans la cohorte tracée » n'est pas « pas traçable ».** Rien ne dit qu'un rouleau
lisible résiste au traceur ; il n'a simplement jamais eu de campagne. Ce que la disjonction
dit, c'est **où** l'expérience doit être montée — pas qu'elle est impossible. L'instrument
formule donc une **action** et pas une impasse, et le témoin exige qu'il le fasse.

## 3. ⚠⚠ Un défaut à moi, et c'est la sonde réseau qui l'a corrigé

Ma première recommandation était *« commencer par `PHerc0172`, 92 % de cartes écrites »*.
Elle est **irréalisable**, et rien dans les données déjà en main ne le disait :

| rouleau | publie |
|---|---|
| `PHerc0172` | `photos/` `segments/` `volumes/` — ⚠ **pas de `representations/`** |
| `PHerc1667` | `photos/` **`representations/`** `segments/` `volumes/` |
| `PHercParis4` | `photos/` **`representations/`** `segments/` `volumes/` |

La recherche de graine part d'une **prédiction de surface**. Un rouleau qui n'en publie pas
ne peut pas recevoir la campagne, quelle que soit la qualité de son encre. L'instrument
**écarte** désormais un tel candidat au lieu de le classer dernier — le classer laisserait
recommander une expérience qui ne peut pas tourner.

⭐ Et le classement des candidats restants n'est pas la part écrite : c'est **où le
détecteur est mesuré directement**. `PHercParis4` est le rouleau de `36` §5bis, celui où le
modèle atteint AUC 0,925 avec σ = 0,7712. Une mesure vaut mieux qu'une ressemblance.

## 4. ⚠ Le blocage restant, nommé plutôt que contourné

`PHercParis4` publie **deux prédictions de surface du même scan**, toutes deux à 2,4 µm :

```
20260411134726-surface-20260413141734-surface-recto-
20260411134726-surface-20260413222639-surface-m7-L2-
```

L'appariement **refuse** — *« 2 scans à 2.4 µm ± 1.0 — ambigu, refus plutôt qu'un tirage au
sort »*. Ce n'est pas une ambiguïté de volume mais de **produit de surface**, et choisir au
hasard entre deux prédictions est exactement le défaut que ce dépôt recense sous « supposer
une provenance ».

### ✅ Tranché par la mesure, le 2026-08-22 — et la réponse est « ni l'une ni l'autre, pas encore »

Ce ne sont pas deux versions d'une même chose : leurs métadonnées disent qu'elles sortent du
**même volume** (`2.4um_PHerc-Paris4_masked.zarr`), générées à deux secondes d'intervalle,
par **deux modèles différents** — `ps256_trainpy` à seuil 0,45 et `m7_nnunet` à seuil 0,2.

⚠ **Les scores internes ne tranchent pas**, et il fallait le mesurer pour le savoir : les
deux meilleures graines sont aux **extrêmes** de la bande admissible — `ps256` à une
occupation de **0,0215** quand le plancher est 0,02, `m7` à **0,75** avec une planarité de
**1,0** quand le plafond est 0,80. « Tout est surface ET parfaitement plan » est la signature
d'une prédiction **saturée** que [`39`](39_le_seam_de_correction.md) §3 décrit : il n'y a
alors aucun gradient à suivre.

Le critère du dépôt, lui, tranche — on trace la meilleure graine de chacune avec des
paramètres identiques et on juge au test de convergence
(`tools/tracer_prediction_paris4.sh`) :

| prédiction | aire | croisements | verdict |
|---|---:|---:|---|
| `ps256` | 0,317 cm² | 0 | α = **+0,89**, *suit la fenêtre*, ⚠ fragile, 100 % des fenêtres au bord |
| `m7` | 0,317 cm² | 0 | ⚠⚠ **INDÉCIDABLE** — profil plat |

> ⚠⚠ **Aucune des deux ne donne une trace posée sur une feuille**, et `m7` ne donne même pas
> une mesure : son profil est plat, donc son α de 1,01 était le **rapport de deux bords de
> fenêtre**. C'est ce que [`49`](49_alpha_ne_separe_pas_deux_pannes.md) a trouvé, et
> l'instrument refuse désormais de conclure dans ce cas.

### ⚠⚠ Et relever le plafond bute sur le coût du rendu, mesuré

À 200 générations la trace passe de 0,317 à **3,655542 cm²** — onze fois plus, donc la
troncature est bien levée. Mais le rendu, lui, devient inabordable : mesuré sur
`/proc/<pid>/io`, `vc_render_tifxyz` à `--scale 1` sur ce rouleau à 2,4 µm a lu **51 Mo et
écrit 1592 octets en quinze minutes** — 41 fichiers de sortie de **8 octets**. Pour
~2,6 milliards de voxels cela fait **plus de douze heures** pour une seule fenêtre, et
quatre fois plus pour celle à 161 couches.

⭐ Rien dans la sortie ne le disait. D'où `tools/rendre_surveille.sh` : il surveille
l'**activité du processus** plutôt que le temps écoulé — un rendu long n'est pas un rendu
bloqué — abandonne en le disant, et **rapporte le débit dans les deux cas**, succès compris.

> ⚠⚠ **Et c'est ce rapport qui a corrigé mon propre diagnostic.** Le rendu suivant, même
> échelle et même volume, a écrit **148 Mo en 131 s — 1108 Kio/s**, soit **vingt fois** le
> débit que j'avais mesuré. Mon « plus de douze heures » était une extrapolation depuis **un
> seul échantillon de quinze minutes**, et une extrapolation n'est pas une mesure.
>
> ⚠ Je ne sais pas ce qui explique l'écart. Deux candidats, non séparés : la **localité** —
> une surface onze fois plus grande touche beaucoup plus de morceaux du zarr distant, et un
> accès dispersé coûte bien plus qu'un accès séquentiel — et la simple **variabilité du
> réseau**. Les distinguer demanderait de rejouer le même rendu deux fois, ce qui n'a pas
> été fait.
>
> ⭐ Ce qui est acquis : le débit est désormais **rapporté à chaque rendu**, donc les runs
> suivants donnent une distribution au lieu d'un point. Mesurés depuis :
> **1108, 1116, 3848 et 1834 Kio/s**. Le 57 Ko/s initial est une valeur aberrante d'un
> facteur vingt à soixante-dix, et un seul point ne pouvait pas le montrer.

⚠ `ECHELLE` devient un paramètre. Une échelle plus grossière réduit l'échantillonnage **dans
le plan** et pas le long de la normale, donc les microns du profil restent des microns ; ce
qui change est le nombre de fenêtres. C'est une vraie différence de mesure, et c'est
pourquoi **les deux prédictions sont rendues à la même échelle** : la comparaison reste une
comparaison, seule la valeur absolue cesse d'être comparable à un run à l'échelle 1.

### ✅ Le 2×2 croisé tranche — et la question se dissout

⚠⚠ Tracer chaque prédiction à **sa** graine confondait « quelle prédiction » avec « quel
endroit » : les deux graines tombent à des kilovoxels l'une de l'autre. Les deux prédictions
couvrant le même volume, une graine y est une coordonnée valide des deux côtés — d'où les
quatre cellules.

| | graine de `ps256` | graine de `m7` |
|---|---|---|
| prédiction **`ps256`** | α = **+1,12** | ⚠⚠ **indécidable** (profil plat) |
| prédiction **`m7`** | α = **+0,95** | ⚠⚠ **indécidable** (profil plat) |

| facteur | écart | verdict |
|---|---:|---|
| **prédiction** | 0,17 | ⚠ **sous le bruit** de 0,20 — indistinguables |
| **endroit** | catégorique | ⭐ les **2** cellules indécidables sont du même côté |

> ⭐⭐ **La question bloquante se dissout, comme celle de [`47`](47_le_critere_doit_etre_relatif.md).**
> Il n'y a pas de bonne prédiction à choisir : les deux se comportent pareil au même endroit,
> et ce qui décide est **la graine**. L'effort doit aller là.

### ✅ Répété quatre fois par cellule, et l'écart RÉTRÉCIT

![le 2×2, chaque tirage](images/48_2x2.png)

⚠ La première passe avait un tirage par cellule, or le traceur *en est un* : la même graine
dans la même prédiction avait rendu α = +0,89 puis +1,12. Le 2×2 a donc été rejoué à
**quatre tirages par cellule** — seize runs, parfaitement équilibrés.

| | graine de `ps256` | graine de `m7` |
|---|---|---|
| **`ps256`** | +1,12 · +1,01 · +0,94 · +1,09 — médiane **+1,05** | ⚠⚠ **4 indécidables** |
| **`m7`** | +1,01 · +1,01 · +0,97 · +0,95 — médiane **+0,99** | ⚠⚠ **4 indécidables** |

> ⭐⭐ **L'écart entre prédictions passe de 0,17 à 0,06** — il a *rétréci* en répétant, ce qui
> est exactement le comportement d'une différence due au bruit. Il faudrait au moins **0,20**
> pour distinguer. Et l'indécidabilité suit la graine à **chacune** des huit répétitions.

⭐ **Le bruit de tirage est mesuré, plus déduit** : l'étendue intra-cellule vaut **0,18** sur
la cellule la plus dispersée. ⚠ Ce n'est pas la même quantité que le ±0,2 de
[`43`](43_la_chaine_des_spires.md) — celui-ci est une **demi-largeur** (bande de 0,4) sur un
mode *déterministe*, donc une résolution de **mesure**. Ce qu'on peut dire, et pas plus :
l'étendue de tirage observée **tient dans** la bande déclarée, donc celle-ci n'est pas trop
généreuse.

⚠ Deux réserves restent :
- les deux α mesurables valent **≈ 1** : les deux prédictions sont indistinguables *et*
  mauvaises à cet endroit ;
- l'effet catégorique repose sur **deux endroits**, pas deux cents — huit répétitions
  n'élargissent pas l'échantillon de graines, elles ne font que fiabiliser chaque case.

Instrument : [`analysis/src/comparer_predictions.py`](../analysis/src/comparer_predictions.py)
(19 témoins) et [`figure_2x2.py`](../analysis/src/figure_2x2.py) (6 témoins). ⭐ Il **refuse** quand l'écart est sous le bruit, et le bruit n'est pas choisi :
c'est le plus grand de la résolution que `test_convergence` déclare et de l'étendue
intra-cellule mesurée.

⚠ Et les deux aires valent **0,317 cm²** à cinq chiffres près — les deux traces butent sur
le même plafond de 60 générations. C'est la troncature de `35` : deux traces coupées au même
endroit ont la même aire pour une raison qui n'a rien à voir avec la prédiction. **La
comparaison n'est donc pas encore concluante**, et relever le plafond est le prochain pas —
pas un choix de prédiction.

## 5. Ce que ce document n'établit pas

- ⚠ **Que la statistique typographique d'une carte prouve qu'elle porte du texte.** `45` le
  dit explicitement : c'est un critère **nécessaire, jamais suffisant** — une carte
  périodique peut être un artefact. Le critère sert ici à écarter, pas à valider.
- ⚠ **Que le détecteur répond sur les trois rouleaux lisibles.** Il n'est mesuré
  directement que sur `PHercParis4` (par `36`) et sur `PHerc1447` (par `46`). Pour les deux
  autres, la lisibilité est **inférée** de la statistique de leurs cartes publiées.
- ⚠ **Que réparer sert à quelque chose.** C'est la question, et elle reste ouverte. Ce
  document dit seulement où elle peut être posée.

## Reproduire

```bash
python3 analysis/src/eligibilite_aval.py --docs docs --json docs/eligibilite_aval.json
python3 analysis/src/eligibilite_aval.py --docs docs --sonder --json docs/eligibilite_aval.json
cd inference && uv run python ../analysis/src/figure_eligibilite.py \
    --json ../docs/eligibilite_aval.json --sortie ../docs/images/48_eligibilite.png

# les témoins, hors ligne
python3 analysis/src/eligibilite_aval.py --verifier
python3 analysis/src/figure_eligibilite.py --verifier
```

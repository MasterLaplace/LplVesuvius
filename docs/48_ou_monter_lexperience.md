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

# Le batch d'épuisement — tout fermer avant d'inventer

2026-08-18. Objectif posé par l'auteur : **plus rien d'ouvert dans la doc ni dans la
passation** avant de chercher des pistes créatives. Ce fichier est la liste, et il se
coche ici.

⚠ Un item se ferme de **deux** façons également valables : *fait et mesuré*, ou
*écarté avec la raison écrite*. Ce qui n'est pas acceptable, c'est qu'il reste ouvert
sans que personne sache pourquoi.

⭐ **Le tri est fait par l'objectif** — le **déroulement**, pas la lecture. Ce qui mesure
une trace passe devant ce qui mesure de l'encre.

---

## Voie A — la métrique de proximité tient-elle sur un second rouleau ?

Ferme `07` §5 (« un seul rouleau ») et `06` §C.

| # | quoi | état |
|---|---|---|
| A1 | métrique sur les **53 traces de Scroll 5** | ✅ **44 sur 53 rendent ZÉRO cellule** — voir A2 |
| A2 | corréler aux croisements publiés de Scroll 5 | ✅ **la métrique est INAPPLICABLE**, pas moins bonne : elle exige une trace qui se recouvre, et 44 traces couvrent ≤ 1 tour. Les 9 mesurables sont 9 morceaux du **même** segment, donc n = 1. `07` §7 |
| A3 | le **confond longueur/qualité** de `05` | ✅ **expliqué** : sur Scroll 5 seules les traces longues sont mesurables, donc toute corrélation y est confondue **par construction** |
| A4 | le **seuil arbitraire** de `07` §5 | ✅ **tranché** (`07` §8) : aucune grandeur sans seuil ne l'égale (`shortfall` +0,340, `ratio_p5` −0,512 contre **+0,769**) — le signal EST dans la queue. Et le plateau tient de 0,15 à 0,40, un facteur **2,7** sans que rho bouge |
| A5 | les 3 corpus restants — PHerc0139 (38), PHerc1667 (20), PHerc0814 (13) | ✅ **71 traces mesurées** (`07` §9). Avec le rayon issu de la physique : PHerc0139 **+0,666** (p = 2,3e-05), PHerc1667 +0,579, PHerc0814 +0,141 (n = 12, sous-puissant). ⭐ Le gain est le plus grand **à 9,362 µm**, la résolution des 13 rouleaux du prix |

## Voie B — la profondeur de surface, de l'anecdote à l'instrument

Ferme `12` §5 (« trois segments, deux rouleaux, ce n'est pas un corpus »).

| # | quoi | état |
|---|---|---|
| B1 | le **sous-échantillonnage des couches** | ✅ **sans objet** — les volumes de surface sont en **Zarr**, un chunk = une colonne de profondeur entière pour **1,78 Mo et 1,03 s**. Le problème du téléchargement disparaît |
| B2 | trouver le corpus | ✅ **81 segments** de Scroll 1 avec volume de surface, **80 avec une carte d'encre publiée** (récupérées), et **3 campagnes** : 45,5 / 2,4 / 1,13 µm |
| B3 | mesurer les 80 segments | ✅ **80 segments** mesurés. ⚠⚠ **L'instrument a été corrigé deux fois** (`12` §10) : l'intensité localise, le contraste non ; et l'écart se mesure **à la trace en µm**, pas en « tiers central » d'une fenêtre non centrée. Prédiction **reposée** : *écart médian > ~50 µm ⇒ pas d'encre lisible* |
| B4 | croiser avec les cartes d'encre **et** les croisements publiés | ✅ **les deux** : croisements `+0,388` (p = 0,0038, n = 54, `croisement_profondeur.json`) ; cartes d'encre **`19`** — et c'est là qu'est né le premier résultat qui change une décision |

## Voie C — la direction des fibres ⭐ valeur la plus haute

`06` §3.4, problème ouvert nº 5. **Discriminant physique**, donc déroulement pur.

| # | quoi | état |
|---|---|---|
| C1 | **tenseur de structure** → orientation locale | ✅ fait (`14`), cohérence jusqu'à **0,64** |
| C2 | **cohérence spatiale** de l'orientation | ✅ campagne finie, **80 segments** (`fibres_corpus.json`) |
| C3 | ⭐ les **deux instruments s'accordent-ils** ? | ❌ **non** — le signe s'INVERSE de n = 12 à n = 54 (+0,330 → −0,192). `14` |
| C4 | une **discontinuité** d'orientation marque-t-elle un saut de feuille ? | ❌ **écarté** avec C3 : la grandeur dont il dépend n'a pas survécu à la montée en puissance |

## Voie D — retrouver la feuille de Scroll 4

`12` §9. Le cœur de matière est hors des 65 couches ; de quel côté, à quelle distance ?

| # | quoi | état |
|---|---|---|
| D1 | mesurer **dans le volume**, le long de la normale à la trace, sans réengendrer de couches | ➡️ **repris et élargi** par la voie J de `18` : `champ_correction.py` mesure l'écart fenêtre par fenêtre, sur tout segment, sans réengendrer de couches |
| D2 | en déduire de combien la trace est décalée, et si c'est un décalage ou une dérive | ➡️ **c'est exactement** ce que `residuel` et `coherence_voisins` séparent (`18` voie J) |

## Voie E — les restes de géométrie

| # | quoi | état |
|---|---|---|
| E1 | vrai **ombilic** (`06` §2.3) — ⚠ 404 à l'adresse notée, chemin à retrouver | ➡️ `18` M1 |
| E2 | plus de bandes **niveau 0** : 2 faites, une migre et une non | ➡️ `18` M2 |
| E3 | **ESRF 2,4 µm** sur les 4 sites (`06` §3.6) | ➡️ `18` M3 |

## Voie F — cohérence de la doc, sans machine

| # | quoi | état |
|---|---|---|
| F1 | `10` §5 « bloqué sur le maillage » | ✅ corrigé — c'était une prudence mal placée, pas un fait matériel |
| F2 | `06` §7 C2 « le suivi PAS ENCORE » | ✅ **clos** : le suivi n'a pas été réparé, il a été **remplacé** |
| F3 | `06` §B « contrôle en aveugle » | ✅ **fait le 2026-08-17** (`09` §9), + la limite du voisin (`09` §12) |
| F4 | `06` §C « un second rouleau » | ✅ **répondu deux fois** : encre (cause en amont) et géométrie (métrique inapplicable) |


---

## Voie G — le passage à l'échelle ⭐⭐

Contrainte posée par l'auteur : la solution doit tenir sur les **53 rouleaux publiés** et
sur les **~800 de la villa**. Chiffrée, pas affirmée
(`analysis/src/cout_passage_echelle.py`) :

| rouleaux | donnée lue | 1 fil | 16 fils | **part du volume** |
|---:|---:|---:|---:|---:|
| 13 (le prix) | 1,3 Go | 6 min | < 1 min | **0,0042 %** |
| 53 (publiés) | 5,2 Go | 30 min | 4 min | 0,0042 % |
| **800 (la villa)** | **78 Go** | 7,2 h | **0,9 h** | **0,0042 %** |

> On lit **quatre millièmes de pour-cent** d'un rouleau pour le juger. C'est ce que
> permet un chunk OME-Zarr : il contient toute la colonne de profondeur d'une fenêtre,
> et les chunks se lisent indépendamment par HTTP. **On ne télécharge jamais un rouleau.**

⚠ **La colonne « 16 fils » est désormais MESURÉE** (×8,35, 2026-08-19), plus supposée.
La première version divisait par 16 — un parallélisme parfait — donc annonçait 0,5 h là
où la mesure dit **0,9 h**. Un modèle de coût qui se flatte n'est pas un modèle de coût.

⚠⚠ **Ce qui NE passe PAS à l'échelle, et il faut le dire** : la détection d'encre (42 min
par segment sur cet iGPU) et le **traçage** lui-même, qui reste semi-manuel. Nos
instruments **jugent vite ce que la production fait lentement** — c'est utile, et ce
n'est pas la même chose que dérouler 800 rouleaux.

| # | quoi | état |
|---|---|---|
| G1 | chiffrer le coût par rouleau | ✅ 97 Mo, 30 s pour un rouleau non tracé |
| G2 | extrapoler à 53 et 800 | ✅ 5,2 Go / 78 Go, part du volume **constante** |
| G3 | paralléliser réellement les campagnes | ✅ **×8,35 mesuré** (21,80 s → 2,61 s sur 16 fenêtres), sortie **bit-pour-bit identique** au sérialisé. `18` voie K |

## Voie H — la qualité de scan (nommée par le concours)

Le tableau des goulots de `2026_open_problems` dit, pour les régions comprimées :
*« What would help : **scan-quality metrics** »*.

| # | quoi | état |
|---|---|---|
| H1 | métrique de séparabilité (d′ feuille / interstice) | ✅ `analysis/src/separabilite_scan.py` |
| H2 | ⚠ sa **limite d'échelle**, mesurée | ✅ un d′ **baisse** quand on résout plus de structure : valide à résolution égale seulement |
| H3 | témoin apparié : même rouleau, deux protocoles | ✅ PHerc0139 en 9,362 **et** 2,399 µm |
| H4 | carte des 13 rouleaux du prix | ✅ **13 rouleaux mesurés** (`16`). Compression et médiane de qualité **écartées** ; c'est la **queue** qui sépare (témoin 0 %, les treize 4–24 %). `PHerc0358` désigné |


---

## ✅ Clôture du batch — 2026-08-19

**Les huit voies sont fermées**, chacune par une mesure ou par une raison écrite. Trois
items de géométrie (E1–E3) et la suite « produire » passent au batch suivant,
**`18_batch_produire.md`**, qui n'est pas une continuation de celui-ci : il attaque ce
que `00` §9 nommait comme le vrai manque — *aucun de nos instruments n'a encore changé
quoi que ce soit*.

| voie | verdict |
|---|---|
| A — proximité sur un second rouleau | ✅ **réplique**, et le rayon vient de la physique |
| B — profondeur, de l'anecdote à l'instrument | ✅ **80 segments**, corrélée aux croisements **et** à l'encre publiée |
| C — direction des fibres | ❌ **réfutée** : le signe s'inverse quand n monte |
| D — la feuille de Scroll 4 | ➡️ reprise et élargie par `18` voie J |
| E — restes de géométrie | ➡️ `18` voie M |
| F — cohérence de la doc | ✅ |
| G — passage à l'échelle | ✅ chiffré **et** réalisé (×8,35) |
| H — qualité de scan | ✅ métrique, limite d'échelle, témoin apparié, carte des 13 |

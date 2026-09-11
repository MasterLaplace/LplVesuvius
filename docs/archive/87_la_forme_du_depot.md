# 87 — La forme du dépôt, mesurée : ce qui est cassé et ce qui ne l'est pas

> ⚠⚠⚠ **La plainte de l'auteur — « plein de scripts dans tous les sens, des duplicata, des trucs
> abandonnés qu'on refait sans le savoir, aucun test » — est vraie sur trois points et FAUSSE sur
> le quatrième. Et la mesure a trouvé un défaut dans la garde qui existe pour empêcher exactement
> ça : `artefacts_orphelins` déclare « 0 orphelin » avec 46 % de son verdict reposant sur une tige
> de douze caractères ou moins.**

Ce document est l'instrument, pas un audit ponctuel : c'est lui qui dira si un refactor a servi.

## 1. Ce qui est faux dans la plainte, et il faut le dire d'abord

| | mesuré |
|---|---|
| « aucun test n'est réellement fait » | ⛔ **faux** : **267 / 356** modules (75 %) exposent `--verifier`, et **0** batterie n'est non enregistrée |
| les 89 sans batterie | `apprendre` 8/8 et `outils` 8/8 sont des **récits** et des **lanceurs** — une batterie n'y dirait rien. Les vrais trous : **`excision` 13/29 (45 %)** et **`volume` 8/17 (47 %)** |

⭐ Corriger ce point change les priorités : **les tests ne sont pas la panne.**

## 2. Ce qui est vrai, et chiffré

**Le graphe.** 356 modules, **393 arêtes** d'import. **152 (43 %)** n'importent aucun module du
dépôt ; **117 (33 %)** sont **isolés** — n'importent rien, ne sont importés par rien.

Le **noyau de fait** — ce que le dépôt partage réellement : `figure_commune` (77), 
`figure_le_residu_est_une_translation` (38), `zarr_depth` (22), `le_corpus_des_spires` (22),
`langue` (19), `le_raccrochage_a_la_matiere` (17).

**La duplication.** 26 noms définis dans 4 modules ou plus, **contrat de greffon écarté** —
`main`, `verifier`, `mesurer`, `dessiner`, `prose` sont la convention que `lplv` exploite, et les
compter annoncerait 338 doublons d'une convention utile. Restent : `_leve` ×19, `_pixels` ×14,
`lire` ×13, `charger` ×10, `comparer` ×10, `rapporter` ×10, `legende` ×9, `balayer` ×9.

## 3. ⭐⭐⭐ La vraie panne : on ne peut pas retrouver ce qu'on a déjà mesuré

| `docs/mesures/` — 486 artefacts | |
|---|---:|
| retrouvés par leur **nom complet** | **182 (38 %)** |
| retrouvés seulement après **troncature** | **303 (62 %)** |
| ⚠⚠ déclarés produits sur une tige de **≤12 caractères** | **224 (46 %)** |
| tige la plus courte acceptée | **4** — `juge_scroll4.json` matché par le mot `juge` |

⚠⚠⚠ **C'est le péché capital nº1 du dépôt, dans la garde qui existe pour ne rien perdre.**
`nomme_par` tronque la tige jusqu'à quatre caractères, donc un artefact est déclaré produit dès
qu'un mot de quatre lettres de son nom apparaît quelque part dans `src/`.

⚠ **Et le compromis est assumé dans sa propre docstring** : chercher le nom exact signalait
**389 orphelins sur 568**, et « une alerte qui désigne les deux tiers du corpus ne désigne rien ».
Le remède n'est donc **pas** un préfixe plus étroit — c'est que le producteur soit **DÉCLARÉ** au
lieu d'être deviné. C'est la cause mécanique de « on refait des trucs existants » : un chiffre
existe, personne ne peut retrouver son producteur par `grep`, donc quelqu'un le remesure.

## 4. ⭐⭐⭐ Et la mesure qui ANNULE un refactor

Idée de l'auteur : *« récupérer la liste de tous les mots du dépôt et regarder les plus utilisés,
ça peut faire des catégories ? »* — reformulée en la version qui marche. Pas les mots de la prose
(le dépôt est francophone, ils fuient des docstrings) mais le **vocabulaire de domaine** lu par
l'**AST**, et pas la fréquence mais la **co-occurrence** : *les dossiers correspondent-ils au
domaine, ou le coupent-ils en travers ?*

| dossier | n | cohésion interne | hors dossier | rapport |
|---|---:|---:|---:|---:|
| `apprendre` | 8 | 0,398 | 0,017 | **×23,9** |
| `rendu` | 5 | 0,141 | 0,013 | **×10,5** |
| `figures` | 105 | 0,125 | 0,022 | **×5,6** |
| `depot` · `nappe` · `tables` | 31·64·8 | ~0,045 | ~0,021 | ×2,0–2,3 |
| `encre` | 48 | 0,034 | 0,025 | ×1,35 |
| ⚠ `volume` | 17 | 0,024 | 0,021 | ×1,15 |
| ⛔ **`tracecheck`** | 5 | 0,009 | 0,015 | **×0,61** |

**Rapport global ×1,89.**

- ⛔ **`tracecheck` est sous le hasard** : ses cinq modules se ressemblent **moins entre eux**
  qu'avec un module tiré du reste du dépôt. Ce n'est pas un dossier, c'est cinq choses qui
  partagent un nom.
- ⚠⚠ **La cohésion absolue médiane est 0,0385** : deux modules d'un même dossier partagent **4 %**
  de leur vocabulaire. C'est la version chiffrée des 117 isolés — les modules ne partagent pas du
  code, ils **réexpriment chacun un domaine commun**.

⭐⭐⭐ **CONCLUSION QUI DÉCIDE : il ne faut PAS re-partitionner les dossiers.** Un reclassement par
domaine ferait passer ×1,89 à peut-être ×3 pour **353 déplacements de fichiers** — beaucoup de
churn, aucun gain sur la panne du §3. Ce que la mesure désigne est la **couche partagée** et la
**provenance déclarée**, pas le rangement.

## 5. Ce qui gonfle l'arbre sans être le dépôt

**2 `.venv` sous `src/`** portant **27 245 fichiers** — c'est pourquoi un `find` naïf annonce
30 657 `.py` là où le dépôt en a **356**. Plus **482 lanceurs gelés** dans `.lances/gel`. Et sur
**1 074** `.json` versionnés, **486** sont dans `docs/mesures/` : le reste vit dans quatre dossiers
de champ, hors du circuit des mesures nommées.

## 6. ⚠⚠ Une faute à moi, dans le module qui diagnostique les fautes

Mon compte de batteries enregistrées sortait à **zéro** : je faisais `Path(champ).name` sur
`"$ROOT/src/depot/x.py"`, guillemets compris. Et **mon contrôle n'assertait que « c'est un
entier »** — donc il a laissé passer un zéro qui était un bug. **Une vérification incapable
d'échouer, dans le module qui diagnostique les vérifications incapables d'échouer.** Le contrôle
borne désormais le compte par le bas : un compte effondré vient du découpage, pas du dépôt.

⚠ Et deux mesures antérieures à celle-ci étaient fausses et ont été jetées avant publication :
un compte de « 348 artefacts nommés nulle part » qui ne captait que les chemins littéraux, puis un
« 240 nommés nulle part » qui ignorait la troncature de la garde. Les deux sont dans le journal du
registre, parce qu'une mesure jetée est une leçon sur l'instrument.

## Reproduire

```
uv run python src/depot/la_forme_du_depot.py
uv run python src/depot/la_forme_du_depot.py --verifier
uv run python src/depot/la_forme_du_depot.py --json docs/mesures/la_forme_du_depot.json
```

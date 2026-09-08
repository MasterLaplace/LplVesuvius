# 91 — Le pas inter-feuilles, lu sur les transferts que l'humain a réussis

> ⭐⭐⭐ **L'étendue déclarée d'une bande EST son nombre de tours mesuré — écart médian −0,01 tour,
> 27 bandes sur 28 à moins d'un dixième. Et le pas lu sur ces transferts vaut 164 µm, contre
> 182,4 µm à l'atlas `winding-ruler`, par un chemin entièrement indépendant.**

![le pas lu sur les transferts](images/91_le_pas_lu_sur_les_transferts.png)

## 1. Pourquoi ces bandes sont la seule vérité de terrain du goulot

[`84`](84_une_surface_combien_de_spires.md) établit que `PHercParis4` publie **92 franchissements
de spire contenus dans une seule maille**, et **zéro** partout ailleurs. Une bande `wNNN-MMM` est
donc un **transfert de spire à spire déjà fait à la main** — et sa géométrie se lit **sans toucher
au volume**.

⚠ La lecture est valide parce qu'une **ligne** de grille est iso-z — écart-type **0,73 mm** contre
**41,8 mm** pour une colonne, qui court sur tout le rouleau. La pente est donc lue à hauteur
constante. **Vérifié, pas supposé.**

## 2. ⭐⭐⭐ Le nom d'une bande est sa géométrie

En déroulant l'angle le long d'une ligne de grille :

| | |
|---|---:|
| écart médian entre tours mesurés et étendue déclarée | **−0,01 tour** |
| bandes à moins d'un dixième de tour | **27 / 28** |
| ⚠ l'exception, nommée | `w010-027` : **12,75** pour 18 |

`w028-037` rend **9,97** tours pour 10, `w116-117` rend **1,99** pour 2. Les noms ne sont pas des
étiquettes.

## 3. ⭐⭐ Le pas, et deux instruments qui ne partagent rien

**164 µm** (136 à 207) sur les **12** bandes d'au moins 4 tours, contre **182,4 µm** publiés par
`winding-ruler` ([`86`](86_la_demi_feuille_par_objet.md)).

⭐ Les deux chemins n'ont **rien en commun** : l'atlas lit des **prédictions de surface** le long
de rayons sur un volume, ce fichier lit des **maillages publiés par des humains**. Deux instruments
qui ne partagent ni la donnée, ni la méthode, ni l'auteur, et qui s'accordent à 10 %.

## 4. ⚠⚠⚠ Un gradient rétracté avant d'être publié

La pente brute donne ~205 µm au cœur, ~145 au milieu, ~380 puis **~1000 µm au bord** — les
**16** bandes courtes rendent **391 µm** de médiane, un facteur 2,4. **On lirait une délamination
du bord.**

⭐ Le contrôle le tue, et il ne dépend d'aucune hypothèse : sur **UNE SEULE bande de dix tours**,
donc à pas constant **par construction**, ajuster la pente sur une fenêtre de plus en plus courte
donne

| fenêtre | 10 | 6 | 4 | 3 | 2 | 1 |
|---|---:|---:|---:|---:|---:|---:|
| pente | **202** | 208 | 224 | 287 | **523** | **1817** µm |

**Le pas ne change pas ; seule la fenêtre change.**

⭐⭐ **La règle qui en sort vaut pour tout marcheur : on ne mesure pas le pas d'un enroulement sur
un arc court.** Les bandes du bord n'en couvrent que deux, donc elles ne peuvent pas le mesurer.

## 5. ⚠⚠ Et la cause n'est PAS établie

Deux mécanismes testés sur fixture, **aucun ne rend l'ampleur** :

| mécanisme | 8 tours | 1 tour | verdict |
|---|---:|---:|---|
| cercle parfait | 200,0 | 200,0 | le plancher |
| **section ovale** `cos(2θ)` | 200,3 | **183,2** | ⛔ **dégonfle** — ma première explication, fausse |
| **centre décalé 1 mm** | 198,6 | 233,3 | gonfle, bon sens |
| **centre décalé 2 mm** | 194,1 | **269,5** | ⚠ il faudrait des **dizaines** de mm pour 1817 |

⭐ **Le contrôle tient sans la cause** : reproduire un biais sur des données dont on connaît la
réponse n'exige pas de l'expliquer pour le réfuter. Les deux explications réfutées sont **gardées
dans les contrôles**, pour qu'on ne les re-propose pas — une fixture ovale qui *dégonfle* est ce
qui empêche de réécrire ma première phrase.

## 6. Ce que ça donne au graal

⭐ Le pas de `PHercParis4` est **confirmé par deux instruments indépendants**, donc sa demi-feuille
— la tolérance d'une marche perdue — est un chiffre **établi** et non plus emprunté :
**82 à 91 µm** selon l'instrument, contre **67,75 µm** sur l'objet courant.

⚠ Et le coût d'un changement d'objet, que [`85`](85_le_sens_du_rang.md) disait non chiffré et que
[`86`](86_la_demi_feuille_par_objet.md) a chiffré à l'atlas seul, est maintenant **corroboré**.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/le_pas_lu_sur_les_transferts.py --verifier
uv run python src/nappe/le_pas_lu_sur_les_transferts.py \
    --json docs/mesures/le_pas_lu_sur_les_transferts.json
uv run python src/figures/figure_le_pas_lu_sur_les_transferts.py --verifier
```

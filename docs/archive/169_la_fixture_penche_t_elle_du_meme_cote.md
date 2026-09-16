# 169 — La fixture penche-t-elle du même côté que le rouleau ?

> ⭐⭐⭐⭐ **ELLE LE SUIT AUSSI BIEN, ET ELLE NE RENVERSE PAS AVEC LUI.** La cohérence — la persistance
> du penchant **dans** une marche — s'accorde aux **deux** caps : **0,758** contre **0,719** sans
> cap, **0,958** contre **0,925** avec. Le **côté**, lui, ne s'accorde qu'au cap zéro : le cap fait
> basculer le rouleau vers l'**axial** (**0,334** contre **0,193**) et la fixture reste
> **azimutale** (**0,147** contre **0,345**).
>
> ⭐⭐⭐⭐ **ET LE MÉCANISME EST LISIBLE, CAUSE PAR CAUSE.** L'**écrasement seul** penche
> **azimutalement** (**0,0** d'axial contre **0,343**) et suit **parfaitement** (**0,999**), sur
> **0** marche axiale sur 20. Le **froissement seul** penche **axialement** (**0,091** contre
> **0,061**) sur **14** marches sur 20 — et ne suit **pas** (**0,453**). **Les deux causes du dépôt
> tirent en sens opposés**, et le rouleau demande un penchant **axial ET cohérent** qu'aucun mélange
> des deux ne produit.
>
> ⭐ **LE CONTRÔLE TIENT, ET IL EN PORTE DEUX.** Ni la spirale nue ni l'écrasement seul ne glissent
> le long de l'axe : **0,0 µm**. Le glissement axial vient donc du **froissement** — **16,9 µm** à
> 42,4 d'amplitude, **33,0 µm** à 100.
>
> ⚠⚠⚠ **ET CETTE TRANCHE A ÉTÉ PUBLIÉE FAUSSE DEUX FOIS AVANT CELLE-CI.** Deux défauts de mesure
> distincts, tous deux à ma charge, racontés au §6 — et c'est une contradiction entre deux nombres
> déjà publiés qui les a fait sortir.

## 1. Pourquoi ce fichier, et un fait établi le désignait

`R4-F87` établit que l'écrasement mesuré **plus** un froissement approche le rouleau à **5,5 %** sur
**trois** grandeurs : le **rapport** des axes, le **penchant** et la **cohérence**. C'est cette
matière-là que la chaîne `161`–`168` emploie.

⭐⭐⭐⭐ **La direction du penchant n'est pas dans ces trois grandeurs.** Or `R4-F79` mesure sur le vrai
rouleau que le penchant est plus **axial** qu'azimutal — **0,334** contre **0,193** — et que le
marcheur glisse de **43,2 µm** le long de la longueur du rouleau à chaque pas. Personne n'avait
vérifié que la fixture penche du même côté, et la mesure existait déjà : `penchant()`, la fonction
qui a produit `R4-F79`, publie exactement ces deux parts.

## 2. Comment la comparaison est faite sans être truquée

⚠⚠ **Le même instrument, le même marcheur, le même échantillonnage.** La décomposition est
`penchant()`, celle de `R4-F79` ; le marcheur est `marcher`, celui de `100` ; et les départs
tournent **autour de la spirale** — dix angles à dix millimètres — comme ceux de `R4-F87`. Trois
choses à tenir égales, et le §6 dit ce qu'il en coûte d'en manquer une.

⚠⚠⚠ **Et CAP PAR CAP, jamais sur leur mélange.** `R4-F79` publie **deux** courses du rouleau, et
elles ne disent pas la même chose : le cap **renverse** le sens du penchant.

⚠⚠ **Le départ est assis SUR une feuille, et c'est vérifié.** Le recalage est une **recherche de
racine** bornée, pas un décalage : la phase n'est linéaire le long du rayon que sur une spirale
ronde. La borne est **dérivée** — un départ est sur sa feuille quand son reste de phase passe sous
ce qu'**un voxel** exprime, **0,013873** feuille. Mesuré sur les **100** départs : pire écart
**0,013362**.

⚠ **Et le départ se fait le long de la NORMALE**, jamais du rayon : sur la matière du rouleau elle
en est à 28–32°, et partir de travers coûte au marcheur ses premiers pas — donc précisément la
cohérence qu'on mesure.

⚠ **Les chiffres du vrai rouleau sont RELUS**, jamais recalculés, et le jugement **refuse de
conclure** si la mesure est absente.

## 3. ⭐⭐⭐⭐ La réponse, cap par cap

![La fixture suit aussi bien que le rouleau mais ne bascule pas vers l'axial sous le cap](../images/169_la_fixture_penche_t_elle_du_meme_cote.png)

| cap | | part axiale | part azimutale | penche | glissement | cohérence |
|---|---|---|---|---|---|---|
| **0,0** | la fixture | 0,209 | **0,308** | azimutalement | 34,8 µm | **0,758** |
| **0,0** | le rouleau | 0,348 | **0,405** | azimutalement | 57,5 µm | 0,719 |
| **0,75** | la fixture | 0,147 | **0,345** | **azimutalement** | 28,2 µm | **0,958** |
| **0,75** | le rouleau | **0,334** | 0,193 | **axialement** | 43,2 µm | 0,925 |

⭐⭐⭐ **Le suivi s'accorde aux deux, et la fixture est même un peu plus persistante que le rouleau.**
C'est ce que `R4-F87` avait calibré, et cette tranche le retrouve par un autre chemin.

✗ **Le côté ne s'accorde qu'au cap zéro.** Ce qui manque n'est pas un penchant, c'est un
**renversement** : le cap fait basculer le rouleau vers l'axial, et la fixture n'y bascule pas.

## 4. ⭐⭐⭐⭐ Les deux causes tirent en sens opposés

| matière | marches | axial | azimutal | glissement | cohérence | axial / azimutal |
|---|---|---|---|---|---|---|
| spirale nue | 20 | 0,0 | 0,002 | **0,0 µm** | 1,0 | 0 / 20 |
| spirale écrasée | 20 | **0,0** | **0,343** | **0,0 µm** | **0,999** | **0 / 20** |
| spirale froissée 42.4 µm | 20 | **0,091** | **0,061** | 16,9 µm | **0,453** | **14 / 6** |
| spirale écrasée et froissée 42.4 µm | 20 | 0,096 | 0,349 | 12,8 µm | 0,96 | 4 / 16 |
| spirale écrasée et froissée 100 µm | 20 | 0,206 | 0,334 | **33,0 µm** | 0,868 | 4 / 16 |

⭐ **L'écrasement donne la persistance et le mauvais côté ; le froissement donne le bon côté et pas
la persistance.** Mélangés, l'écrasement l'emporte sur la direction et le froissement coûte un peu
de cohérence. Le rouleau demande les **deux** ensemble, et c'est cela qu'aucune matière du dépôt ne
fabrique.

⚠ Sur la spirale nue et sur l'écrasée, la ligne « 0 / 20 » ne dit pas qu'elles penchent
azimutalement **par choix** : leur part axiale vaut exactement **0,0**. C'est pourquoi le contrôle
exige une **absence de glissement** et non un sens.

## 5. ⭐⭐⭐ Le glissement axial vient du froissement, pas de l'écrasement

C'est le second contrôle, et il est exact : l'**écrasement seul** rend **0,0 µm** de glissement
axial, exactement comme la spirale nue. Aplatir une spirale ne fait pas glisser le marcheur le long
de l'axe — c'est le froissement qui le fait, et la quantité croît avec son amplitude : **16,9 µm**
à 42,4, **33,0 µm** à 100.

## 6. ⚠⚠⚠ Deux défauts de mesure, et ce qui les a fait sortir

Cette tranche a publié **deux verdicts faux** avant celui-ci, et les deux venaient d'un défaut de
**protocole**, jamais d'un défaut de définition.

**Le premier : le verdict agrégeait les deux caps.** La fixture était comparée à la seule course
**capée** du rouleau pendant que son propre chiffre venait d'une médiane sur **cap 0 et cap 0,75
ensemble**. Or le cap **renverse** le sens : une médiane des deux régimes n'est le chiffre d'aucun.
⚠⚠ La mesure portait déjà la réponse — le module publiait un tableau `par_cap` et la figure le
dessinait. C'est **moyenner sur l'axe où vit la différence**, sur un axe que j'avais moi-même mesuré
et affiché.

**Le second : le marcheur ne partait pas sur une feuille, et pas dans la bonne direction.** Le
recalage était un décalage d'un **quart de pas**, recette écrite pour une spirale **ronde** ; sur
une section **écrasée** la phase se lit en coordonnées elliptiques. Mesuré : les départs tombaient à
**0,28 à 0,49 feuille** de la feuille la plus proche — pratiquement **entre deux feuilles**. Et le
départ se faisait le long du **rayon**, quand la normale y est à **28–32°**.

**Et un troisième, d'échantillonnage** : trois rayons à **un seul angle**. Sur une section écrasée
l'obliquité **tourne avec l'angle polaire**, de période π, donc le côté dépend de l'endroit où l'on
part. À un seul angle la cohérence rend **0,69** ; à dix angles, **0,958**. Même matière, deux
échantillonnages, deux réponses.

⭐⭐⭐⭐ **Ce qui les a fait sortir n'est pas une relecture, c'est une contradiction entre deux nombres
déjà publiés** : `R4-F87` publie une cohérence de **0,942** sur cette matière et cette tranche en
publiait **0,558**. Les définitions se sont révélées **identiques, ligne pour ligne** — donc la
différence ne pouvait venir que du **protocole**. Elle en venait, aux trois niveaux.

⚠ **Trois contrôles neufs le gardent désormais**, et les trois mordent : le départ tombe **sur** une
feuille, sous une borne **dérivée du voxel** ; le verdict d'assise **s'accorde avec la mesure** (une
première version lisait le drapeau du module, donc le figer à `True` la faisait passer) ; et la
comparaison est **refusée** sans découpage par cap.

## 7. Ce que cette tranche laisse

- **`R4-P27` se resserre, et pas là où je l'avais écrit deux fois** : ce qui manque aux fixtures
  n'est ni la persistance du penchant — elles l'ont — ni sa grandeur, c'est qu'aucune ne penche
  **axialement ET de façon suivie**. Les deux causes du dépôt se le disputent.
- ⚠ **`134` (le vrillage) se rouvre avec une cause nommée** : il faudrait une matière dont la
  normale sorte du plan du tour **toujours du même côté**, là où le froissement l'en fait sortir en
  **alternant**.
- ⚠ **Ce qui reste ouvert ailleurs est intact** : `167` mesure que la pince échoue à réparer
  **0,309859** des contradictions qu'elle rencontre, et rien ne dit de quoi elles sont faites.

## 8. Reproduire

```
uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py --verifier
uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py \
    --json docs/mesures/la_fixture_penche_t_elle_du_meme_cote.json
uv run python src/figures/figure_la_fixture_penche_t_elle_du_meme_cote.py --verifier
```

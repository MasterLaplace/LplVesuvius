# 51 — Une pente a deux appuis, et vingt séries rendaient le même nombre

2026-08-23. Trouvé en reprenant le mur nº 1 — *le tracé ne suit pas de feuille* — et en
ouvrant les profils des huit candidats de [`48`](48_ou_monter_lexperience.md) au lieu de
relire leur tableau.

![un écart au bord de la fenêtre est une flèche, pas un point](images/51_appuis.png)

Instrument : [`analysis/src/appui_de_pente.py`](../analysis/src/appui_de_pente.py)
(37 témoins) et [`figure_appuis.py`](../analysis/src/figure_appuis.py) (24 témoins).

---

## 1. ⚠⚠ Le refus de `49` existait, et il ne voyait pas son propre cas

[`49`](49_alpha_ne_separe_pas_deux_pannes.md) a appris à `test_convergence` à refuser une
série dont **aucune** fenêtre ne mesure rien. Le code agrège les amplitudes par un
**maximum**, avec sa raison écrite sur place :

> ⚠ On prend le MAXIMUM d'amplitude sur les fenêtres : si une seule fenêtre a du relief,
> la mesure n'est pas vide. Prendre la médiane condamnerait une série dont une fenêtre sur
> trois mesure quelque chose.

Cette règle est juste pour la question *« y a-t-il quelque chose ici ? »*. Elle est fausse
pour la question que α pose, qui est *« quelle est la pente ? »* — **une pente a deux
appuis, et un appui qui ne mesure rien n'en est pas un.**

Les trois candidats `ps256`, publiés dans `48` avec α = +1,01 · +1,17 · +1,01, ont tous
leur fenêtre étroite sous le seuil de détection :

| candidat | 41 couches | 161 couches |
|---|---|---|
| `ps256` c0 | écart 48,00 = demi-fenêtre · amplitude 0,0175 < 0,02 | écart 192,00 = demi-fenêtre |
| `ps256` c1 | écart 36,00 · amplitude 0,0193 < 0,02 | écart 177,60 |
| `ps256` c2 | écart 48,00 = demi-fenêtre · amplitude 0,0138 < 0,02 | écart 192,00 = demi-fenêtre |

## 2. ⭐⭐ Le remède n'est pas un refus de plus, c'est un SIGNE

Un écart posé sur la demi-fenêtre n'est pas une absence de donnée. C'est une **borne** : le
pic est au moins là, peut-être plus loin. Le dessiner comme un point rond affirme une
position ; le dessiner comme une flèche vers le haut dit ce qu'on sait, et rien de plus.

Et comme α = $\log(e_1/e_0)/\log(n_1/n_0)$ avec $n_1 > n_0$, la direction se
**déduit** au lieu de se deviner :

| appui au bord | α mesuré est | condamnation (α ≥ 0,7) | convergence (α < 0,7) |
|---|---|---|---|
| aucun | exact | ⭐ tient | ⭐ tient |
| **étroit** | un **majorant** | ⚠ ne tient pas | ⭐ tient |
| **large** | un **minorant** | ⭐ tient | ⚠ ne tient pas |
| les deux | rien | ⚠ ne tient pas | ⚠ ne tient pas |

⚠ Un appui **plat hors du bord** — amplitude sous le seuil, écart pas sur la demi-fenêtre,
le cas de `ps256` c1 — ne donne aucun signe : l'écart rapporté est l'argmax d'un bruit, ni
majorant ni minorant. Il vaut « rien », et le dire est plus honnête que de lui prêter une
direction.

## 3. ⚠⚠ Vingt séries rendaient exactement le même nombre

Quand les **deux** appuis sont au bord, α vaut
$\log(192/48)/\log(161/41) = 1{,}013497$ — une propriété du **couple de fenêtres**, et
de rien d'autre. L'instrument regroupe ces séries et **recalcule** l'identité depuis les
demi-fenêtres plutôt que de la recopier depuis α :

```
  ⚠⚠ 20 série(s) rendent un α qui est l'IDENTITÉ de leur couple de fenêtres — le même
     nombre, à la quatrième décimale, quels que soient la graine, la prédiction et le
     tirage :
      20 série(s)  41c→161c  α = +1.0135  = log(d₁/d₀)/log(n₁/n₀)
```

> ⭐⭐ **Vingt runs indépendants** — graines séparées par des kilovoxels, deux prédictions,
> plusieurs tirages du traceur — rendent la même valeur à la quatrième décimale. Ce n'est
> pas une mesure robuste, c'est une mesure absente. Et rien ne le signalait : chaque run
> pris isolément affiche un « α = +1,01 » parfaitement plausible, et leur **cohérence** est
> précisément ce qui les rendait convaincants.

C'est le même motif que le plafond de 60 générations de `48` §4 : un réglage pris pour une
raison qui a cessé d'être vraie ne se signale jamais tout seul, et la cohérence des
résultats qu'il produit est ce qui le rend invisible.

## 4. Le recensement de tout l'arbre

| | |
|---|---:|
| séries jugeables | **132** |
| à deux appuis mesurés — α exact | **92** |
| appui étroit au bord — α **majorant** | **14** |
| appui large au bord — α **minorant** | **0** |
| ⚠⚠ aucun appui qui porte | **26** |
| séries dont le verdict ne tient plus | **33** |
| séries sauvées par le **signe** de la borne | **7** |
| séries convergentes | **75** |
| ⭐ convergentes perdues | **0** |

> ⭐⭐ **Et cette fois la moitié rassurante a une RAISON, pas seulement un constat.** Le seul
> signe observé dans tout l'arbre est le **majorant** : quatorze séries ont leur appui
> étroit au bord, aucune n'a l'appui large. Un majorant place α vrai *en dessous* du
> mesuré, donc il préserve exactement ce qui est sous le seuil — c'est-à-dire les
> convergences. Les verdicts positifs ne survivent pas par chance : la direction de la
> borne les protège.

`49` disait déjà « aucun verdict positif n'est touché », et c'était vrai de *son* test.
Ce document le redit d'un test plus dur et en donne le mécanisme.

## 5. ⚠⚠ Ce que ça change pour le mur nº 1

**Sur les 27 séries `PHercParis4` de l'arbre, 26 tombent.** Toute la campagne — le 2×2, ses
seize répétitions, les huit candidats, le relèvement de plafond — repose sur des appuis qui
ne portent pas de verdict.

⭐ **Il en reste une, et elle condamne.** `paris4_croise/ps256_sur_graine_ps256` a ses deux
appuis mesurés : α = **+1,12**, borne exacte, verdict *suit la fenêtre*.

> Le mur nº 1 tient donc, et il tient **sur une mesure au lieu de vingt-sept**. C'est un
> résultat plus fragile à énoncer et plus solide à défendre : vingt-sept nombres dont vingt
> sont la même identité arithmétique ne sont pas vingt-sept témoignages.

⚠ **Ce qui, en revanche, ne tient plus** : la conclusion du 2×2 de `48`, *« ce n'est pas la
prédiction qui décide, c'est l'endroit »*. Elle comparait des écarts de 0,06 et 0,17 entre
cellules — or la plupart de ces cellules rendent l'identité +1,0135, donc leur accord est
arithmétique et pas empirique. Et l'« étendue de tirage » de 0,18 mesurée intra-cellule
mélange deux choses : la vraie variation du traceur, et le saut entre une cellule tombée
sur l'identité et une cellule qui mesure. **Les deux ne sont pas séparées.**

⚠ Ce qui reste vrai sans réserve : la trace ne se pose pas sur une feuille à cet endroit.
Un appui au bord *veut dire* « aucun pic dans la fenêtre », ce qui est la même conclusion
pratique. C'est la **quantification** qui tombe, pas le constat.

### ⚠ Et l'α le plus cité du dépôt n'est pas jugeable ici

`38`, et par lui `N5` et `M8` de [`29`](29_ce_qui_reste.md), reposent sur α = **+1,01** pour
notre trace. Cette série a quatre fenêtres et **un seul de ses profils est encore sur
disque** — donc l'instrument ne la juge pas : il faut deux profondeurs pour poser une pente.

Ce qu'on peut dire du profil survivant, et rien de plus : `data/leur_graine/profil_41c.json`
a un écart de **172,80 µm** pour une demi-fenêtre de 20 × 8,64 = **172,80 µm**, et une
amplitude de **0,0194** pour un seuil de 0,02. **C'est un appui au bord, et il est plat.**

> ⭐ Le verdict *pratique* survit sous les deux lectures — un appui au bord veut dire
> qu'aucun pic n'est dans la fenêtre, ce que `49` §4 disait déjà. ⚠ Ce qui reste hors de
> portée, c'est de rejuger la série : les trois autres profils ne sont pas dans l'arbre,
> donc les redemander veut dire relancer le rendu, pas relire un fichier.

## 6. Ce que ce document n'établit pas

- ⚠ **Que la fenêtre de 41 couches soit trop étroite pour ce rouleau.** L'amplitude passe de
  0,0175 à 0,0462 entre 41 et 161 couches sur `ps256` c0 : elle croît avec la fenêtre. Une
  fenêtre plus profonde mesurerait peut-être ; une fenêtre plus profonde mesure aussi une
  autre chose. La question appartient au test relatif de
  [`47`](47_le_critere_doit_etre_relatif.md), pas à celui-ci.
- ⚠ **Que les 26 séries tombées soient fausses.** Elles ne sont pas *jugées*. Un verdict
  retiré n'est pas un verdict inversé.
- ⚠ **Que le signe suffise toujours.** Il ne dit rien quand aucun appui n'est fixe, et c'est
  exactement le cas des vingt séries d'identité.

## Reproduire

```bash
python3 analysis/src/appui_de_pente.py --racine . --json docs/appui_de_pente.json
cd inference && uv run python ../analysis/src/figure_appuis.py \
    --json ../docs/appui_de_pente.json --sortie ../docs/images/51_appuis.png
cd inference && uv run python ../analysis/src/figure_appuis.py \
    --json ../docs/appui_de_pente.json --sortie ../docs/images/en/51_appuis.png --anglais

# le verdict porte désormais son appui
cd inference && uv run python ../analysis/src/test_convergence.py --nom ps256_c0 \
    --profil ../data/paris4_candidats/ps256_c0/profil_41c.json \
    --profil ../data/paris4_candidats/ps256_c0/profil_161c.json

# les témoins, hors ligne
python3 analysis/src/appui_de_pente.py --verifier
python3 analysis/src/figure_appuis.py --verifier
python3 analysis/src/test_convergence.py --verifier
```

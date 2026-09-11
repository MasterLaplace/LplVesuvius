# 118 — La fenêtre du marcheur est globale, l'espacement des feuilles est local

> ⭐⭐⭐⭐ **LES DEUX BOUTS DE LA FENÊTRE SONT DE VRAIS PAS, ET `117` SUPPOSAIT LE CONTRAIRE.** Son
> §5 avançait — sans le mesurer — qu'au bout long la matière demandait un saut de feuille et qu'au
> bout court elle demandait un pas qui ne traverse rien. **Les deux suppositions sont fausses.**
> L'espacement local qu'impliquent les pas en butée vaut **80,7 µm** au bout court et **380,2 µm**
> au bout long : de part et d'autre de la fenêtre [86,5 ; 346,0], exactement comme une butée le
> prédit. Le marcheur demandait un pas que sa fenêtre ne sait pas exprimer.
>
> ⭐⭐⭐⭐ **ET LE CONTRÔLE EST CE QUI REND CES DEUX NOMBRES LISIBLES.** Sur les **287** pas libres
> déductibles, l'espacement déduit s'accorde au pas choisi à un rapport médian de **1,015**
> [0,955 ; 1,070], rho **+0,7515**. Là où la fenêtre ne borne pas, l'optimiseur cherchait une
> feuille et l'a trouvée : la fraction franchie est donc calibrée, et son usage aux bouts tient.
>
> ⭐⭐⭐ **LA VARIATION N'EST PAS RADIALE**, donc un pas nominal fonction du rayon ne la rattraperait
> pas : rho **+0,2895** (p **0,2293**) sur 19 marches, et les deux bouts se rencontrent aux mêmes
> rayons (14,70 mm contre 13,63, p **0,7729**). Ce qu'il faut est une fenêtre centrée sur
> l'espacement **mesuré localement**.
>
> ⭐ **Zéro lecture distante** : tout se calcule sur les 560 étapes que `113` a gardées.

## 1. Pourquoi ce fichier, et ce qu'il corrige

`117` a mesuré que **63 pas voyants sur 382** sont refusés parce que l'optimum de longueur tombe au
bord de la fenêtre de candidats — 43 au bout court (86,5 µm), 20 au bout long (346,0 µm), zéro entre
les deux. Il en a tiré, **par raisonnement et non par mesure**, que les deux bouts ne voulaient pas
dire la même chose.

⚠⚠ **Cette phrase de `117` §5 est retirée par ce document**, et elle est le genre d'erreur que ce
dépôt recense : un raisonnement plausible publié à la place d'un compte que les données portaient
déjà. La correction ne se fait pas sur place — `117` reste tel qu'il a été écrit — elle se fait ici.

## 2. ⭐⭐⭐⭐ Ce que la fenêtre exclut

Le registre garde, à chaque pas, la **fraction de feuille réellement franchie**. Un pas de longueur
`L` qui franchit `f` feuille implique donc un espacement local de `L / f`.

| | pas déductibles | espacement déduit | q1 | q3 |
|---|---:|---:|---:|---:|
| bout court (86,5 µm) | 42 | **80,7 µm** | 74,1 | **85,5** |
| bout long (346,0 µm) | 17 | **380,2 µm** | **349,5** | 409,5 |

Le **troisième quartile** du bout court est sous la borne basse, et le **premier quartile** du bout
long est au-dessus de la borne haute. Ce n'est donc pas « parfois » : aux deux bouts, l'espacement
que la matière montre est majoritairement hors de la fenêtre.

## 3. ⚠⚠ Le contrôle, sans lequel ces deux nombres ne valent rien

La fraction franchie a **sa propre fenêtre** [0,35 ; 3,2] et **sa propre butée**, et son fichier
l'écrit : *« sur du bruit pur la valeur sature en haut de la fenêtre une fois sur deux »*. Un
rapport de deux bornes ne mesure rien.

- **Les pas dont la fraction est elle-même en butée sont écartés** — 43 → 42 au bout court, 20 → 17
  au bout long. Écartés plutôt qu'inclus avec une réserve : une réserve dans un texte ne retire pas
  le nombre de la médiane.
- **Et sur les pas LIBRES, le déduit doit s'accorder au choisi.** Là où la fenêtre ne borne pas,
  l'optimiseur a cherché une feuille, donc le pas retenu EST une estimation de l'espacement.

| | |
|---|---:|
| pas libres déductibles | **287** |
| rapport médian choisi / déduit | **1,015** |
| q1 – q3 | 0,955 – 1,070 |
| rho | **+0,7515** |

⚠ Le rapport est **apparié**, pas comparé entre médianes — et ma première lecture s'y est trompée :
181,7 contre 150,0 se lisait comme 21 % de biais, alors que le rapport apparié vaut 1,015. Deux
médianes de deux distributions ne disent rien de l'accord pas à pas.

⚠ La bande d'acceptation (±10 % sur la médiane du rapport) est déclarée **dans le code, avant le
résultat**. La choisir après avoir vu 1,015 serait la régler.

## 4. ⭐⭐⭐ Où ces espacements tombent dans ce qui est déjà publié

`R2-F07` mesure l'espacement entre parties non adjacentes sur 4 000 cellules : **p5 101 · p50 177 ·
p90 303 µm**. Les deux bouts tombent donc **dans les queues** de cette distribution, pas au milieu.

La distinction change le remède. Une fenêtre mal **placée** se recentre ; une fenêtre qui couvre le
gros de la distribution et rate ses extrêmes doit soit s'élargir — ce qui coûte des candidats, donc
du temps de lecture — soit se **centrer localement**.

## 5. ⭐⭐⭐ Et la variation n'est pas radiale

| | |
|---|---:|
| espacement médian par marche contre rayon (19 marches) | rho **+0,2895**, p **0,2293** |
| rayon médian, bout court | **14,70 mm** |
| rayon médian, bout long | **13,63 mm** |
| les deux bouts se distinguent-ils par le rayon | p **0,7729** |

⚠⚠ L'unité du test est la **MARCHE** et non le pas : les vingt pas d'une marche partagent son rayon
et son départ, donc un test par pas prendrait 287 observations pour 28.

⚠ n = 19 marches exploitables : un rho qui tombe **cesse de rejeter** l'absence d'effet, il ne la
prouve pas. Et `R2-F07` mesure bien une tendance radiale (158 µm au cœur → 203 dehors, +28 %) sur
4 000 cellules ; ce document ne la contredit pas, il dit qu'elle est trop faible pour expliquer des
écarts d'un facteur cinq sur 19 marches.

## 6. Ce que ça change pour le graal

- Les 63 pas refusés par la fenêtre ne sont pas des demandes absurdes : ce sont des pas que la
  matière montre et que l'instrument ne sait pas exprimer. La borne supérieure de **0,9122** de
  `117` reste une borne, mais elle cesse d'être une borne « peut-être vide ».
- ⭐ Le remède n'est **pas** un pas fonction du rayon : la variation ne suit pas le rayon. C'est une
  fenêtre centrée sur l'espacement **mesuré à l'endroit du pas**, ce que le dépôt sait déjà faire
  ailleurs (`R2-F08` utilise un espacement **local**).
- ⚠ Ce qui reste à faire est une **re-course**, pas une relecture : centrer la fenêtre localement et
  voir lesquels des 63 pas deviennent des pas mesurés. C'est `R4-P24`, resserrée par ce document.

## 7. Les registres

Faits : `R4-F45` (la fenêtre exclut de vrais pas aux deux bouts), `R4-F46` (la variation n'est pas
radiale). Porte `R4-P24` **resserrée** — elle demandait quel bout cachait un vrai pas, la réponse
est **les deux**, et ce qui reste est de savoir si une fenêtre locale les récupère. Aucune porte
ouverte : ce document répond, il ne demande pas.

## Reproduire

```bash
uv run python src/nappe/la_fenetre_est_globale_lespacement_est_local.py --verifier   # 21 contrôles
uv run python src/nappe/la_fenetre_est_globale_lespacement_est_local.py \
    --json docs/mesures/la_fenetre_est_globale_lespacement_est_local.json
```

⚠ **Aucune lecture distante**, et **aucune figure** : le résultat tient en six nombres et deux
comparaisons de quartiles. Une figure y serait une décoration, pas un argument.

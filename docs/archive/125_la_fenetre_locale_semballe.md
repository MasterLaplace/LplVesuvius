# 125 — La fenêtre locale s'emballe sur la vraie matière : la boucle était circulaire

> ⚠⚠⚠ **LA RE-COURSE A TROUVÉ LE DÉFAUT EN UNE BANDE, ET IL EST DANS CE QUE `122` A ÉCRIT.** La
> fenêtre qui suit l'espacement local part de **1,000** et atteint **32,6645** — une amplitude de
> **×549** — avec un pas de **7644,4 µm**, soit **44,2 feuilles**.
>
> ⚠⚠⚠ **ET ELLE N'A PAS AIDÉ : ELLE A EMPIRÉ.** Part des pas en butée **0,2202** contre **0,1649**
> pour `113` à fenêtre fixe ; taux de confirmation **0,7156** contre **0,7618**. Elle était écrite
> pour retirer la butée ; elle en ajoute.
>
> ⭐⭐⭐⭐ **LA CAUSE EST STRUCTURELLE.** L'espacement suivi vaut `avance / feuilles franchies`, or
> `avance` est choisi **dans la fenêtre déjà mise à l'échelle**. La boucle n'a aucune force de
> rappel : elle a un point fixe à **n'importe quelle** échelle où la fraction vaut un, et la
> fraction vaut un facilement à toute échelle puisque le gabarit est rééchantillonné sur le
> candidat. Mesuré : rho **+0,8916** (p 7,6·10⁻³⁶) entre l'échelle d'un pas et l'espacement qu'il
> déduit.
>
> ⚠⚠ **ET LA DÉMONSTRATION DE `122` NE POUVAIT PAS LE VOIR.** Une pile fabriquée n'a **qu'un** pas
> vrai, donc le profil ne s'accorde qu'à cet endroit et la boucle est ramenée à chaque pas. La
> fixture ne pouvait pas produire l'ambiguïté dont la panne a besoin.

## 1. Ce qui a été lancé, et pourquoi il a été arrêté

La re-course a été lancée avec le plafond dérivé de **112 pas**, la fenêtre locale et l'arrêt sur
vide, sur 8 bandes. La première bande a demandé **3 296 s** et a rendu de quoi arrêter : l'échelle
de la fenêtre avait parcouru trois ordres de grandeur.

⚠ La suite aurait coûté sept heures de lecture sur une configuration dont la première bande dit
qu'elle est cassée. Le run a été arrêté et relancé **sans** la fenêtre locale, qui n'est pas en
cause pour `R4-P20`.

⭐ Et la bande garde une bonne nouvelle au passage : l'**arrêt sur vide a fonctionné**. La marche
s'est arrêtée sur « plus rien a lire » au pas **109**, et non au plafond — cinq fois plus loin que
les vingt pas de `113`.

## 2. ⚠⚠⚠ Ce que l'échelle a fait

| | |
|---|---:|
| échelle au départ | **1,000** |
| minimum | **0,0595** |
| maximum | **32,6645** |
| amplitude | **×549,0** |
| pas le plus long | **7644,4 µm** |
| soit, en feuilles nominales | **44,2** |

Une fenêtre qui suit l'espacement doit **osciller** autour de la vérité. À un facteur cinq cents,
elle n'oscille plus.

⚠ Sortir de la fenêtre publiée [0,5 ; 2,0] n'est pas en soi une panne — c'est le but de `R4-P24`.
S'en éloigner d'un facteur dix en est une, et c'est le critère que la batterie applique.

## 3. ⭐⭐⭐⭐ Le diagnostic, et il est arithmétique

L'espacement suivi est `avance / f`. Or `avance` est borné par la fenêtre, donc par l'échelle. Si
l'échelle d'un pas prédit l'espacement qu'il déduit, la quantité suivie n'est pas une mesure de la
matière : c'est une mesure de la fenêtre.

| | |
|---|---:|
| rho entre l'échelle et l'espacement déduit | **+0,8916** |
| p | 7,6·10⁻³⁶ |
| pas déductibles | 101 |

⚠⚠ **Ce rho n'est pas un résultat, c'est une démonstration.** Le lien est garanti par la
construction ; le mesurer sert à montrer que la quantité suivie n'est pas indépendante de ce
qu'elle règle. Le nommer évite de le lire comme une corrélation intéressante.

⚠ La sonde de la batterie remet une course où l'avance **ne suit pas** la fenêtre, et le test doit
alors dire que la boucle est rompue — sans quoi il répondrait « circulaire » à n'importe quoi.

## 4. ⚠⚠ Pourquoi la pile fabriquée ne pouvait pas le montrer

`122` a démontré la fenêtre locale sur un empilement dont le pas décroît, et elle y retirait la
butée entièrement (3 → 0). Ce n'était pas une erreur de mesure : sur cette pile, **le profil ne
s'accorde qu'au pas vrai**, donc chaque pas ramène la fenêtre vers lui.

Sur la vraie matière le profil s'accorde sur une **plage** — c'est d'ailleurs ce que `117` mesure
autrement, avec ses 63 pas dont l'optimum tombe au bord — et il n'y a plus rien pour ramener.

⭐ **La leçon est transportable, et elle est le vrai résultat de ce document** : une fixture
analytique dont la réponse est **unique** ne peut pas produire l'ambiguïté dont une boucle de
rétroaction a besoin pour s'emballer. Elle valide donc le mécanisme **là où il ne peut pas
échouer**.

## 5. ⚠⚠⚠ Et c'est une mauvaise lecture de `118`, à ma charge

`118` concluait : *« il faut une fenêtre centrée sur l'espacement **mesuré à l'endroit du pas** »*.
J'ai implémenté *« centrée sur l'espacement **déduit du pas précédent** »*.

Les deux phrases se ressemblent et ne disent pas la même chose. La première demande une mesure
**indépendante** de la fenêtre ; la seconde en fait une fonction de la fenêtre, donc une boucle.

⚠ `R4-F50` n'est pas rétracté : il dit ce qu'il a mesuré, sur une pile à réponse connue, et c'est
vrai. Ce qui tombe est l'**extrapolation** qu'on pouvait en tirer, et sa note le dit désormais.

## 6. Ce que ça change pour le graal

- `R4-P24` reste ouverte et son dessin change : la fenêtre doit suivre un espacement **mesuré
  indépendamment**, pas déduit du pas qu'elle a elle-même choisi. Le dépôt sait le faire ailleurs —
  `R2-F07` mesure l'espacement local sur 4 000 cellules sans marcher.
- ⭐ Ce que `121` a établi ne bouge pas : recentrer est gratuit, élargir coûte un nul. C'est **ce
  qu'on recentre dessus** qui était faux.
- ⚠ Et le plafond de 112 pas, lui, tient : la marche a fait **109 pas** avant de cesser de lire,
  donc le plafond dérivé n'était pas un budget déguisé.

## 7. Les registres

Faits : `R4-F54` (la fenêtre locale s'emballe et empire la butée), `R5-F22` (une fixture à réponse
unique ne peut pas produire la panne d'une boucle). Porte `R4-P24` **rouverte** avec le dessin
corrigé. La note de `R4-F50` dit ce que la vraie matière en fait.

## Reproduire

```bash
uv run python src/nappe/la_fenetre_locale_semballe.py --verifier   # 13 contrôles
uv run python src/nappe/la_fenetre_locale_semballe.py \
    --json docs/mesures/la_fenetre_locale_semballe.json
```

⚠ **Aucune lecture distante** : tout se calcule sur la bande que la re-course a écrite avant d'être
arrêtée, gardée dans `docs/mesures/la_fenetre_locale_sur_la_vraie_matiere.json` avec son drapeau
`course_incomplete`.

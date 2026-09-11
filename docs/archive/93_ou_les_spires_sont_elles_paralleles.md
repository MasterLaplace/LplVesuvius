# 93 — Où les spires voisines sont-elles parallèles ? Au milieu

> ⭐⭐⭐ **Un marcheur transfère en avançant le long de la NORMALE. Ce pas n'atterrit sur la spire
> voisine que si les deux spires sont parallèles. Mesuré sur les transferts que l'humain a
> réussis : quasi parallèles à mi-rayon (×1,23), désalignées au bord (×4,18), et non résolues sur
> les deux bandes les plus internes.**

![où les spires sont-elles parallèles](../images/93_ou_les_spires_sont_elles_paralleles.png)

## 1. Pourquoi cette question précède toute construction

À un désalignement de trente degrés, un pas de 182 µm tombe à **91 µm de côté** — la moitié du pas
lui-même. Savoir où les spires sont parallèles, c'est savoir **où un pas géométrique suffit**, et
où il faut autre chose.

## 2. ⭐⭐⭐ La réponse est un U

| bande | rayon | rot./cellule | adjacent | **un tour** | rapport |
|---|---:|---:|---:|---:|---:|
| `w010-027` | 4,1 mm | **13,3°** | 11,6° | 42,4° | ⚠ non résolue |
| `w073-076` | 14,0 mm | 3,2° | 6,2° | **7,7°** | **×1,23** |
| `w128-129` | 23,8 mm | 1,9° | 6,3° | **26,3°** | **×4,18** |

Par tiers : **cœur ×1,88 · milieu ×1,80 · bord ×3,67**.

⭐ Ce n'est donc **ni « pire au cœur » ni « pire au bord »** : c'est **minimal au milieu**.

## 3. ⚠⚠⚠ Les deux bandes les plus internes ne sont pas désalignées, elles sont NON RÉSOLUES

`w010-027` n'a que **27 colonnes par tour**, donc sa normale est moyennée sur **13,3° d'arc par
cellule** — plus que son propre désaccord entre cellules adjacentes (11,6°).

⭐ **Quand la rotation d'une seule cellule dépasse la variation locale de la surface, l'estimateur
mesure l'échantillonnage et non la matière.** Le critère d'exclusion est **dérivé** de cette
comparaison, pas choisi. Il exclut exactement deux bandes.

## 4. ⭐⭐ Les deux modes d'échec sont au BORD, pas aux deux bouts

| | continuité (`92`) | parallélisme (ici) |
|---|---|---|
| milieu | **1,7 à 5,9×** | **×1,23** |
| bord | **31×** | **×4,18** |

Un automate a donc un problème **localisé**, pas uniforme : au bord la surface est **brisée** *et*
les spires y sont **désalignées** ; au milieu les deux sont propres.

## 5. ⚠⚠⚠ Une erreur à moi qui a inversé la conclusion

Mon exploration comparait la **bande 0** à la **bande 7** en appelant la seconde « le bord » —
alors que **les deux sont dans le tiers intérieur**. J'en avais tiré *« désaligné au cœur,
parallèle au bord »*, soit exactement l'inverse.

> **Un tiers se compte sur le corpus entier, pas sur les premières lignes d'un tableau.**

## 6. ⚠⚠ Et le « plancher » n'est pas un plancher de bruit

Le désaccord entre cellules **adjacentes** est dominé par la **rotation** de la normale d'une
cellule à l'autre — 13,3° au cœur, 1,9° au bord — et non par la rugosité. Preuve : une spirale
**parfaite** échantillonnée à 60 colonnes par tour rend **6,0°**, soit exactement **360/60**.

⚠ Il reste un repère **utile** — il est mesuré à la même résolution que le signal — mais l'appeler
« bruit » serait faux, et c'est ce mot qui m'a fait construire la mauvaise comparaison.

⚠⚠ Le repère **trompeur** est gardé lui aussi : comparée à une spirale parfaite (**0,4°**), la
mesure semblait 14 à 19 fois trop grande **partout**. Une spirale parfaite n'a **aucune rugosité**.

## 7. ⭐ Le contrôle qui valide la méthode est dans la mesure

Une normale de spirale **tourne** avec l'angle : à un quart de tour elle doit maximalement
diverger, à un tour entier elle doit **revenir**. Mesuré : **62 à 66°** au quart de tour contre
**7,7 à 42°** au tour. Sans ce retour, la mesure ne suivrait pas la spire.

⚠ Et un défaut d'outillage attrapé au passage : **`--verifier` est resté vert à 17 contrôles
pendant que `main()` plantait** sur une clef renommée. L'affichage vit désormais dans
`main_affichage(r)`, **que la batterie lance** — une batterie qui n'emprunte jamais le chemin de
l'utilisateur ne garde pas ce que l'utilisateur voit.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/deux_modes_dechec_du_transfert.py --verifier
uv run python src/nappe/deux_modes_dechec_du_transfert.py \
    --json docs/mesures/deux_modes_dechec_du_transfert.json
uv run python src/figures/figure_ou_les_spires_sont_elles_paralleles.py --verifier
```

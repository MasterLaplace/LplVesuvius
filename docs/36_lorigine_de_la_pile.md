# L'origine de la pile — d'où se mesure un écart à la trace

2026-08-20, après-midi. ⏳ **Ce document porte un résultat mesuré et un contrôle en cours.**
Il est écrit avant que le contrôle rende, parce que les documents qu'il met en cause sont
cités activement — et qu'une réserve écrite après coup n'a protégé personne.

---

## 1. L'hypothèse, et où elle est vérifiée

Tout l'instrument de profondeur de [`12`](12_profondeur_de_surface.md) se rapporte à **la
couche tracée**, et son §13 le dit sans détour :

> *« Tout l'instrument se rapporte à la couche tracée, **supposée** au milieu de la pile
> (`shape[0] // 2`) parce que le volume de surface est engendré autour d'elle
> (`vc_layers_from_ppm -r 32`). C'est l'hypothèse la plus lourde du dispositif. »*

Et `12` §13 la **vérifie** — sérieusement, sur 98 segments :

| corpus | couches | trace supposée | pic observé |
|---|---:|---:|---:|
| Scroll 1 (80 segments) | 109 | 54 | **53** |
| PHerc1667 (18 segments) | 109 | 54 | **55** |

⭐ **Mais elle la vérifie sur les volumes de surface PUBLIÉS**, ceux qu'engendre
`vc_layers_from_ppm` autour de la trace. Nos propres piles viennent d'un **autre
producteur** — `vc_flatten` puis `vc_render_tifxyz` — et cette chaîne-là n'a jamais été
vérifiée. L'hypothèse a été **transportée d'un producteur à l'autre** sans le dire.

## 2. ⭐⭐ Ce que la mesure dit

Deux segments **officiels** du même rouleau du prix, `PHerc1447` — donc deux surfaces qui
suivent leur feuille par construction, puisque l'équipe du concours les publie pour être
lues :

| producteur | segment | couches | **écart médian** | tiers central | au bord |
|---|---|---:|---:|---:|---:|
| **volume de surface publié** | `20250702235910` | 31 | **3,0 µm** | **62,5 %** | 12,5 % |
| **notre `vc_flatten` → `vc_render_tifxyz`** | `auto_grown_20250502160708188` | 61 | **237,6 µm** | **2 %** | 38 % |

> **Un facteur 79 sur l'écart.** Soit un segment officiel est à 238 µm de sa propre
> feuille — ce qui n'est pas crédible pour une surface publiée pour être lue — soit
> **l'origine de nos piles n'est pas celle qu'on suppose**.

⚠ **Ces deux lignes portent sur des segments DIFFÉRENTS**, donc elles confondent le
producteur et le segment. C'est exactement pourquoi le contrôle ci-dessous existe.

## 3. ⏳ Le contrôle qui tranche — en cours

`tools/origine_de_la_pile.sh` prend **un seul** segment officiel qui publie **les deux** —
son `tifxyz` et son volume de surface — et le mesure des deux façons. Le confond disparaît
par construction.

| issue | ce qu'elle voudrait dire |
|---|---|
| **différence > 50 µm** | l'origine diffère selon le producteur, et tout écart mesuré depuis un rendu à nous est pris depuis un mauvais point |
| **différence < 50 µm** | l'hypothèse du milieu transporte, et les 237 µm du segment officiel sont une propriété de **ce segment-là** |

⚠ Et le remède, si c'est la première : ce n'est pas de renoncer à l'instrument, c'est de
**calibrer l'origine** — un segment officiel suit sa feuille, donc la position de son pic
*est* la couche tracée pour cette géométrie de rendu.

⚠⚠ **La chaîne suspecte contient DEUX étages**, et cette expérience ne les sépare pas :
`vc_flatten` s'intercale entre le maillage et le rendu chez nous, et pas chez eux. Ce qui
serait établi est que **notre chaîne** décale l'origine, pas lequel de ses deux maillons.

## 4. Ce qui en dépend — et il faut le dire avant de savoir

| document | ce qui serait touché |
|---|---|
| [`24`](24_premiere_trace_rouleau_du_prix.md) §2 | *« écart médian pic ↔ couche tracée : 94 µm »* — une des trois jambes qui condamnaient la trace |
| [`25`](25_une_graine_choisie_sur_la_planeite.md) | le critère du **tiers central**, **retiré** au motif qu'un segment officiel y échouait (2 % contre 16 et 20 %) |
| [`35`](35_le_tirage_sur_douze_rouleaux.md) et le second axe | 32 rendus, tous mesurés depuis le milieu supposé |
| [`21`](21_texte_de_soumission.md) | le §9 reprend le tiers central et son retrait |

⭐⭐ **Et la conséquence la plus intéressante est une réhabilitation, pas une perte.** `25`
a retiré le critère du tiers central parce qu'*« un critère que la référence rate plus mal
que le cas jugé ne peut pas servir à juger »*. Le raisonnement est juste ; sa prémisse ne
l'est peut-être pas. Si l'origine est décalée, la référence ne ratait pas le critère — **on
la mesurait depuis le mauvais point**, et un critère parfaitement utilisable a été rangé
pour cette raison.

⚠ Ce serait la deuxième fois aujourd'hui qu'une conclusion tombe non pas parce que la
mesure était bruitée, mais parce qu'elle était **décalée** : un décalage a l'air d'un
résultat, là où du bruit a l'air de bruit. Voir aussi [`34`](34_un_verdict_qui_ne_mesure_rien.md),
où un filtre transformait des croisements réels en zéros silencieux.

## 5. ⚠ Ce que ce document ne dit pas

- **Il ne dit pas que `vc_render_tifxyz` est fautif.** Un rendu le long de la normale n'a
  aucune obligation de centrer sa pile sur la surface ; c'est une convention, et il se peut
  qu'elle soit documentée quelque part que nous n'avons pas lu. Ce qui est fautif est de
  l'avoir **supposée** identique à celle d'un autre outil.
- **Il ne mesure pas encore de correction.** Tant que le contrôle n'a pas rendu, aucun
  chiffre de `24`, `25` ou `35` n'est retiré — ils sont **signalés**, ce qui est différent.
- **Il ne remet pas en cause `12` §13.** Cette vérification-là est bonne, et sur 98
  segments. Ce qui a échoué est le **transport** de sa conclusion à un autre producteur.

## Reproduire

```bash
# le volume de surface publié d'un segment officiel de PHerc1447
cd inference_xpu
uv run python ../analysis/src/zarr_depth.py \
  "PHerc1447/segments/20250702235910-auto_grown_20250702235910292/surface-volumes/8.64um-1.2m-116keV-volume-20250521151220.zarr" \
  --windows 25 --out ../docs/origine_officiel_PHerc1447.json

# le contrôle : le MÊME segment, mesuré des deux façons
./tools/lancer.sh --fond tools/origine_de_la_pile.sh
```

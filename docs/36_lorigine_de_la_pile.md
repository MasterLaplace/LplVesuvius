# L'origine de la pile — une hypothèse testée, réfutée, et ce qu'elle a trouvé à la place

2026-08-20. ⚠⚠ **Ce document a été écrit sur une hypothèse, et la mesure l'a réfutée.** Il
est conservé sous cette forme parce que la réfutation a produit un résultat meilleur que
l'hypothèse — et parce qu'effacer une piste fausse fait perdre la raison pour laquelle on
l'avait suivie.

---

## 1. L'hypothèse, et pourquoi elle était sérieuse

Tout l'instrument de profondeur de [`12`](12_profondeur_de_surface.md) se rapporte à **la
couche tracée**, et son §13 le dit sans détour :

> *« Tout l'instrument se rapporte à la couche tracée, **supposée** au milieu de la pile
> […]. C'est l'hypothèse la plus lourde du dispositif. »*

`12` §13 la **vérifie** — sur 98 segments, et le pic observé tombe à une couche du milieu
supposé. Mais il la vérifie sur les **volumes de surface publiés**, engendrés autour de la
trace par `vc_layers_from_ppm -r 32`. Nos piles viennent d'un **autre producteur** —
`vc_flatten` puis `vc_render_tifxyz` — et cette chaîne n'avait jamais été vérifiée.

Deux chiffres rendaient le soupçon lourd. Sur des segments **officiels** de `PHerc1447`,
donc publiés pour être lus :

| producteur | segment | écart médian | tiers central |
|---|---|---:|---:|
| volume de surface publié | `20250702235910` | **3,0 µm** | 62,5 % |
| notre chaîne de rendu | `auto_grown_20250502160708188` | **237,6 µm** | 2 % |

Un facteur **79** — mais sur des segments **différents**, donc confondant le producteur et
le segment.

## 2. ⭐⭐ Le contrôle, et il tranche contre l'hypothèse

`tools/origine_de_la_pile.sh` prend **un seul** segment officiel qui publie les deux — son
`tifxyz` et son volume de surface — et le mesure des deux façons.

| producteur | couches | écart médian | tiers central | au bord |
|---|---:|---:|---:|---:|
| volume de surface publié | 31 | **3,00 µm** | 62,5 % | 12,5 % |
| notre `vc_flatten` → `vc_render_tifxyz` | 31 | **17,28 µm** | **100 %** | **0 %** |

> ✅ **14,3 µm d'écart sur le même segment. Les deux producteurs s'accordent.** L'hypothèse
> du milieu **transporte**, et notre chaîne place sa pile au moins aussi bien : elle rend
> **100 %** de pics dans le tiers central là où le volume publié en rend 62,5 %.

⚠ **Le seuil de décision était écrit avant la mesure** (50 µm, dans le script), avec ses
deux issues et leur signification. C'est ce qui empêche de relire un résultat de 14 µm comme
« presque une confirmation ».

## 3. ⭐⭐⭐ Ce que la réfutation a trouvé à la place

Si le producteur n'explique pas les 237,6 µm, alors c'est **le segment**. Et ça pose une
question que personne n'avait posée : **un segment officiel est-il une référence ?**

Les **quatre** segments de `PHerc1447` qui publient un volume de surface, lus par le même
instrument (`docs/officiels_PHerc1447.json`) :

| segment | fenêtres avec matière | **tiers central** | écart médian |
|---|---:|---:|---:|
| `20250703025628` | 22 / 50 | **68,2 %** | 3,0 µm |
| `20250702235910` | 24 / 50 | 62,5 % | 3,0 µm |
| `20250703034159` | 22 / 50 | **18,2 %** | 10,5 µm |
| `20251105093211-z_dbg_gen_00320` | ⚠ **4** / 50 | 25,0 % | 11,0 µm |

> ⚠⚠ **« Officiel » n'est pas synonyme de « bon ».** Sur un seul rouleau, le tiers central va
> de **18 % à 68 %** — un facteur 3,7 — et le quatrième segment s'appelle littéralement
> `z_dbg_gen_00320`, un artefact de débogage, avec 4 fenêtres exploitables sur 50.

## 4. ⭐⭐ Ce que ça corrige dans `25`, et le sens n'est pas celui prévu

[`25`](25_une_graine_choisie_sur_la_planeite.md) a **retiré** le critère du tiers central en
écrivant :

> *« La trace officielle d'un rouleau du prix […] échoue au critère du tiers central plus
> mal que les nôtres : 2 %, contre 16 et 20 %. Un critère que la référence rate plus mal que
> le cas jugé ne peut pas servir à juger. »*

Le **raisonnement est juste**. Ce qui ne l'est pas, c'est de traiter **un** segment officiel
comme **la** référence. Sur ce même rouleau, deux autres segments officiels rendent 62 % et
68 % — soit trois à quatre fois mieux que nos traces, ce qui est exactement le
comportement qu'on attendrait d'une référence.

⏳ **Le critère mérite donc d'être reconsidéré** — pas parce que la mesure était fausse, mais
parce que **la référence n'en était pas une**. ⚠ Reconsidéré, pas rétabli : le remettre
demande de choisir une référence sur un motif défendable, et « le meilleur des quatre » n'en
est pas un.

## 5. Ce qui n'est PAS touché

- [`24`](24_premiere_trace_rouleau_du_prix.md) §2, *« écart médian 94 µm »* : la mesure tient,
  l'origine est bonne. Le signalement posé ce matin est **retiré**.
- [`37`](37_les_deux_axes_ne_saccordent_pas.md) : ses valeurs absolues tiennent aussi, en
  plus de la comparaison intra-producteur qui était déjà à l'abri.
- `12` §13 : intact, et c'est même lui qui avait raison — sa conclusion transporte.

⚠ Il reste vrai que les seize rendus de `37` lisent des écarts de **146 à 187 µm**, contre
3 à 11 µm pour les segments officiels publiés. Ce n'est donc pas un artefact de mesure :
**nos traces sont réellement loin de leur feuille**, d'un ordre de grandeur, et c'est le
fait le plus dur de la journée pour la suite.

## 6. ⚠ Ce que ce document ne dit pas

- **Il ne dit pas que les segments officiels sont mauvais.** Deux des quatre sont excellents.
  Il dit qu'il faut **regarder lequel** avant de s'en servir comme référence.
- **Le contrôle porte sur UN segment.** Un seul same-segment suffit à réfuter « le
  producteur décale systématiquement », pas à établir qu'il ne décale jamais.
- **La chaîne a deux étages** (`vc_flatten`, `vc_render_tifxyz`) et le contrôle les teste
  ensemble. ⓘ Le bucket publie un `<segment>_flattened.obj` : leur chaîne aplatit aussi, donc
  ce sont deux exécutions de la même forme, pas deux formes différentes.

## Reproduire

```bash
./tools/lancer.sh tools/origine_de_la_pile.sh          # le même segment, deux fois
cd inference_xpu                                        # les quatre segments publiés
for k in $(cut -f2 ../docs/volumes_surface_PHerc1447.txt); do
  uv run python ../analysis/src/zarr_depth.py "$k" --windows 25
done
```

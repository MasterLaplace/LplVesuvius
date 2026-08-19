# Une graine choisie sur la planéité — et deux défauts qu'on croyait n'en faire qu'un

2026-08-19, suite de [`24`](24_premiere_trace_rouleau_du_prix.md). Le traceur suivait
n'importe quoi ; on lui donne enfin une raison de partir au bon endroit.

**Résultat en une ligne** : la même chaîne, le même rouleau, les mêmes paramètres, **une
seule chose changée — la graine** : **240 auto-intersections → 0**, sur une surface
**2,3 fois plus grande**. Et la profondeur, elle, n'a pas bougé d'un pouce : ce sont
**deux défauts distincts**, et la graine n'en règle qu'un.

---

## 1. Le critère précédent ne classait rien, et personne ne l'avait remarqué

`docs/24` a choisi sa graine par la **moyenne d'un cube de voisinage**, en écartant
explicitement l'`argmax` — *« un pic isolé est du bruit »*. Le raisonnement était bon. Le
résultat, non :

```
   score  -s x y z (niveau 0)
   255.0  1544 1544 7768
   255.0  4108 1544 7688
   255.0  1544 3848 7688
   255.0  3868 4408 7728
   ... huit candidats, huit fois 255
```

⚠⚠ **255 est le plafond du format.** La prédiction est **seuillée** (`th0.2`), donc
binaire : tout bloc entièrement dans la matière prédite atteint la borne. Huit candidats à
égalité ne sont pas un classement, c'est **un tirage au sort déguisé en mesure** — et
c'est le piège nº 2 du dépôt (*une valeur identique partout = saturation contre sa propre
borne*), payé sans que rien ne le signale.

Le chercheur de graine **le dit maintenant** : quand tous les candidats retenus partagent
le même score, il l'écrit en clair au lieu de rendre un classement muet.

## 2. La planéité, et pourquoi elle ne peut pas saturer

On cherche un endroit où la prédiction forme **un plan**, pas un endroit où il y en a
beaucoup. Le tenseur de structure 3D le donne en forme close :

    J = ⟨∇f ∇fᵀ⟩       λ₁ ≥ λ₂ ≥ λ₃       planéité = (λ₁ − λ₂) / λ₁

Le raisonnement est **physique**, pas statistique :

| situation | ce que fait le tenseur | planéité |
|---|---|---:|
| **une** feuille traverse le bloc | tous les gradients le long de sa normale | **1,00** |
| **deux feuilles parallèles** | les normales sont encore alignées | **1,00** |
| une **jonction** à 90° | deux directions peuplées, λ₂ monte | **0,00** |
| du bruit isotrope | trois directions équivalentes | 0,04 |
| un bloc uniforme (vide ou plein) | tenseur **nul** — écarté, pas classé | — |

⭐ **La deuxième ligne est celle qui compte.** Un empilement régulier de feuilles
parallèles est exactement l'endroit où l'on veut poser une graine, et un critère qui le
pénaliserait chercherait « peu de matière » au lieu de « matière bien rangée ». Ce qui
fait tomber le score, c'est **la jonction** — précisément l'endroit où le traceur peut
passer d'une spire à l'autre sans que rien dans la prédiction ne l'en empêche.

⚠ **Le biais d'orientation est mesuré, pas supposé.** Une prédiction seuillée est binaire,
donc un plan incliné y est un **escalier**, et les marches peuplent une seconde direction.
Sur un plan synthétique tourné de 0° à 90°, la planéité brute descend de 1,000 à **0,828**
(écart 0,172). Un lissage 3³ avant les gradients ramène l'écart à **0,053** — et le biais
résiduel reste très loin sous le signal, puisqu'une jonction rend 0,000.

## 3. ⚠⚠ Le même piège, un étage plus haut, repayé une passe plus tard

La première version prenait l'`argmax` de la planéité sur les blocs d'un chunk. Résultat :
**quatre candidats à 1,0000 exactement**.

> Un chunk de 192³ contient **13 824 blocs** de côté 8. Le maximum d'un score borné par 1
> sur autant de tirages vaut ~1 **quel que soit le terrain**. *Le maximum d'un échantillon
> nombreux ne décrit pas l'échantillon.*

C'est mot pour mot le défaut que le paragraphe précédent venait de corriger, à un étage de
plus — et je l'ai écrit **dans le fichier qui documentait déjà le piège**. Le classement
retenu est donc :

1. la planéité **moyennée sur le voisinage 3³ de blocs**, limitée aux blocs qui passent la
   barrière d'occupation ;
2. les ex æquo tranchés par le **nombre de voisins valides** — une graine au milieu d'un
   empilement propre et étendu vaut mieux qu'une graine sur le bord d'un éclat isolé,
   planaire par accident ;
3. chaque chunk rapporte en plus sa **part planaire**, une propriété de la *région* qu'un
   maximum ne peut pas fabriquer.

Après quoi le classement discrimine enfin — la part planaire va de **0,121 à 0,967** — et
les niveaux 0 et 1, calculés indépendamment, **désignent le même endroit** (à un tiers de
chunk près). Le critère saturé, lui, ne s'accordait avec rien.

⚠ **La graine rendue est un voxel ALLUMÉ**, pas le centre du bloc : le centre géométrique
d'un bloc traversé en biais tombe dans le vide, et le traceur part alors de rien. L'ancien
code rendait le centre ; il a marché **par chance**, sur un bloc saturé donc plein.

## 4. ⭐⭐ Le résultat : 240 → 0

Un seul paramètre changé — la graine. Mêmes `seed.json`, même prédiction, même machine.

| | A — voisinage (`24`) | **B — planéité** | officiel `PHerc1447` |
|---|---:|---:|---:|
| graine (x y z) | 1544 1544 7768 | **5842 5839 7386** | 5340 3584 22669 |
| aire | 8,48 cm² | **19,82 cm²** | 2,89 cm² |
| triangles | 48 040 | 112 338 | — |
| paires testées | 387 151 | **852 135** | 388 083 |
| **auto-intersections transverses** | **240** | **0** | **0** |
| pénétration maximale | 21,5 vx = 201 µm | **0** | 0 |

⭐ **La colonne de droite est le contrôle qui rend le résultat lisible.** C'est un segment
**officiel** d'un rouleau du prix (`PHerc1447`), et son `meta.json` dit
`source: "vc_grow_seg_from_seed"`, `mode: "explicit_seed"`, `min_area_cm: 0.3` — **la même
chaîne que la nôtre**, pilotée par l'équipe du concours. Il rend 0 auto-intersection.
Notre graine planaire aussi ; notre graine par voisinage, non.

⚠ **Et l'aire n'est pas un critère.** La trace officielle en fait 2,89 cm², sept fois moins
que la nôtre. Ce qui compte pour First Letters, c'est **4 cm² portant dix lettres** — pas
la surface, et surtout pas une surface qui traverse les spires.

⚠⚠ **Et l'aire ne mesure même pas ce qu'on croit** — troisième saturation de la journée,
après le score de voisinage contre 255 et l'argmax contre 1,0. Les deux traces planaires
s'arrêtent à la **génération 119 sur 120** et rendent respectivement **19,821 592** et
**19,823 246 cm²** : deux rouleaux différents, deux graines différentes, la même aire à
**huit millièmes de pour-cent près**. Ce n'est pas une coïncidence, c'est un **plafond** :
la surface croît par un front, donc son aire est fixée par le nombre de pas quand rien ne
l'arrête. Les traces par voisinage, elles, **calent** — génération 79 sur PHerc0358,
génération 26 sur PHerc0125.

> La grandeur qui a un sens n'est donc pas l'aire mais **« le traceur a-t-il consommé son
> budget ou s'est-il arrêté avant »**. L'aire n'en est le proxy que tant qu'on ne relève
> pas le budget.

### Les deux traces, à la même échelle

![deux traces du meme rouleau](images/25_deux_traces.png)

⚠⚠ **La figure est à échelle physique commune** — sans quoi une surface deux fois plus
grande passerait pour identique. À gauche, les deux plaques écartelées de `24` : c'est ce
que devient une surface qui se recoupe quand on l'aplatit. À droite, une nappe d'un seul
tenant.

⚠ **Mais regardez les striations à droite.** Elles s'enroulent, bifurquent et se
superposent, exactement comme à gauche. Le règlement demande *« can you visually follow
horizontal papyrus fibers across the page »* : la réponse est **non**, des deux côtés. La
trace B ne se recoupe plus ; elle ne suit pas pour autant **une** feuille. L'œil dit ici la
même chose que le §5, et il le dit après les mesures, pas avant.

## 5. ⚠⚠ Ce que la graine ne règle PAS — et c'est la moitié du résultat

L'instrument de profondeur de [`12`](12_profondeur_de_surface.md) devait confirmer.
Il a refusé, et il a eu raison de refuser.

**Première mesure, fausse par construction.** Sur la pile de 21 couches de `24`, la trace B
rendait **62 % de pics au bord** — c'est-à-dire le verdict de la mauvaise trace. Sauf que
21 couches à 9,362 µm valent **±94 µm**, soit **une demi-distance inter-feuilles** (187 µm
mesuré sur ce rouleau) : la fenêtre est presque entièrement *dans* la feuille. Amplitude
médiane du profil : **1,5 %**, et **61 % des profils sont plats**.

> ⚠⚠ **Un profil plat a quand même un maximum, parfaitement défini, et sa position est du
> bruit** — qui sort aux deux extrémités et imite une bimodalité. C'est le piège nº 20 du
> dépôt (*afficher la courbe avant de croire son argmax*), et il est désormais **dans
> l'outil** : `depth_profile.py` rapporte l'amplitude, la part de profils plats, et refuse
> de laisser lire « au bord » sans le dire quand plus de la moitié sont plats.

**Deuxième correction : une fenêtre spatiale est aussi une échelle.** Moyenner sur 9,6 mm
mélange des endroits où la feuille n'est pas à la même profondeur — c'est précisément le
**champ de correction** de [`20`](20_le_champ_de_correction.md). Mesuré, en rétrécissant la
fenêtre sur la même pile :

| fenêtre | amplitude médiane | profils plats |
|---|---:|---:|
| 9,6 mm | 3,5 % | 22 % |
| 4,8 mm | 3,4 % | 15 % |
| 2,4 mm | 5,4 % | 7 % |
| **1,2 mm** | **8,7 %** | **1 %** |

**La comparaison honnête, à taille physique égale (1,2 mm) et sur ±281 µm :**

| trace | amplitude | pic dans le tiers central | pic au bord |
|---|---:|---:|---:|
| `20230909121925` — Scroll 1, **AUC 0,925** | **50,1 %** | **77 %** | **5 %** |
| `scroll4_20231111135340` — l'échec connu de `12` §9 | 19,3 % | 13 % | 29 % |
| notre **A** (voisinage) | 14,8 % | 16 % | 27 % |
| notre **B** (planéité) | 8,7 % | 20 % | 28 % |
| ⭐ **officiel `PHerc1447`** — rouleau du prix | 28,8 % | **2 %** | 38 % |

⚠⚠ **Et c'est la dernière ligne qui décide — dans l'autre sens que prévu.** La trace
**officielle** d'un rouleau du prix, faite avec le même outil par l'équipe du concours,
échoue au critère du tiers central **plus mal que les nôtres** : 2 %, contre 16 et 20 %.
Ses pics ne sont pas décalés d'un cran constant, ils sont **étalés sur les 61 couches**.

> Donc le critère « pic dans le tiers central », calibré sur Scroll 1, **ne sépare pas les
> traces sur les rouleaux du prix**. Il est hors de son domaine de validité, et l'instrument
> ne peut pas départager B de A tant qu'il ne départage pas non plus l'officielle du reste.

⚠ **Cela oblige à corriger `24`.** La trace A y était condamnée par *trois* instruments ;
l'un des trois — la profondeur — s'avère muet sur ce rouleau. Le verdict tient toujours,
parce que les deux autres suffisent (240 auto-intersections avant tout rendu, et l'image),
mais il tient sur **deux** jambes et non trois. Corrigé sur place, `24` §2.

Ce qui reste lisible dans cette table, c'est l'**amplitude**, et elle ordonne : Scroll 1
(50 %) ≫ officiel rouleau du prix (28,8 %) > notre A (14,8 %) > notre B (8,7 %).
⚠ Mais elle mélange deux causes — la qualité de la trace et celle du **scan** — et les deux
lignes du milieu ne portent pas sur le même rouleau. La seule façon de les séparer est de
tracer **nous-mêmes** `PHerc1447`, où une trace officielle existe pour comparer à volume
égal. C'est ce que fait `tools/campagne_graines.sh`.

⚠⚠ **Donc la graine planaire a supprimé les auto-intersections sans qu'on puisse encore
dire si elle rapproche la trace de la feuille.** Ce sont deux questions distinctes, et une
seule a aujourd'hui un instrument valide sur ces rouleaux.

- **Où l'on part** décide si la surface se recoupe. C'est réglé.
- **Comment on avance** décide si elle reste sur *une* feuille. Ça ne l'est pas.

Et la seconde a un nom, déjà écrit dans `24` §4 : le traceur n'a reçu **aucune information
d'orientation** (`direction_fields` absent). Une bonne graine ne peut pas s'y substituer —
elle place le premier pas, pas les 112 337 suivants.

## 6. Reproduire

```bash
cd experiments
S="PHerc0358/representations/predictions/surfaces/20250821151737-surface-20260413222639-surface-m7-L0-th0.2.zarr"
uv run python ../analysis/src/trouver_graine.py "$S" \
    --level 0 --chunks 25 --bloc 8 --critere planarite --voxel-um 9.362

cd ../data/trace/PHerc0358/essai_b
B=https://vesuvius-challenge-open-data.s3.amazonaws.com
vc_grow_seg_from_seed -v "$B/$S" -t . -p seed.json -s 5842 5839 7386
vc_tifxyz_selfcross --surface auto_grown_* -o selfcross_b.json   # ⚠ JUGER AVANT DE RENDRE
vc_flatten -i auto_grown_* -o flat_b
V="$B/PHerc0358/volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
rm -rf render_b61   # ⚠ un outil qui saute ses sorties existantes saute aussi les tronquees
vc_render_tifxyz -v cache_vol --remote-url "$V" --scale 1 -g 0 -s flat_b \
    --tif-output render_b61 -n 61 --slice-step 1 --auto-crop

cd ../../../inference_xpu
uv run python ../analysis/src/depth_profile.py ../data/trace/PHerc0358/essai_b/render_b61 \
    --grid --size 128 --step 128 --traced-layer 30 --voxel-um 9.362
```

⚠ **`seed.json` doit porter `"voxelsize"`**, sinon l'aire vaut 0 et toute surface est
rejetée. ⚠ **La fenêtre de rendu doit valoir plus d'un écart inter-feuilles**, sinon la
mesure de profondeur ne peut rien voir — `-n 61` et non `-n 21`.

## 7. Les témoins

22 contrôles hors ligne (`tools/temoins.sh`, batterie « graine : planarite »), et **chacun
a été vérifié cassable** : cinq sondes remplacent une garde par sa version fautive et la
batterie doit tomber.

| sonde | ce qu'elle casse | témoins qui tombent |
|---|---|---:|
| `enroulement` | l'agrégation 3³ enroule au lieu de répliquer | 1 |
| `centre_du_bloc` | la graine redevient le centre géométrique | 1 |
| `sans_barriere_trace` | un bloc à tenseur nul est classé | 1 |
| `argmax_sans_voisinage` | on reprend l'argmax brut | 1 |
| `sans_lissage` | le biais d'orientation n'est plus corrigé | 1 |

⚠ **Trois de ces cinq sondes passaient au vert à la première tentative** : mes fixtures ne
pouvaient pas échouer. La feuille du test de graine traversait le centre du bloc, donc
rendre le centre était indistinguable de rendre un voxel allumé ; la barrière sur la trace
était redondante avec la bande d'occupation sur des données binaires ; et le chunk de
contrôle n'avait aucun éclat isolé, donc l'argmax brut trouvait la bonne moitié tout seul.
Refaites, les cinq tombent.

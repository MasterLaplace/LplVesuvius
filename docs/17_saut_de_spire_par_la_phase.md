# Détecter un saut de spire par la phase d'enroulement publiée — ❌ ÉCHEC (définitif, §10)

> ⚠⚠ **Verdict final : la mesure NE MARCHE PAS.** À n = 38, rho **+0,149** (p = 0,37).
> L'effet s'est évanoui à mesure que l'échantillon grandissait — **+0,517 (n=8) →
> +0,306 (n=30) → +0,149 (n=38)** — ce qui est la signature de l'absence d'effet, pas
> d'un effet modeste. Le §3 ci-dessous raconte l'enquête ; le §7 tire la leçon.

2026-08-18. Le tableau des goulots de `2026_open_problems` réclame, pour les sauts de
spire : *« stronger local continuity constraints and **conservative failure
detection** »*. Voici une tentative, et son verdict — qui n'est pas celui qu'on espérait.

---

## 1. La quantité, et pourquoi elle est la bonne

`00` §2 le dit : *« ce qui manque est le numéro d'enroulement — la seule quantité qui
rende le sheet switching nommable : deux points d'une même feuille le partagent, un saut
l'incrémente »*.

⭐ **Elle est publiée.** Le groupe `lasagna` de chaque rouleau expose un canal `cos` — le
cosinus de la phase d'enroulement, par voxel, en OME-Zarr, chunks 32³ à ~32 Ko
compressés. **Quatre rouleaux l'ont**, dont les trois qui ont des traces.

⚠ **Mesuré avant de théoriser, et ça a évité une erreur.** J'attendais une période par
feuille — auquel cas un saut d'**exactement** une spire serait **invisible**, le pire cas
possible. Mesuré : la période vaut **3 à 7 fois le pas inter-feuilles** (614 à 1228 µm
pour un pas de ~170 µm). Le champ est **diffusé**, donc un saut y laisse une marche
d'une fraction de période.

## 2. ⚠⚠ Un bug de conception, écrit dans mon propre docstring

Le principe est : sur une trace correcte la phase varie continûment d'une cellule **à sa
voisine**, et un saut est une discontinuité. Le docstring le disait ; **le code prenait
une cellule sur quarante**. Les points comparés étaient à quarante colonnes l'un de
l'autre, et la continuité entre voisins — la seule chose qu'un saut brise — n'était pas
mesurée.

Le symptôme était visible et je ne l'ai vu qu'en lisant la sortie : la trace **la plus
atteinte** (17 croisements) avait le p99 et le max **les plus bas** du lot, et une trace
**propre** montait à max = 124. Signal inversé, c'est-à-dire aucun signal.

Corrigé en **segments contigus de 48 cellules**.

## 3. Le verdict : positif, cohérent, et NON ÉTABLI

| n | statistique | rho ~ croisements | p | rho détectable |
|---:|---|---:|---:|---:|
| 8 | marche médiane | +0,498 | 0,210 | **0,85** |
| 8 | p95 | +0,517 | 0,190 | 0,85 |
| **30** | marche médiane | **+0,301** | 0,105 | **0,49** |
| **30** | **p95** | **+0,306** | **0,100** | 0,49 |
| 30 | p99 | +0,219 | 0,246 | 0,49 |
| 30 | max | +0,167 | 0,378 | 0,49 |

**Le signe tient** sur les quatre statistiques et sur les deux tailles d'échantillon —
contrairement à la mesure des fibres, où il s'est **inversé** entre n = 12 et n = 54.
Mais **l'amplitude fond** de +0,50 à +0,30 quand n passe de 8 à 30, ce qui est le
comportement attendu d'un effet réel mais modeste, ou d'un effet nul mesuré deux fois.

> ⚠⚠ **À n = 30, un rho de 0,30 n'est pas détectable.** Établir cette valeur demanderait
> **n ≈ 85**. PHerc0139 en offre 38 ; avec PHerc1667 (20) et PHerc0814 (13) on monte à
> **71** — encore court.

## 4. ⭐ Le test qui ne dépend d'aucun tiers

Nos deux instruments mesurent la même chose par deux chemins sans rapport : l'un lit la
**phase d'enroulement** le long de la paramétrisation, l'autre l'**écart entre la feuille
et la surface tracée** dans le volume de surface. Sur les **mêmes 30 segments** :

| | rho | p |
|---|---:|---:|
| marche de phase (p95) ~ écart feuille↔trace | **+0,242** | 0,198 |
| marche de phase (p95) ~ tiers central | **−0,256** | 0,172 |

**Les deux signes sont ceux qu'on attend** — plus de discontinuité de phase va avec une
feuille plus loin de la trace, et avec moins de fenêtres centrées. Mais à n = 30 ils
restent sous le seuil de détection.

## 5. ✅ Ce que la même campagne a établi, en revanche

L'instrument de profondeur atteint la significativité sur **PHerc0139** —
rho **+0,369, p = 0,045** contre les croisements publiés. C'est son **troisième corpus** :

| corpus | grandeur | rho | p |
|---|---|---:|---:|
| Scroll 1 (n = 54) | tiers central | **−0,487** | < 0,001 |
| PHerc1667 (n = 18) | pic d'intensité | **+0,698** | 0,001 |
| **PHerc0139 (n = 30)** | **écart à la trace** | **+0,369** | **0,045** |

**Trois rouleaux, trois fois le bon signe, deux fois sous 0,05.**

## 6. ❌ *(sans objet — le §10 a tranché)* Ce qu'il faudrait pour trancher le détecteur

⚠ Conservé pour que le raisonnement reste lisible, mais **la question est fermée** : le
volume `cos` n'a pas de niveau plus fin que celui utilisé, et la quantification n'écrase
rien (marche médiane 12,2 / 255, **0 trace sur 38** à médiane nulle).

1. **n ≈ 85** — soit les trois corpus tracés réunis, avec leurs chemins `lasagna`
   respectifs.
2. ⚠ Vérifier un soupçon non levé : à quelle distance les cellules voisines d'une trace
   tombent-elles dans le champ de phase ? Si huit cellules du maillage partagent un
   voxel au niveau 3, la plupart des marches valent **zéro par construction**, et la
   mesure porterait sur les rares transitions de voxel plutôt que sur la trace.
3. Un référent meilleur que le compte de croisements, qui `06` §3.8 a montré ne pas
   prédire la lisibilité.

## Reproduire

```bash
./src/campagnes/campagne_saut_spire.sh docs/saut_spire
cd inference_xpu
uv run python ../src/tables/table_saut_spire.py ../docs/saut_spire \
    ../repos/windcheck/results/index.json
```


---

## 7. ❌ Le verdict, et la courbe qui le donne

| n | rho ~ croisements (p95) | p | rho détectable à 80 % |
|---:|---:|---:|---:|
| 8 | **+0,517** | 0,190 | 0,85 |
| 30 | **+0,306** | 0,100 | 0,49 |
| **38** | **+0,150** | **0,368** | 0,44 |

> **Un effet réel ne fond pas quand on l'échantillonne mieux.** Un effet nul, si — et
> c'est exactement ce qu'on voit : chaque fois que n monte, rho se rapproche de zéro.

À n = 38 la mesure détecte un rho de 0,44 ; le +0,15 observé est très en dessous. Ce
n'est pas « pas assez de puissance » : c'est que la valeur elle-même s'effondre à mesure
que la puissance monte.

**La marche de phase entre cellules voisines ne prédit pas les croisements recensés.**

## 8. Ce qu'on garde de l'échec

1. ⭐ **La donnée existe et se lit.** Le canal `cos` du `lasagna` est publié pour quatre
   rouleaux, chunks 32³ à ~32 Ko, lisible à distance. Personne d'autre ne l'exploite
   pour juger une trace, et le lecteur est écrit.
2. ~~⚠ Le soupçon non levé reste la meilleure piste : refaire au niveau 0 ou 1
   changerait peut-être tout.~~ **RÉFUTÉ le 2026-08-19, deux fois** — voir le §10.
3. ⚠⚠ **La discipline a payé trois fois aujourd'hui.** Les fibres (signe **inversé** de
   n=12 à n=54), ce détecteur (amplitude **divisée par 3,5** de n=8 à n=38), et — dans
   l'autre sens — l'instrument de profondeur, qui a **tenu** sur trois corpus. Sans la
   règle « rapporter la puissance avec le résultat », on aurait publié deux faux.

## 9. Ce qui a tenu, pour comparaison

| instrument | corpus | rho | p |
|---|---|---:|---:|
| **profondeur** | Scroll 1 (n = 54) | −0,487 | < 0,001 |
| **profondeur** | PHerc1667 (n = 18) | +0,698 | 0,001 |
| **profondeur** | PHerc0139 (n = 30) | +0,369 | 0,045 |
| fibres | Scroll 1 (n = 54) | −0,192 | 0,165 ❌ |
| phase | PHerc0139 (n = 38) | +0,150 | 0,368 ❌ |

**Un sur trois tient, et c'est celui qui tient sur trois corpus.**


---

## 10. ⚠⚠ Le soupçon est levé, et l'échec devient définitif

*(2026-08-19)* Le §8 laissait **une** porte ouverte : la campagne tournait au niveau 3
(19,2 µm), où huit cellules d'un maillage à 2,4 µm partagent un voxel de phase, donc
« la plupart des marches valent zéro par construction ». Deux mesures la ferment, et
elles échouent différemment — c'est pour ça qu'il en fallait deux.

### 10.1 Il n'existe pas de niveau plus fin

Le `.zattrs` du volume `cos` déclare ses niveaux, et le bucket les confirme :

```
$ curl … /?list-type=2&prefix=…_cos.ome.zarr/&delimiter=/
.zattrs   .zgroup   3/   4/   5/

$ curl … /_cos.ome.zarr/2/.zarray   →  absent
$ curl … /_cos.ome.zarr/3/.zarray   →  shape [9620, 3314, 3314]  chunks [32,32,32]
```

> **Le niveau 3 n'était pas un choix : c'est la résolution la plus fine qui existe.**
> « Refaire au niveau 0 ou 1 » n'a pas d'objet — ces niveaux ne sont pas publiés.

⚠ C'est une correction de ma propre formulation du §8, qui présentait un niveau imposé
par l'éditeur comme un réglage de notre campagne.

### 10.2 Et la quantification n'écrase rien — mesuré, pas supposé

La suspicion reste testable **par sa conséquence** : si le partage de voxels écrasait le
signal, la distribution des marches serait dominée par le zéro. Sur les 38 traces déjà
calculées (`src/nappe/resolution_phase.py`) :

| grandeur | min | médiane | max |
|---|---:|---:|---:|
| marche médiane | 6,0 | **12,2** | 16,0 |
| marche p95 | 37,0 | 55,5 | 70,0 |
| marche max | 93,0 | 117,0 | 185,0 |

> **35 551 marches, et ZÉRO trace sur 38 dont la marche médiane soit nulle.** Sur une
> échelle de 0 à 255, une médiane à 12,2 dit que le champ **varie** entre cellules
> adjacentes. La quantification n'est pas ce qui a tué le signal.

⚠ 14 valeurs distinctes de marche médiane sur 38 traces : on n'est pas non plus dans un
régime où la mesure ne pourrait prendre que deux ou trois valeurs.

### 10.3 Verdict

**L'échec est définitif, et il est propre.** Le canal `cos` se lit, le lecteur marche,
la résolution disponible suffit, et la marche de phase entre cellules voisines **ne
prédit pas** les croisements recensés (+0,517 à n = 8, +0,306 à n = 30, **+0,150 à
n = 38**). Un effet réel ne fond pas quand on l'échantillonne mieux.

⭐ Ce qui reste acquis : le lecteur de champ `lasagna`, écrit et contrôlé, prêt pour la
prochaine idée qui aura besoin de la phase d'enroulement.

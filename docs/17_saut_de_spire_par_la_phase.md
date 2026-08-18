# Détecter un saut de spire par la phase d'enroulement publiée

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

## 6. ⏳ Ce qu'il faudrait pour trancher le détecteur de phase

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
./tools/campagne_saut_spire.sh docs/saut_spire
cd inference_xpu
uv run python ../analysis/src/table_saut_spire.py ../docs/saut_spire \
    ../repos/windcheck/results/index.json
```

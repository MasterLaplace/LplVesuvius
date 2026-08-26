# Les rouleaux du prix, mesurés là où quelqu'un a déjà tracé

2026-08-19. `16` a mesuré les **13 rouleaux du Grand Prize** sur leur volume brut, sans
trace — c'était tout ce qu'on pouvait faire. Depuis, un inventaire complet montre que la
situation n'est pas uniforme.

---

## 1. L'état des treize, compté proprement

`src/outils/etat_rouleaux_prix.sh`, sorties dans `docs/mesures/etat_rouleaux_prix.txt` :

| rouleau | volumes | surfaces | lasagna | **segments** |
|---|---:|---:|---:|---:|
| PHerc0125, 0191, 0211, 0257, 0268, **0358**, 0813, 0826, 1218, 1545 | 1 | 2 | 1 | **0** |
| PHerc1203 | 2 | 4 | 1 | 1 |
| PHerc0800 | 1 | 2 | 1 | 6 |
| **PHerc1447** | 1 | 2 | 1 | **16** |

> **Dix rouleaux sur treize n'ont été tracés par personne.** Et les treize publient tous
> ce qu'il faut pour commencer : un volume, une prédiction de surface avec ses
> *normal-grids*, et le champ d'enroulement `lasagna`.

⚠ **Deux lectures d'un zéro, et rien ici ne les départage** : soit le prix y est intact,
soit des gens ont essayé et abandonné. Pour `PHerc0358` la première est plus probable —
`16` en fait le **moins difficile** des treize (bonne séparabilité médiane, seulement 4 %
de poches indissociables).

⚠ Piège payé en écrivant le script : une réponse S3 contient le **préfixe interrogé** en
plus de ses sous-préfixes. Compter les lignes sans l'exclure décale la table de **un
partout** — et une table décalée d'un cran ressemble parfaitement à une table juste.

## 2. ⭐ La première mesure de trace sur un rouleau du prix

`PHerc1447` est le **seul** des treize à publier des volumes de surface : 4 segments sur
ses 16, à **8,64 µm**, et **aucune carte d'encre** — personne n'y a encore détecté de
texte. Nos instruments s'y appliquent tels quels.

| segment | matière | au bord | écart | résiduel | part rigide | cohérence |
|---|---:|---:|---:|---:|---:|---:|
| `20250702235910-auto_grown_…292` | 57,5 % | 0,0 % | −17,3 µm | 8,6 | 66,7 % | −0,144 |
| `20250703025628-auto_grown_…283` | 51,0 % | 3,6 % | −13,0 µm | 13,0 | 50,0 % | +0,504 |
| `20250703034159-auto_grown_…599` | 59,0 % | 6,0 % | −8,6 µm | 77,8 | 10,0 % | +0,635 |
| **`20251105093211-z_dbg_gen_00320`** | **9,0 %** | **17,4 %** | **+86,4 µm** | 43,2 | 66,7 % | +0,269 |

> ⭐⭐ **Le quatrième segment est hors du papyrus, et les trois grandeurs le disent
> ensemble** : 9 % de fenêtres avec de la matière quand les autres sont à 51–59 %, 17,4 %
> de pics collés à un bord de la pile, et un écart de **+86 µm** quand les autres sont
> sous 18. Son nom — `z_dbg_gen` — suggère d'ailleurs une génération de mise au point.

**Ça coûte 300 requêtes par segment et se calcule avant toute inférence.** C'est
exactement ce que le tableau des goulots du concours appelle *« detecting failure-cases of
existing methods on real scroll data »*, appliqué pour la première fois à un rouleau du
prix.

⚠ **n = 4.** Le contraste entre 9 % et 51–59 % est net et le mode d'échec est cohérent
sur trois grandeurs indépendantes, mais quatre segments ne font pas une distribution. Ce
qui est solide ici est le **diagnostic d'un segment**, pas une statistique sur le rouleau.

⚠ Et une limite qui vaut d'être dite : les trois bons segments ont des **parts rigides
hautes** (66,7 / 50,0 / 10,0 %), donc contrairement à Scroll 1, 4 et 5, une translation y
enlèverait souvent la moitié de l'erreur. À 8,64 µm et sur quatre segments, c'est une
observation, pas un résultat.

## 3. Reproduire

```bash
./src/outils/etat_rouleaux_prix.sh                      # l'inventaire des treize

cd inference_xpu
uv run python -u ../src/tracecheck/tracecheck.py PHerc1447 --all \
    --voxel-um 8.64 --prefer 8.64um --side 5 --blocks 5
```

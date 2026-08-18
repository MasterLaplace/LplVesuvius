# Reprise de session — état au 2026-08-18

Document de passation. **À lire en entier avant de reprendre.**

---

## 1. ⭐⭐ L'OBJECTIF — et ce n'est pas le texte

> **Le but est le DÉROULEMENT, pas la lecture.** Traduire n'est pas notre métier.
> Repérer quelques lettres sert à **s'assurer que le rouleau assemblé et déroulé fait
> du sens** — l'encre est la **règle graduée**, pas l'ouvrage.
> *(cadrage de l'auteur, 2026-08-17)*

| famille | rôle |
|---|---|
| fusions, onde radiale, dépliage polaire, proximité géométrique, direction des fibres | **le travail** |
| détection d'encre, juge calibré, second rouleau | **l'instrument** |

⚠ Pousser l'AUC plus haut, chercher un meilleur détecteur d'encre ou faire transcrire
davantage **ne sert pas** l'objectif.

## 2. ⚠ CE QUI TOURNE (2026-08-18)

| quoi | sortie | attendu |
|---|---|---|
| inférence Scroll 4, 6038 × 8000 | `data/out/ink_scroll4.npy` | ~40 min |

```bash
ps -eo etime,cmd | grep "[i]nfer_ink"
cat docs/scroll4_infer.log | grep -vE "SyntaxWarning|if amt"
```

⚠ **Juger sur un fichier de résultat, jamais sur une notification** : celles-ci
concernent le *wrapper*, pas le travail `nohup`, et un log vide veut dire « Python
bufferise ».

## 3. Le projet

`~/LplVesuvius` — Vesuvius Challenge vu depuis Laplace. Contexte non versionné dans
`PRIVE.md` (gitignoré). **Budget disque** : 100 Go, ~52 Go utilisés.

⚠ Aucun remote git configuré. Ne jamais pousser.

### Ordre de lecture

| doc | contenu |
|---|---|
| `00` | point d'entrée : la chaîne, les acteurs, les prix |
| `01`–`05` | le goulot, l'inventaire, la reproduction `windcheck`, l'excision |
| **`06`** | **le carnet de mesures** — faites, en attente, écartées |
| `07` | la réparation ne déplace pas le défaut |
| `08`, `10` | ⭐ la passe d'encre : **AUC 0,925** sur un segment entier |
| `09` | juge par modèle : 3 juges mécaniques en échec, 1 calibré qui marche |
| **`11`** | ⭐ **onde radiale, dépliage polaire, fusions localisées en 3D** |

## 4. L'outillage, et comment le relancer

```bash
./tools/temoins.sh                      # 16 contrôles hors ligne, tous verts
./tools/mirror_site.sh                  # miroir + contrôle de couverture
./tools/fetch_layers.sh <url> <dest> <largeur> <de> <a>   # couches, reprenable
./tools/ppm_to_tifxyz.py <in.ppm> <out.tifxyz>            # .ppm de VC -> tifxyz
./tools/survey_fusions.sh <out> <bandes> <par> <pas>      # fusions, niveau 2

cd experiments   # geometrie
uv run python src/excision/radial.py {centre|compter|profil|deplier|axe} …
uv run python src/excision/fusions.py {controle|ecarts-controle|densite|ecarts} …
uv run python src/excision/fusion_scan.py …               # persistance en z
uv run python src/excision/pyramid.py <volume>            # separabilite par niveau
uv run python src/excision/shape.py {degradation|ellipticite} <volume>
uv run python -m excision.proximity <mesh.tifxyz> --json

cd inference_xpu # encre
uv run python src/infer_ink.py <layers> --model … --device xpu --out out.npy
uv run python ../analysis/src/{evaluate_segment,render_segment,structure}.py …
uv run python ../analysis/src/judge_api.py --list-models
uv run python ../analysis/src/proximity_vs_ink.py <mesh> <pred> <labels>
```

### Matériel

| voie | verdict |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ ×4,5, sortie identique au CPU à 4,9e-6 |
| NPU | ❌ non exposé à WSL2 |
| OpenVINO | ❌ ne convertit pas ce modèle |

⚠ `sudo apt install intel-opencl-icd libze-intel-gpu1 libze1`. Le nom
`intel-level-zero-gpu` **n'existe pas** sous Ubuntu 26.04 et apt annule **toute** la
transaction sur un nom inconnu.

## 5. Les résultats acquis

### Géométrie — le travail

1. **Onde radiale** : **176 spires** (max sur 20 tranches), rayon 25,1 mm →
   **~13,9 m** de papyrus. ⚠ Borne **inférieure** : deux feuilles fondues comptent
   pour une. Longueur **axiale** du rouleau : 164 mm ; diamètre 48 mm.
2. **Invariant fort** : rayon / feuilles = **142,8 µm, cv 1,8 %** sur toute la hauteur,
   alors que chaque grandeur varie de 4-5 %. Profil en **U** (25,1 → 21,3 → 24,3 mm).
3. **Le rouleau est écrasé** : rapport d'axes **1,26 à 1,57**, le plus au milieu.
   ⚠ Le périmètre perd quand même 9 % — écrasement **et** perte, aucune écartée.
4. **Fusions localisées en 3D** : 4 candidats vers 17 mm, persistants à **p = 0,0001**
   (coupes à 0,8 mm), et **18 %** de colocation sur le rouleau entier par bandes.
   Le défaut **migre** : +2,4 mm de rayon et +38° sur 2,4 mm de hauteur.
   ⚠ L'inclinaison de l'axe est **écartée** — elle joue en sens opposé (−0,47 mm).
5. **Le niveau 2 de la pyramide suffit** : **89 %** des murs pour **33 Gio au lieu de
   2100**. Falaise entre les niveaux 2 et 3. ⚠ C'est un **crible** : les deux niveaux
   ne trouvent pas les mêmes sites (fond 10,3 % contre 6,6 %), donc tout candidat se
   confirme au niveau 0.
6. **Théorie du dommage de l'auteur** : à moitié. Cœur dégradé (−20 %), extérieur à
   peine (−5 à 8 %). **Pas un U.** ⚠ Bonne nouvelle : ce qu'on a perdu du **début**
   des textes est moindre que craint.

### Encre — l'instrument

7. **AUC 0,925** sur 44,7 M de pixels d'un segment entier, contrôle mélangé à **0,500**.
   9,2 cm de grec lisible. ⚠ Orientation de lecture = **rotation 270°**.
8. **Juge de langue calibré** : **15/16, zéro fabrication**, lisibilité séparant sans
   chevauchement le vierge (0–1) du texte (3–6). Protocole : `data/juge/PROTOCOLE.md`.

### La jonction — et c'est un NON

9. ⚠⚠ **La proximité géométrique ne prédit PAS la lisibilité.** rho **+0,019** à
   n = 89 tuiles (contrôle plat), et à ce n la mesure détecterait un rho de 0,3.
   La métrique de `07` corrèle avec les croisements publiés (+0,77) mais pas avec le
   résultat : **elle mesure un défaut de la TRACE, pas du RÉSULTAT**. Elle reste un
   contrôle qualité de trace bon marché ; elle n'est pas un argument sur le rendu.
   ⚠ Une seule trace — la seule qui ait maillage **et** encre.

## 6. ⚠ Le cap n'est PAS franchi

> **On ne publie rien sans une passe complète — rouleau déroulé, texte extrait, soumis
> à un expert qui dise si ça fait sens — et sur plusieurs rouleaux.**

Trois juges mécaniques ont échoué : Kraken (aucun modèle entraîné sur papyri), score
structurel sur région, score structurel sur segment entier. ⚠ La dernière cause est
définitive : **ce type de segment ne porte que 4 à 5 lignes de texte**, et les glyphes
**fusionnent** au seuil du modèle. Le juge calibré de `09` est le seul disponible.

## 7. ⏳ CE QUI RESTE, avec son blocage

| # | quoi | blocage |
|---|---|---|
| **E** (suite) | juger l'inférence Scroll 4 avec le juge calibré | attend le run en cours. ⚠ **Scroll 4 n'a pas de vérité terrain** → pas d'AUC, c'est le juge qui répond. ⚠ Scroll 5 écarté : couches **JPG 8 bits** quand le modèle veut du 16 bits |
| **C5** ⭐ | direction des fibres comme séparateur | problème ouvert nº 5, discriminant **physique** donc déroulement pur. Prédictions nnUNet disponibles. Coût élevé, **valeur la plus haute** |
| `06` §3.2 | fenêtre de `proximity.py` | mesuré : elle couvre **96,9 % d'un tour** (309 colonnes) et le rayon y varie de 59,5 % de l'étendue. À descendre bien sous 309, ou normaliser par le rayon, puis re-mesurer les 46 traces |
| C4 / §3.6 | les 4 sites à **2,4 µm** (ESRF) | distinguerait une soudure d'un défaut de résolution. On a **4 endroits précis** |
| §2.3 | vrai ombilic | `umbilicus.txt` sur Scroll 1 |
| — | appariement **prédictif** entre coupes | départagerait « défauts de 1 mm » de « défauts qui migrent » (`11` §10) |
| D (suite) | élargir à d'autres traces | ⚠ **plus bloqué** : `tools/ppm_to_tifxyz.py` convertit n'importe quel `.ppm` publié. C'est une commande, plus une décision |

## 8. ⚠ Les pièges payés, à ne pas repayer

**Mesure**
1. **Un seuil calé sur le niveau 0 ne se transporte pas** à une résolution réduite —
   réduire *moyenne* les voxels et remonte le fond. (« 53 feuilles au niveau 1 ».)
2. **Une valeur identique partout** = saturation contre sa propre borne. (Axe long à
   22,7 mm sur les 8 coupes.)
3. **Comparer une grandeur à elle-même.** (Mon « périmètre » valait 2π × rayon moyen.)
4. **Échantillonner à l'échelle de l'objet** et non de la structure cherchée : coupes
   à 22 mm pour un défaut millimétrique → verdict inversé.
5. **Décimer mange la queue** : −60 % du signal, parce qu'il *est* dans la queue.
6. **Un chiffre emprunté n'est pas une mesure** (« 300 µm entre spires »).

**Outillage**
7. ⚠⚠ **Un outil validé sur 300 K cellules ne tient pas sur 21 M** : un `cKDTree`
   global y prend des gigaoctets et **a fait tomber la machine trois fois**. Découper
   en **blocs 3D** (validé à 0,0 % d'écart), jamais en tuiles de paramétrisation —
   la métrique cherche justement les points loin en paramétrisation et proches en 3D.
8. **`pkill -f` / `pgrep -f` matchent leur propre ligne de commande** (payé 4×).
9. **Le code de sortie d'un pipeline est celui de sa DERNIÈRE commande** (payé 3×).
10. **Chemin relatif après un `cd`** : `mkdir` à un endroit, écriture à un autre →
    10 bandes calculées puis perdues.
11. **Éditer un script pendant qu'il tourne** le casse (bash lit par offset).
12. **Une boucle d'attente sans borne** survit à la disparition de ce qu'elle attend
    (payé : 3 h 19).
13. **`aws s3 cp --include` énumère TOUT le préfixe.**
14. **Vérifier l'alignement avant toute comparaison d'images** (remplissage à 512).

## 9. Règles de mesure tenues ici

1. **Aucun seuil absolu** sur une grandeur physique — normaliser, ou être **ordinal**.
2. **Vérifier le confond avant de conclure.**
3. **Un contrôle qui ne peut pas échouer ne prouve rien** : témoin apparié + cas négatif.
4. **Mesurer d'abord, expliquer ensuite.** La lecture du code a produit une hypothèse
   fausse à chaque fois qu'elle a précédé l'instrument.
5. ⚠⚠ **Un chiffre publié dont le calcul n'est pas dans l'arbre n'est pas un résultat,
   c'est une anecdote.** Payé : l'onde radiale a dû être récupérée du transcript.
6. **Une idée testée et écartée est un actif** — à condition que la *raison* soit
   écrite. Quatre formulations des fusions, trois échecs, et c'est le troisième qui a
   désigné la bonne méthode.
7. **Rapporter la puissance avec un zéro** : « pas de corrélation » ne veut rien dire
   sans le rho que la taille d'échantillon permettait de détecter.

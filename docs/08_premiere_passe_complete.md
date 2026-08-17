# Première passe complète : des couches au texte lisible

2026-08-17. Premier bout-en-bout du pipeline, avec vérité terrain publiée.
Rejouable : `inference_xpu/src/infer_ink.py`.

---

## 1. Ce qui a débloqué la chaîne

L'étage « rendu » n'a jamais été manquant : **il est déjà publié**. `download.sh` du
dépôt Grand Prize révèle que les **couches rendues** sont sur `dl.ash2txt.org`, et
l'accès y est désormais **libre** (les identifiants du script datent d'une époque où
l'inscription était requise). Donc ni `vc_render_tifxyz` à construire, ni volume de
2,1 Tio à streamer.

⚠ **Mesure qui a évité 16 Go de gâchis** : une couche pèse 474 Mo, donc 65 couches
feraient 31 Go. Les modèles n'en lisent que **26** (`start_idx=15`, `in_chans=26`).

## 2. Le matériel

| voie | verdict |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ **×4,5** (104 → 23 ms/fenêtre) |
| CPU seul, réglé | 104 ms/fenêtre (16 fils, lot 4) |
| NPU | ❌ non exposé à WSL2 (`/dev/accel` absent) |
| OpenVINO | ❌ ne convertit pas ce modèle (einsum des *rotary embeddings*) |

⚠ **Le GPU n'a été retenu qu'après vérification numérique** : sortie identique au
CPU à **4,9e-6** près (bruit fp32). Un résultat rapide et faux ne vaut rien.

⚠ Ce qui a débloqué le GPU sous WSL2 : `intel-opencl-icd libze-intel-gpu1 libze1`.
Le nom `intel-level-zero-gpu` n'existe pas sous Ubuntu 26.04, et **apt annule toute
la transaction** sur un nom inconnu. Le GPU fonctionne **sans `/dev/dri`**, par
`/dev/dxg`.

**Coût final** : 4 cm² en **5,6 min**, segment entier en **3,4 h**.

## 3. Le pas de balayage : mesuré, puis rendu caduc

Question posée : passer de 21 à 32 divise le travail par 2,3 — à quel prix ?

| | valeur |
|---|---|
| corrélation des deux cartes | 0,941 |
| désaccord au seuil médian | **17,9 %** |
| désaccord sur l'encre franche (p90) | 3,0 % |

**Pas gratuit** : les détections fortes s'accordent, les zones marginales divergent
— et c'est là que se joue une lettre à demi effacée. Le GPU rendant le pas 21
abordable, on garde **21**.

## 4. Résultat, sur un segment JAMAIS VU par le modèle

`20230909121925` — étiqueté, **absent du jeu d'entraînement** (vérifié contre
`download.sh`).

⚠ **Contrôle d'alignement fait avant toute comparaison** : étiquettes en 11776×4096,
couches en 11591×3882. Un décalage aurait produit un chiffre parfaitement faux. Ce
sont des multiples de 512 dont le remplissage est **entièrement vide** — donc
alignement en (0,0), vérifié et non supposé.

| région | pixels | AUC | précision @0,5 | rappel |
|---|---|---|---|---|
| 1024² | 1,0 M | 0,893 | 0,712 | 0,751 |
| **2560×3072** | **7,8 M** | **0,919** | 0,553 | 0,777 |

À comparer au segment d'entraînement `20231022170901` : AUC **0,874**. **Le modèle
fait aussi bien sur du papyrus inconnu** — ce qui ne prouve pas une généralisation
remarquable, mais prouve qu'on ne mesurait pas du sur-apprentissage.

## 5. ⚠⚠ L'étiquetage est PARTIEL, donc la précision est une borne inférieure

Constaté en **regardant les images** : la prédiction montre nettement plus de
lettres que la vérité terrain, et ces lettres ont des formes cohérentes, une
épaisseur de trait régulière et un alignement en colonnes — ce n'est pas du bruit.

Mesuré : **50 % des lignes du segment ne portent aucune étiquette**, et des bandes
entières sont vides.

| évaluation | précision |
|---|---|
| toute la région | 0,553 |
| lignes annotées seulement | 0,585 |
| lignes densément annotées | 0,587 |

L'étiquetage partiel explique donc **une partie** des faux positifs apparents, pas
la majorité. **L'AUC reste 0,919 dans tous les découpages** — c'est le chiffre
robuste ; la précision, elle, est un plancher.

⚠ Et la restriction par lignes est grossière : les images montrent que la zone non
annotée est surtout faite de **colonnes**, pas de lignes. Une évaluation propre
demanderait le masque d'annotation, que ce jeu ne fournit pas.

## 6. Ce que ça établit, et ce que ça n'établit pas

**Établi** : la chaîne complète fonctionne — trace → couches publiées → modèle →
carte d'encre → **lettres grecques visibles à l'œil**, sur du papyrus que le modèle
n'a jamais vu, en **52 secondes par cm²**.

**Non établi** : que ce soit *lisible* au sens d'un papyrologue. Des lettres
reconnaissables ne font pas un texte suivi, et personne de compétent ne l'a encore
regardé. C'est exactement la barre fixée en `06` §1bis, et elle n'est pas franchie.

⚠ **Ne pas confondre** : *le modèle retrouve les traits encrés* (mesuré, AUC 0,92)
et *le texte est lisible* (non mesuré, demande un expert). Les deux se ressemblent
assez pour qu'on prenne le premier pour le second.

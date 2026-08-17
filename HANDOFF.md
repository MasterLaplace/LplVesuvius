# Reprise de session — état au 2026-08-17

Document de passation. **À lire en entier avant de reprendre**, puis suivre
`docs/06_mesures_a_faire.md` §3bis pour la priorisation.

---

## 1. ⚠ CE QUI TOURNE ENCORE

| PID | quoi | attendu | sortie |
|---|---|---|---|
| `537466` | inférence d'encre sur le **segment entier** `20230909121925` | ~40 min (lancé à 31 min au moment d'écrire) | `data/out/ink_segment_complet.npy` |

```bash
# verifier
kill -0 537466 2>/dev/null && echo actif || echo fini
grep -vE "SyntaxWarning|if amt" docs/segment_complet.log | tail -6
```

**Pourquoi il tourne** : c'est la priorité A — aucune mesure de cohérence (ni HTR ni
structurelle) ne fonctionne sur 20 × 24 mm, il faut assez de lignes. Voir §6.

⚠ **Piège payé quatre fois dans ce projet** : `pkill -f` / `pgrep -f` **matchent
leur propre ligne de commande**. Trois boucles d'attente ont ainsi tourné 15 heures.
**Toujours tuer et attendre par PID.**

## 2. Ce que le projet est

`~/LplVesuvius` — Vesuvius Challenge vu depuis Laplace. Le déroulage produit du grec
ancien **avec une provenance**, donc `harvest::Tei` et `corpus::Locus` savent déjà
l'ingérer : le raccordement en aval est un lecteur de plus, pas une architecture.

⚠ Objectif non public, à ne pas écrire dans les documents versionnés : **gagner un
prix pour financer du matériel de recherche**. Il change la priorisation — une piste
se juge aussi sur le fait qu'elle soit **soumissionnable**.

**Budget disque** : 100 Go autorisés, **38 Go utilisés**.

## 3. L'ordre de lecture des documents

| doc | contenu |
|---|---|
| `00_etat_de_lart.md` | **point d'entrée** : la chaîne, les acteurs, les prix |
| `01` | le goulot, et pourquoi la première piste a été abandonnée |
| `02` | inventaire mesuré (tailles, pyramide, 45 échantillons) |
| `03` | reproduction de `windcheck`, 53/53 |
| `04` | expérience d'excision : **H₀ non rejetée** |
| `05` | le prédicat vérifié est plus étroit que le défaut |
| **`06`** | **le carnet de mesures** — faites, en attente, écartées, et la suite priorisée |
| `07` | la réparation ne déplace pas le défaut (46 traces) |
| `08` | ⭐ **la passe complète** : AUC 0,919 hors entraînement, lettres grecques |
| `09` | protocole de jugement par modèle, et deux juges mécaniques en échec |

## 4. L'outillage monté, et comment le relancer

```bash
# donnees & depots
./tools/mirror_site.sh          # miroir + controle (sort non nul si incomplet)
./tools/clone_repos.sh          # 33 depots
./tools/s3_size.py PHerc0332/   # tailles S3 sans telecharger

# etat de l art reproduit
cd repos/windcheck && uv sync && uv pip install awscli
clang++ -O3 -std=c++17 -pthread -o engines/selfcross engines/selfcross.cpp

# nos mesures geometriques
cd experiments && uv sync
uv run python -m excision.proximity <mesh.tifxyz> --json
uv run python -m excision.correlate docs/proximity_scroll1.jsonl repos/windcheck/results/index.json
uv run python -m excision.winding <mesh.tifxyz>     # ⚠ trop lent, voir §7

# inference d encre — GPU Arc
cd inference_xpu
uv run python src/infer_ink.py <layers_dir> --model data/models/timesformer_GP_scroll1 \
    --top T --left L --height H --width W --stride 21 --batch-size 64 --device xpu --out out.npy
```

### Matériel — ce qui a été tranché

| voie | verdict |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ **×4,5**, sortie identique au CPU à 4,9e-6 |
| CPU réglé | 104 ms/fenêtre (16 fils, lot 4) ; ⚠ 22 fils s'effondre à 734 ms |
| NPU | ❌ non exposé à WSL2 (`/dev/accel` absent) |
| OpenVINO | ❌ ne convertit pas ce modèle (einsum des rotary embeddings) |

⚠ Le GPU a demandé `sudo apt install intel-opencl-icd libze-intel-gpu1 libze1`.
Le nom `intel-level-zero-gpu` **n'existe pas** sous Ubuntu 26.04 et apt **annule
toute la transaction** sur un nom inconnu. Fonctionne **sans `/dev/dri`**, par
`/dev/dxg`. **L'auteur est disponible pour les commandes sudo.**

Coût : 4 cm² en **5,6 min**, un segment de 45 Mpx en **~40 min**.

## 5. Les résultats acquis

1. **La chaîne complète marche** : trace → couches publiées → modèle → lettres
   grecques visibles, **AUC 0,919** sur un segment jamais vu, 52 s/cm² (`08`).
   ⚠ L'étiquetage de vérité terrain est **partiel** (50 % des lignes vides), donc la
   précision mesurée est un **plancher**, pas une performance.
2. **Le rendu n'a jamais été manquant** : les couches sont **déjà publiées** sur
   `dl.ash2txt.org`, en accès libre. Ni renderer à construire, ni volume à streamer.
3. **`windcheck` reproduit à l'identique** sur deux corpus entiers : 53/53 (Scroll 5)
   et 55/55 (Scroll 1), triangles **et** contacts.
4. **La réparation d'auto-intersection ne déplace pas le défaut** : recensement
   11 673 → 0, métrique de proximité 0,37 → 0,38 % (`07`).
   ⚠ Mais elle **corrèle** (rho 0,77, tenant dans les trois terciles de longueur)
   sans **classer** : les 7 traces saines s'étalent sur un facteur 18.
5. **Onde radiale** (idée de l'auteur) : **158 feuilles**, espacement 136–158 µm,
   **11,2 m de papyrus** estimés — mesuré dans le volume, sans aucun traçage.
6. **Le seuil de la métrique n'est pas sur-ajusté** : plateau de rho 0,759 à 0,779
   pour des seuils de 0,15 à 0,40 ; effondrement au-delà de 0,5.

## 6. ⚠ Le cap, et il n'est PAS franchi

> **On ne publie rien sans une passe complète du pipeline — rouleau déroulé, texte
> extrait, soumis à un expert qui dise si ça fait sens — et ce sur plusieurs
> rouleaux.** (décision de l'auteur)

On a des **lettres**, pas un **texte jugé**. Et deux tentatives de juge mécanique
ont échoué avec leurs raisons (`09` §6) :

- **Kraken** : aucun de ses 65 modèles n'est entraîné sur des papyri ; le seul modèle
  grec est pour du **texte imprimé**. Sortie : 6 caractères de bruit.
- **Score structurel** : ne discrimine pas, parce que la région ne contient que 4-5
  lignes et que la **grille de ré-agrandissement ×16** pollue les courts décalages.

**Les deux échouent pour la même raison de fond : la région est trop petite.** D'où
la priorité A.

⚠ Et un modèle de langue **embellit** : soumis à une image, Gemini a affirmé une
« régularité d'interligne exacte » là où la mesure donne 590 et 1251 px (facteur
2,1) et une autocorrélation à 0,159. Ne jamais lui accepter une affirmation
**quantitative** sur l'image — ces grandeurs se mesurent.

## 7. La suite, dans l'ordre

### A. Une colonne entière de texte 🔄 EN COURS (PID 537466)
Seul livrable qui permette de demander un avis à un expert.

### B. Le contrôle en aveugle des modèles de langue
Images prêtes : `data/juge/A_positif.png` (texte réel) et `B_negatif.png` (papyrus
**sans encre**, même pipeline). Prompt dans `09` §3.
⚠ **À faire AVANT** de montrer quoi que ce soit d'inconnu — après, on ne peut plus
calibrer sans biais.

### C. Le vivier d'idées sur l'onde radiale
La localisation des fusions par **comptage** a échoué (475 sites, tous près du
centre = bruit du détecteur). Cinq pistes, par coût croissant :

1. **Suivre les feuilles comme des courbes** en (angle, rayon) plutôt que recompter
   des crêtes — une fusion est deux arcs qui se rejoignent ;
2. ⭐ **Déplier en coordonnées polaires** : les spires deviennent des lignes quasi
   horizontales, et tout le problème passe en traitement d'image ordinaire. Rend (1)
   presque trivial ;
3. **Cohérence du compte le long de z** — une rupture brutale localise un dégât en
   3D. Test à une dimension, très bon marché ;
4. **Revoir les sites suspects à 2,4 µm** (ESRF) : distingue une vraie fusion d'un
   défaut de résolution ;
5. **Le sens des fibres comme séparateur** — problème ouvert nº5, discriminant
   *physique*. Coût élevé, valeur la plus haute.

### D. Boucler `07` sur `08`
*Une trace à forte proximité anormale donne-t-elle une encre moins lisible ?*
On a la métrique sur 46 traces et l'AUC de l'autre côté. ⚠ Demande de télécharger
les couches de plusieurs traces (~2 à 15 Go chacune). Si la corrélation existe, la
métrique devient un **prédicteur de lisibilité** — exactement ce qu'un Progress
Prize récompense.

### E. Un second rouleau
Tous les chiffres de `07` et `08` viennent de Scroll 1.

## 8. ⚠ Les pièges de ce dépôt, payés au moins une fois

1. **`pkill -f` / `pgrep -f` matchent leur propre ligne de commande** — 4 fois.
   Tuer et attendre **par PID**.
2. **Le code de sortie d'un pipeline est celui de sa DERNIÈRE commande** — 3 fois.
   `cmd | grep x; echo $?` lit le `$?` de `grep`.
3. **Un log périmé lu comme un résultat** — vérifier l'horodatage avant de citer.
4. **`xmake`/`uv` lancés depuis le mauvais dossier** répondent « ok » sans rien faire.
   `cd` dans le projet **dans la même commande**.
5. **Vérifier l'alignement avant toute comparaison d'images** : étiquettes et couches
   diffèrent en taille (remplissage à des multiples de 512). Un décalage produit un
   chiffre parfaitement faux.
6. **Un chiffre emprunté n'est pas une mesure** : le « 300 µm entre spires » venait
   du README d'un autre rouleau et a produit une conclusion fausse.
7. **`aws s3 cp --include` énumère TOUT le préfixe** : 11 M de clés et 20 To lus pour
   extraire 400 Mo. Préférer les couches déjà publiées.

## 9. Règles de mesure tenues ici

1. **Aucun seuil absolu** — l'espacement varie d'un facteur 3 selon l'endroit.
2. **Vérifier le confond avant de conclure** (« les automatiques sont 9× pires »
   était un effet de longueur).
3. **Un contrôle qui ne peut pas échouer ne prouve rien** — toute comparaison porte
   un témoin apparié et un cas négatif.
4. **Mesurer d'abord, expliquer ensuite** — la lecture du code a produit une
   hypothèse fausse à chaque fois qu'elle a précédé l'instrument.
5. **Consigner les échecs avec leur diagnostic**, pas seulement les succès : ils
   disent ce qu'il faudrait pour réussir.

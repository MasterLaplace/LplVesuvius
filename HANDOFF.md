# Reprise de session — état au 2026-08-17

Document de passation. **À lire en entier avant de reprendre**, puis suivre
`docs/06_mesures_a_faire.md` §3bis pour la priorisation.

---

## 1. ⚠ CE QUI TOURNE (au 2026-08-17, 20 h)

| quoi | sortie | attendu |
|---|---|---|
| `radial.py profil` — 20 tranches + 6 raffinées | `docs/profil_z_0172.json` | ~3 h (6/20 faites) |
| `fusion_scan.py` — 5 coupes | `docs/fusions_z_0172.json` | ~50 min |

```bash
# juger par ARTEFACT, pas par notification
python3 -c "import json;d=json.load(open('docs/profil_z_0172.json'));print(len(d['uniform']),'/20')"
cat docs/fusions_z.log
```

⚠⚠ **Piège payé trois fois aujourd'hui** : les notifications « tâche terminée »
concernent le **wrapper**, pas le travail `nohup`. Et un log vide ne veut pas dire
« rien ne se passe » — Python bufferise sa sortie quand elle est redirigée. **Juger
sur un fichier de résultat, jamais sur une notification ni sur un log vide.**

La passe sur le segment entier est **terminée** : 99 918 fenêtres, 38,5 min.
Résultats dans `docs/10_segment_complet.md`.

⚠ **Le PID de la table précédente (`537466`) était le WRAPPER bash**, pas le
processus Python (`537472`). Et son log restait vide non parce que rien ne se
passait, mais parce que **Python bufferise sa sortie quand elle est redirigée**. Deux
raisons distinctes de croire un run mort alors qu'il tourne.

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

**Budget disque** : 100 Go autorisés, **38 Go utilisés**, pas une limite fixe mais juste pour éviter de télécharger n'importe quoi et de demander si c'est vraiment nécessaire avant au point de devoir dépasser le budget.

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
| `09` | protocole de jugement par modèle, et **trois** juges mécaniques en échec |
| **`10`** | ⭐ **le segment entier** : AUC 0,925 sur 44,7 Mpx, 9,2 cm de grec lisible |
| **`11`** | ⭐ **onde radiale, dépliage polaire, 4 candidats de fusion** — et 3 échecs conservés |

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

1. **La chaîne complète marche, sur un segment ENTIER** : **AUC 0,925** sur
   44,7 M de pixels, contrôle mélangé à **0,500** exactement, 4 à 5 lignes de grec
   lisible sur 91,7 × 30,7 mm (`10`). 38,5 min sur l'iGPU Arc.
   ⚠ La précision (0,355 à 0,681 selon le domaine) reste un **plancher**, et `10`
   §2bis corrige `08` : la hausse obtenue en restreignant aux zones annotées est
   **largement un effet de taux de base**, pas une preuve de trous d'annotation.
1bis. **Le modèle ne fabrique pas d'encre sur du vierge** — mesuré : la densité
   prédite suit la densité étiquetée à **rho = +0,796** sur 23 bandes, et les bandes
   vierges restent à 0,35–1,66 % contre 12,9 % dans le texte.
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

On a des **lettres**, pas un **texte jugé**. Et **trois** tentatives de juge
mécanique ont échoué, chacune avec sa raison (`09` §6 et §8) :

- **Kraken** : aucun de ses 65 modèles n'est entraîné sur des papyri ; le seul modèle
  grec est pour du **texte imprimé**. Sortie : 6 caractères de bruit.
- **Score structurel** : ne discrimine pas, parce que la région ne contient que 4-5
  lignes et que la **grille de ré-agrandissement ×16** pollue les courts décalages.

- **Score structurel, sur le segment ENTIER** : échoue encore, et le diagnostic
  précédent était **faux**. Le segment entier n'a pas plus de lignes — il n'en porte
  que **4 à 5**, parce que c'est une bande coupée *en travers* du texte : l'allonger
  allonge les lignes sans en ajouter. S'ajoute un second obstacle indépendant : au
  seuil de décision du modèle, les lettres voisines **fusionnent** en composantes
  connexes géantes (41 composantes dans une région qui en montre des centaines).

**Ce qu'un juge mécanique demanderait réellement** : plusieurs dizaines de lignes —
donc un segment couvrant *plusieurs colonnes* — **et** des glyphes séparables. Aucun
segment de ce type ne les fournit. Le protocole de `09` §1–5 est donc le seul juge
disponible, et le cap reste humain.

⚠ Et un modèle de langue **embellit** : soumis à une image, Gemini a affirmé une
« régularité d'interligne exacte » là où la mesure donne 590 et 1251 px (facteur
2,1) et une autocorrélation à 0,159. Ne jamais lui accepter une affirmation
**quantitative** sur l'image — ces grandeurs se mesurent.

## 7. La suite, dans l'ordre

### A. ✅ FAITE — une colonne entière de texte (`10`)

### B. ✅ FAITE — le juge est calibré, et il a tranché (`09` §9 et §10)
`analysis/src/judge_api.py`, `gemini-3.5-flash`, 10 appels, ~34 000 jetons.
**15 panneaux sur 16, ZÉRO fabrication**, et la lisibilité déclarée sépare sans
chevauchement le vierge (0–1) du texte (3–6). Le témoin voyage **dans** l'image, donc
il ne peut plus être sauté — c'est ce qui a corrigé l'échec du protocole manuel.

⚠ **Modèles éliminés par mesure** : `gemini-2.5-*` → 404 (retirés aux nouveaux
comptes), `gemini-3.1-pro-preview` et `gemini-pro-latest` → 429 (hors offre gratuite),
`gemini-3.7-flash` → 503. Utiliser `--list-models`, jamais un nom codé en dur.

⚠ **La clé de l'auteur est passée en clair dans une conversation** ; elle est
révocable sur `aistudio.google.com/apikey` si besoin. Elle n'est écrite dans aucun
fichier du dépôt.

### C. 🔄 EN COURS — l'onde radiale (voir `11`, bien plus détaillé)

**Acquis** : le code perdu est récupéré et vérifié ; le dépliage polaire marche ;
**4 candidats de fusion** groupés vers 17 mm sur un secteur de 50°, avec la coupe du
cœur validée par mesure (les sites internes suivaient la coupe = artefacts).

**En cours** : tiennent-ils le long de *z* ? Un dégât physique occupe une hauteur.

**Reste du vivier** : (4) revoir les 4 sites à 2,4 µm ESRF — c'est maintenant une
liste de quatre endroits au lieu d'un rouleau ; (5) le sens des fibres comme
séparateur, problème ouvert nº5, coût élevé et valeur la plus haute.

<details><summary>vivier d'origine, conservé</summary>
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

</details>

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
6. ⚠⚠ **Un chiffre publié dont le calcul n'est pas dans l'arbre n'est pas un
   résultat, c'est une anecdote.** Payé le 2026-08-17 : l'onde radiale (158 feuilles,
   11,2 m) avait été lancée en `python -c` et a dû être récupérée du transcript de
   session. Aucune mesure qui entre dans un document ne reste en ligne de commande.
7. **Une idée testée et écartée est un actif, pas un déchet** — à condition que la
   *raison* soit écrite. Quatre formulations des fusions, trois échecs, et c'est le
   troisième échec qui a désigné la méthode qui marche.
8. **Un chiffre emprunté n'est pas une mesure** : le « 300 µm entre spires » venait
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

---

## 10. ⚠ Hygiène des processus de fond — leçon payée le 2026-08-17

Un `until … do sleep; done` lancé en fond a tourné **3 h 19** sur une condition qui ne
pouvait plus arriver : le marqueur qu'il attendait avait été supprimé, et le script qui
devait l'écrire tué. Inoffensif mais invisible, et il serait resté indéfiniment.

**Règles qui en découlent** :

1. Une boucle d'attente doit avoir une **borne** (`for i in $(seq 1 N)`), pas seulement
   une condition — une condition seule ne survit pas à la disparition de ce qu'elle
   attend.
2. Auditer périodiquement :
   ```bash
   ps -eo pid,etime,cmd | grep -E "radial|fusion|infer_ink|uv run" | grep -v grep
   ls -la /tmp/*.pid          # les .pid périmés sont le symptôme visible
   ```
3. Nettoyer les `.pid` d'une session terminée : ils font croire à un processus vivant.
4. ⚠ Rappel : les notifications « tâche terminée » concernent le **wrapper**, pas le
   travail `nohup`. Juger sur un fichier de résultat.

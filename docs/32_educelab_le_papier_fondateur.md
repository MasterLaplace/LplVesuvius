# EduceLab-Scrolls — le papier qui a posé le vocabulaire, et les contrôles qu'il n'a pas faits

2026-08-19, tard. C'est la mesure **M3** de `29`, et le quatrième article primaire :
Parsons, Parker, Chapman, Hayashida, **Seales** — arXiv **2304.02084**, v3 du 30 octobre
2023. ⚠ Une **v4** existe (20 mai 2024) ; c'est la v3 qui a été lue.

C'est le papier fondateur du jeu de données que tout le domaine utilise. Il n'avait jamais
été lu ici, et il était noté « à lire » depuis le 17 août.

---

## 1. Ce qu'il contient — et une correction de vocabulaire

| | |
|---|---|
| entraînement labellisé | **16 scans de 6 fragments issus de 4 rouleaux** |
| rouleaux intacts | **9 scans couvrant 4 rouleaux** |
| **total disque** | **11,5 To** |
| ⭐ **pour reproduire le papier** | **55,8 Go** — les seuls *surface volumes* |
| licence | **CC BY-NC 4.0** |

⚠ **Correction de vocabulaire, vérifiée** : le mot **`volpkg` n'apparaît nulle part** dans
ce papier, et « segment » au sens du concours (un dossier avec `.obj`, `.tif`,
`_mask.png`) non plus. Ce sont des conventions de **Volume Cartographer**, pas de cet
article. Ce qu'il introduit vraiment est plus bas.

⭐ **Le scan qui nous concerne** : `P.Herc.Paris. 4` — Scroll 1 — a été scanné à Diamond
Light Source, ligne I12, en 2019, à **7,91 µm**, en deux moitiés (contrainte mécanique :
le rouleau dépassait la course du portique, d'où un **cric de laboratoire manuel**). Les
fragments labellisés sont à **3,24 µm**.

⚠ Et un défaut déclaré qu'il faut connaître : *« Due to a miscalculation in the projected
position of the axis of rotation, a cylinder of diameter ≈4.8 mm at the core of
P.Herc.Paris. 4 is not represented in the projection images. »* **Le cœur de Scroll 1 a un
trou de 4,8 mm**, et il est toujours là.

## 2. ⭐⭐ Ce que « verifiable » veut dire — et c'est une propriété du CORPUS

C'est le point de conception, et il vaut d'être compris avant tout le reste :

> **La vérifiabilité n'est pas une propriété de la méthode. C'est une propriété du jeu de
> données.** Le corpus a été construit autour d'objets qui portent **leur propre réponse**
> — des fragments détachés dont la surface est photographiée en infrarouge, dans une
> **autre modalité**, par un **autre laboratoire** (BYU), **vingt ans plus tôt**.

*« Via **fragments with verifiable ground truth**, open data release, and open source code,
we aim to achieve this »*.

⭐⭐ **C'est exactement la forme qu'un instrument sans vérité terrain doit prendre** :
fabriquer, dans le même corpus et sous les mêmes conditions d'acquisition, une région dont
on connaît la réponse — et faire que tout ce qu'on revendique ailleurs passe d'abord par
elle. Les quatre fragments ne sont pas quatre échantillons de plus : **ils sont
l'instrument**.

## 3. ⭐ Six choses à reprendre telles quelles

1. **Le rapport plutôt que le seuil.** *« recall higher than the false positive rate by a
   **factor of 8** »*. Un rapport entre deux quantités qui bougent ensemble quand on
   change le seuil résiste au réglage ; un seuil absolu est un nombre choisi pour que le
   réglage du jour passe.
2. **F0.5 comme déclaration de politique d'erreur.** β = 0,5 inscrit *dans la métrique*
   qu'un faux positif coûte plus cher qu'un faux négatif — parce qu'un caractère inventé
   pollue le corpus savant, alors qu'un caractère manqué ne fait que manquer.
3. ⭐⭐ **Le sens de l'erreur choisi en amont.** *« This slight preference for false
   negatives is **deliberately chosen** … as false positives … can **bias the subsequent
   meshing step** »*. Règle générale : quand les deux modes d'échec d'une passe ont des
   conséquences aval de **nature** différente — l'un ponctuel et corrigeable, l'autre
   systématique et propagé — on règle la passe pour qu'elle n'échoue que dans le sens
   corrigeable.
4. ⭐⭐ **µ et σ sur la seconde moitié de l'entraînement, jamais le meilleur point de
   contrôle.** *« taken from the second half of 620 000 training batches »*. Le nombre
   publié est une **distribution après convergence**, pas un maximum — et les σ sont ce
   qui permet de savoir si un écart entre deux méthodes veut dire quelque chose.
5. **La notation stricte contre soi-même.** *« even those characters identified as
   uncertain by the papyrologist are scored. **Excluding these characters would further
   improve the results.** »* Prendre la convention qui défavorise, et dire ce que l'autre
   aurait donné.
6. ⭐⭐ **Le juge humain calibré par transcription appariée.** Le protocole n'est pas « un
   expert regarde notre sortie ». C'est : un papyrologue **qui n'a jamais vu ces
   fragments** transcrit **la sortie**, puis **le même expert** transcrit **la vérité
   terrain**, et on compare **transcription contre transcription**. Les limites de
   l'expert s'appliquent alors **des deux côtés** et s'annulent.

⭐ Et une leçon de forme : **la reproductibilité est portée par une ligne de commande et un
hash de commit**, pas par de la prose.

## 4. ⚠⚠ Ce que le papier n'a PAS mesuré — et c'est notre créneau

### 4.1 La précision d'alignement n'est jamais mesurée

C'est la découverte la plus utile de cette lecture. L'alignement photo IR ↔ scan CT est
**manuel** (Photoshop *Puppet Warp*), parce que l'automatique a échoué :

> *« we have **not yet discovered an automated method** that is capable of successfully
> aligning the texture and infrared images. »*

Et sa précision n'est **ni mesurée, ni bornée, ni validée** : aucune erreur en pixels ou
en microns, aucun RMS sur les points d'appui, aucune validation croisée, aucune étude de
sensibilité. Ce que le papier dit à la place :

> *« **Since the label alignment is a manual process, some small error can be assumed.** »*

⭐ **L'erreur est traitée par ÉVITEMENT, pas par quantification** : les pixels proches des
frontières encre/non-encre sont **retirés de l'entraînement**, par dilatation de rayon
**16** autour des contours du label. C'est le **seul chiffre du papier qui encode
l'incertitude d'alignement**, et il a été choisi empiriquement.

⚠ *(Calcul dérivé, pas du papier : à 3,24 µm, 16 pixels ≈ **52 µm**, soit 5 à 10 fois
l'épaisseur d'encre estimée de 5–10 µm. C'est une borne implicite sur l'incertitude
admise.)*

⚠⚠ **Et l'exclusion est appliquée à l'ENTRAÎNEMENT, pas à l'ÉVALUATION.** Les métriques
sont calculées sur toute l'image, frontières comprises — donc elles mesurent en partie le
bruit de la référence. **Exclure les mêmes pixels des deux côtés est une correction
immédiate et gratuite**, et c'est un des rares endroits où on peut améliorer un résultat
publié sans rien recalculer de lourd.

### 4.2 Le seul contrôle sans vérité terrain — nommé, jamais outillé

Sur les couches cachées, où il n'y a par définition aucune vérité, l'unique argument est :

> *« Crucially, the **scale, line separation, and script** of the revealed characters are
> **consistent with those observed on the fragment surfaces**. »*

**La forme est exactement la bonne** : on possède une région vérifiable et une région qui
ne l'est pas, et on transporte la confiance en montrant que les **statistiques de second
ordre** coïncident. C'est un **transport de calibration**.

⚠ **Mais il est laissé au jugement de l'œil.** Ni l'échelle, ni l'interligne, ni le trait
ne sont mesurés. Or les trois sont mesurables **sans jamais connaître le contenu** :

| grandeur | comment |
|---|---|
| interligne | autocorrélation du profil de densité projeté perpendiculairement aux lignes — un pic net à la bonne période dans la zone vérifiée doit se retrouver dans l'autre |
| échelle de caractère | distribution des tailles de composantes connexes de la prédiction binarisée |
| taux de couverture | fraction de surface prédite « encre », qui doit rester dans la plage des surfaces à vérité terrain |
| épaisseur de trait | distribution des distances au squelette |

> ⭐⭐ **C'est un instrument à construire, et il est dans notre domaine exact** : la version
> **quantifiée** de « consistent with ». Le papier a nommé le contrôle et ne l'a pas
> outillé — trois ans plus tard, personne ne l'a fait.

✅ **Construit le 2026-08-22** → [`45`](45_consistent_with_quantifie.md). Les quatre
grandeurs sont mesurées sur 190 cartes publiées, et le résultat est plus intéressant que
prévu : deux d'entre elles retrouvent le classement du contraste d'encre (épaisseur de trait
AUC 0,857, netteté 0,753), et la **séparation des lignes va à contre-sens** (0,319). La
phrase du papier réunit trois propriétés qui, mesurées, ne vont pas ensemble.

### 4.3 ⭐⭐⭐ Le contrôle négatif parfait est dans leurs données, et le pipeline le jette

Le papier n'a **aucun contrôle négatif au sens fort**. Il rapporte un FPR de 0,051, mais
**sur des images qui contiennent de l'encre partout autour** : il ne mesure jamais ce que
le détecteur produit sur un substrat dont on **sait** qu'il n'en porte pas.

⚠⚠ **Et ce témoin existe, dans le même scan.** Les fragments sont montés sur une **feuille
de papier de support**, que la segmentation capte : *« the paper fibers are visible on the
**backing sheet** to which the fragment is mounted »*. Un substrat **fibreux**, imagé dans
la **même session**, au **même voxel**, avec la **même fenêtre d'intensité**, et dont on
sait qu'il ne porte **aucune encre**.

Le pipeline le **supprime** : *« These are removed manually, by selecting and deleting the
extraneous points. »*

> **Le témoin parfait était déjà dans l'image, et le nettoyage l'a jeté.**

Les autres contrôles absents, tous constructibles :

| contrôle | ce qu'il testerait |
|---|---|
| **papyrus vierge** | un détecteur qui ne se tait jamais ne détecte rien |
| **étiquettes permutées** | si la performance ne s'effondre pas, le modèle apprend le **substrat**, pas l'encre |
| ⭐ **volume désaligné** | décaler le recalage de N pixels et mesurer la dégradation donne **la sensibilité au désalignement**, donc la borne indirecte que §4.1 ne fournit pas |
| **second annotateur** | la **variance de la vérité terrain**, qui borne toute performance atteignable |
| **second papyrologue** | ⚠ **un seul** expert a jugé les 125 caractères ; aucun accord inter-juges |

### 4.4 Le critère d'acceptation le plus haut est sourcé à un reportage télévisé

> *« To be readable, letters should form lines with uniform and expected **scale, spacing,
> and margins**. »*

Cette phrase est le critère ultime du papier, et sa référence est **`60minutes`** — un
reportage. Elle n'est **jamais opérationnalisée** : aucune mesure d'échelle, d'espacement
ou de marge n'est rapportée.

⚠ **Un critère d'acceptation qu'aucune commande ne peut évaluer n'est pas un critère,
c'est une intention.** C'est exactement ce que `29` §3 dit du cap papyrologique de ce
dépôt — et ce papier montre que le domaine a le même trou.

## 5. Ce qui tient, ce qui est périmé

**Tient** : toute la doctrine de vérification (les trois niveaux visuel / pixel /
papyrologique), le critère asymétrique *recall vs hallucination*, la validation croisée
anti-mémorisation, l'architecture PPM → *surface volume* → labels alignés, et l'argument
physique **épaisseur d'encre 5–10 µm → il faut un voxel qui l'approche**.

⭐ Et une phrase de 2023 qui décrit, avant qu'on le comprenne, le signal que tout le
domaine exploite : *« a much more subtle signal … likely relating not only to image
intensity but to **morphological (texture, or shape) differences** between ink and blank
papyrus »*.

**Périmé** : les performances (recall caractère 0,42 — le papier les donne d'ailleurs
*« primarily as a benchmark against which future improvements can be evaluated »*, donc
c'est une péremption **par succès du dispositif**) ; le modèle (CNN 3D classifiant un
voxel central) ; et le goulot lui-même — **en 2023 le problème dur était l'encre,
aujourd'hui c'est la géométrie**, que ce papier ne traite quasiment pas.

⚠ La partie « périmé » de ce paragraphe engage des connaissances du domaine hors du
papier ; elle est à recouper avec `27` et `28`, qui sont, eux, mesurés sur des sources
lues intégralement.

## 6. ⭐ Ce que ça ajoute à `29`

Deux mesures nommées, toutes deux dans notre domaine et sans vérité terrain requise :

- **M7 — quantifier « consistent with »** : construire l'instrument de §4.2, celui que le
  papier nomme et n'outille pas. Interligne, échelle, couverture, épaisseur de trait,
  mesurés dans une région vérifiable puis **transportés** vers une région qui ne l'est pas.
- **M8 — le témoin jeté** : chercher, dans nos propres corpus, le substrat **connu sans
  encre** que le pipeline élimine. C'est la forme la plus économique d'un contrôle négatif
  — il est déjà acquis, dans les mêmes conditions.

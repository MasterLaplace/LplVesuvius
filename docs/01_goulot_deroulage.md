# Le goulot : isoler la feuille

Note de cadrage, 2026-08-16. Fondée sur le site (miroir complet, 81 pages) et sur
le code des dépôts clonés, pas sur des souvenirs.

---

## 1. Où en est réellement le concours

La chaîne complète a six étages. **Cinq sont automatiques.**

| étage | état | qui le fait |
|---|---|---|
| Volume tomographique | acquis | scanners (Diamond, ESRF) |
| Prédictions nnUNet (surface, fibres verticales, fibres horizontales) | **automatique** | villa |
| **Maillage de la surface** | **semi-manuel — le goulot** | VC3D, tracer, spiral fit |
| Paramétrisation 2D (aplatissement) | **automatique** | SLIM (`slim-flatboi`), VC |
| Rendu de la feuille | **automatique** | VC render |
| Détection d'encre | **automatique** | Grand Prize 2023, TimeSformer |

Le texte lui-même est lu par des papyrologues, qui n'attendent que les images.
Donc : **une heure gagnée à l'étage 3 est une heure de texte lisible en plus**,
et rien d'autre dans la chaîne ne rend ça.

## 2. Ce que « maillage de la surface » veut dire exactement

Un rouleau carbonisé est une **2-variété enroulée en spirale** plongée dans un
volume 3D. Le problème n'est pas de trouver *de la* surface — nnUNet le fait très
bien — mais de décider **quelle surface est laquelle**. Deux spires adjacentes
sont séparées d'environ 300 µm ; une feuille fait environ 40 µm d'épaisseur. Là où
le rouleau est comprimé, cet écart tombe à zéro et les deux feuilles se touchent.

D'où le mode de panne central, le **sheet switching** : la surface suivie saute
d'une spire à la suivante. Le résultat est une surface *continue, lisse, plausible*
— rien dans sa géométrie locale ne signale l'erreur. Le texte rendu mélange alors
deux passages du rouleau distants de plusieurs centimètres, et le seul détecteur
fiable aujourd'hui est un humain qui lit du grec.

> C'est très exactement le motif que ce projet recense en boucle : **une sortie
> fausse indistinguable d'une sortie juste**. Une automatisation qui n'exhibe pas
> un invariant capable de refuser sera verte pour une mauvaise raison.

## 3. Les deux familles, et pourquoi aucune ne gagne seule

**Spiral fitting** — descendante. On pose une spirale canonique 2D et on la
déforme en 3D par optimisation d'un champ de flot, sous contraintes de fidélité aux
données et d'alignement des fibres. *Quasi aucune intervention humaine.* Sa force
est sa faiblesse : elle **suppose** la spirale, donc elle est structurellement
immunisée contre le sheet switching, et structurellement incapable d'encaisser une
déchirure, un décollement ou un noyau effondré.

**Surface tracer** — ascendante. On sème des patches, on les fait croître, on
recolle ceux qui se recouvrent, sous contraintes de fidélité, continuité et
courbure. Elle épouse la vraie géométrie, y compris pathologique — mais elle dérive,
et elle coûte encore **~4 h d'intervention humaine** par soumission.

**Le contraste est le fait utile** : l'une porte une contrainte globale sans
souplesse locale, l'autre une souplesse locale sans contrainte globale. Ce qui
manque entre les deux est un **numéro d'enroulement** (*winding number*) : la
réponse à « combien de tours depuis le cœur ». C'est la seule quantité qui rend le
sheet switching *nommable* — deux points de la même feuille ont le même numéro, un
saut de spire l'incrémente de un.

⚠ **Correction, obtenue en lisant le code plutôt que le site.** J'allais écrire que
le concours « n'a pas de moyen de calculer le winding ». C'est faux, et l'erreur
aurait orienté tout le reste :

- `villa/lasagna/` est un outillage entier dédié à ça — `labels_to_winding_volume.py`,
  `opt_loss_winding_volume.py`, `opt_loss_winding_density.py` ;
- `villa/volume-cartographer/apps/diffusion/vc_diffuse_winding.cpp` diffuse un champ
  de winding dans le volume ;
- `apps/diffusion/spiral*.{hpp,cpp}` (dont `spiral_ceres.cpp`) est le spiral fit,
  en C++ sur Ceres.

Le winding est donc **déjà calculé**. Ce que le problème ouvert nº7 réclame est
plus étroit et plus dur : **des métriques d'évaluation, des fonctions de coût, et
l'introduction automatique de la contrainte**. Autrement dit le manque n'est pas
« produire un numéro », c'est **savoir si celui qu'on a produit est bon**.

⚠ Deuxième correction : **ThaumatoAnakalyptor est déprécié**, pas seulement migré —
il vit dans `villa/deprecated/thaumato-anakalyptor` (avec `crackle-viewer` et
`vesuvius-c`). Son rapport technique garde de la valeur, son code non.

⚠ Troisième : le **source markdown du site est dans villa** (`scrollprize.org/docs/`,
34 fichiers). Pour lire, c'est supérieur au miroir HTML — le miroir sert à figer un
état daté et à travailler hors ligne, pas à être la référence de lecture.

## 4. Ce que ce projet apporte de spécifique

Trois choses, et aucune n'est « un meilleur modèle » :

1. **La vérification comme livrable.** Le dépôt `vesuvius-automesh` ne revendique
   que 61 fenêtres sur 106 — celles qui passent un contrôle de topologie
   indépendant. `scrollfiesta` compile `wind_audit`, `manifold_check`, `seam_audit`,
   `orient_audit`, `pinhole_verdict`, `pred_reject`. Ce sont des **gates**, au sens
   exact où ce projet emploie le mot. C'est notre terrain, et c'est celui où le
   concours a le plus de mal, parce qu'écrire un vérificateur demande de savoir
   *comment la chose échoue* plutôt que d'ajouter des paramètres.

2. **La géométrie déterministe et entière.** Un numéro d'enroulement est un
   **entier**. Une contrainte de spire est une relation d'ordre. Ce sont des objets
   qui n'ont aucun besoin de virgule flottante, donc qui tombent exactement dans le
   contrat Fixed32 — et qui se **foldent**, c'est-à-dire se comparent bit à bit
   entre deux machines. Un pipeline de déroulage dont deux exécutions donnent deux
   maillages différents est un pipeline dont on ne peut pas mesurer un progrès.

3. **La discipline « mesurer, pas relire ».** Le champ est plein de résultats
   verts pour de mauvaises raisons — c'est ce que dit le problème ouvert nº4
   (« qualité des étiquettes », nommé comme un des goulots principaux : le modèle
   apprend une représentation imparfaite du trait physique et personne ne le voit).

## 5. Pistes, par rapport coût/valeur

Aucune n'est engagée — c'est une liste à trancher, pas un plan.

| # | piste | pourquoi elle tient | risque principal |
|---|---|---|---|
| A | **Métrique et gate de winding** : à partir d'un maillage livré, juger la cohérence d'enroulement face à la structure CT et **refuser** les faces incohérentes | c'est le problème ouvert nº7 pris par le bout qui manque (*évaluer*, pas *produire*) ; aucun entraînement ; s'applique à **toute** méthode existante | définir l'ombilic sur un rouleau effondré |
| B | **Réparation de connectivité** (problème nº3) : détecter et corriger trous, fusions et sauts de spire sans inspection humaine | nommé tel quel dans les problèmes ouverts ; consomme directement la sortie de A | sans A, on ne sait pas si la réparation a amélioré quoi que ce soit |
| C | **Fusion des deux familles** : spiral fit en *prior* global, tracer en correction locale | attaque nº7 de front | c'est ce que tout le monde essaie, avec plus de moyens |
| D | **Qualité des étiquettes** (problème nº4) | goulot nommé par les organisateurs | demande l'accès aux jeux annotés |

### Alignement sur les prix ouverts

Le calendrier tranche autant que la technique :

| prix | montant | échéance | pertinent ici ? |
|---|---|---|---|
| **Progress Prizes (mensuels)** | **20 k$ garantis/mois**, + lots de 0,5 à 20 k$ | **31 août 2026**, puis chaque mois | **oui, directement** |
| Grand Prize 2027 | 1 M$ (800/100/50/50) | 25 juin 2027 | dérouler un rouleau **entier**, 70 % de caractères lisibles |
| First Letters | 50 k$ par rouleau (≤ 500 k$) | 25 juin 2027 | 10 lettres sur 4 cm² — bien plus atteignable |
| Titre de PHerc. Paris 4 | 50 k$ | 25 juin 2027 | ouvert indéfiniment |

Les critères des Progress Prizes sont, mot pour mot : contribution open source sur
un problème de la *wishlist*, **amélioration quantitative sur données réelles**,
correction de bugs d'outils réellement utilisés, documentation qui permet à
d'autres de s'en servir. **C'est la description exacte de la piste A.**

**Recommandation : A, en visant le Progress Prize.** Trois raisons, dans cet ordre :

1. C'est la seule piste qui **produit de la valeur même si elle n'automatise rien** :
   un vérificateur qui refuse correctement sert à tous les autres participants.
2. Elle est **soumissionnable à court terme** — mensuelle, pas dans dix mois.
3. Elle donne la mesure sans laquelle B et C sont du bricolage : on ne peut pas
   améliorer un maillage tant qu'on ne sait pas dire lequel de deux est le meilleur.

**First Letters** est la cible sérieuse à moyen terme (50 k$, 4 cm² seulement) et
devient réaliste **si** A puis B tiennent — mais s'y attaquer d'abord serait
recommencer ce que des équipes mieux dotées font déjà.

## 6. Ce qui n'est pas tranché, et doit l'être avant d'écrire du code

- **Quelle échelle de données** on se donne. Une fenêtre de quelques cm² suffit
  pour A ; B demande un rouleau entier, donc des dizaines de gigaoctets.
- **CC-BY-NC 4.0** : usage non commercial, attribution obligatoire. La contrainte
  se propage à tout ce que le corpus Laplace en dérive.
- **Le raccordement à LplKnowledge** : hors scope tant qu'il n'y a pas de texte.
  Le jour où il y en a, c'est un lecteur `harvest::` de plus, pas une architecture.

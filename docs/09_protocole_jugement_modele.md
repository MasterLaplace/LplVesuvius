# Faire juger un rendu par un modèle de langue, sans se mentir

2026-08-17. Protocole et prompt, en attendant un papyrologue.

---

## 1. Le mode de panne à neutraliser

Devant une image de grec ancien dégradé, un modèle de langue **produira du grec
plausible**. Il connaît Philodème, il connaît la koinè, il connaît les formules
épicuriennes — il peut donc composer une transcription cohérente **sans lire
l'image**. Sa sortie serait alors indistinguable d'une vraie lecture.

C'est le motif que ce projet traque depuis le début : **une sortie fausse qui
ressemble exactement à une sortie juste**.

> Un avis non calibré n'est pas une donnée faible. Ce n'est **pas une donnée**.

## 2. Le protocole, avant le prompt

Trois familles d'images, mélangées, **sans dire au modèle laquelle est laquelle** :

| famille | ce que c'est | ce qu'on attend |
|---|---|---|
| **Témoin positif** | un rendu dont le texte est **publié et lu** (régions du Grand Prize 2023) | il doit le retrouver |
| **Témoin négatif** | du bruit, ou une région **sans encre** passée par le même pipeline | il doit **refuser** |
| Inconnu | ce qu'on veut vraiment faire juger | — |

⚠ **L'ordre compte, et il est irréversible.** Le calibrage doit être fait **avant**
de montrer quoi que ce soit d'inconnu. Une fois qu'un modèle a vu une image non
calibrée dans un fil, on ne peut plus mesurer son taux d'invention sans biais.

⚠ **Le témoin négatif est le plus important.** Un modèle qui transcrit les trois
familles avec la même assurance n'a rien lu du tout — et c'est le seul test qui
puisse l'établir.

### Ce qu'on mesure

1. sur les témoins positifs : **taux de caractères corrects** contre le texte publié ;
2. sur les témoins négatifs : **taux de refus** ;
3. la **cohérence de la confiance** — sa confiance déclarée doit chuter sur le bruit.

Un modèle qui échoue en 2 est disqualifié pour l'inconnu, quel que soit son score
en 1.

## 3. Le prompt

Le prompt ci-dessous est conçu pour **rendre le refus facile et la fabrication
coûteuse**. Ses choix, dans l'ordre :

- **aucun contexte d'auteur, d'œuvre ou de sujet** — le donner invite à compléter de
  mémoire plutôt qu'à lire ;
- **transcription caractère par caractère**, avec position, plutôt qu'un texte
  fluide — un mot fluide se devine, une grille de caractères se lit ;
- **le refus est une réponse attendue et nommée** (`·` pour illisible), pas un aveu
  d'échec ;
- **interdiction explicite de reconstruire** une lacune, même « évidente » ;
- **confiance par caractère**, ce qui rend l'invention mesurable a posteriori.

```
Tu regardes une image produite par un pipeline de détection d'encre appliqué à un
papyrus carbonisé. Les zones sombres sont les endroits où le modèle estime qu'il y
a de l'encre. Le fond clair est le support. Le gris uni, s'il y en a, est une zone
non analysée.

Ta tâche est de RELEVER ce qui est visible, pas de reconstituer un texte.

Règles, dans l'ordre de priorité :

1. Ne transcris QUE ce que tu vois. N'utilise aucune connaissance de la langue,
   d'un auteur ou d'un corpus pour compléter, corriger ou deviner un caractère.
2. Un caractère que tu ne peux pas identifier avec certitude s'écrit « · ».
   Écrire « · » est une bonne réponse. Ce n'est pas un échec.
3. Ne complète JAMAIS une lacune, même si la restitution te paraît évidente.
4. Si l'image ne contient aucune forme de lettre, réponds exactement :
   AUCUNE LETTRE VISIBLE
   et rien d'autre.

Format de réponse, strictement :

LIGNES: <nombre de lignes de texte que tu distingues, ou 0>
Puis, pour chaque ligne, dans l'ordre de haut en bas :
L<n>: <suite de caractères grecs et de « · », sans espaces inventés>
L<n>_CONFIANCE: <un chiffre de 0 à 9 par caractère de la ligne, dans le même ordre>

Enfin :
LISIBILITE: <0 à 10 — 0 = aucune lettre identifiable, 10 = texte suivi lisible>
JUSTIFICATION: <une phrase décrivant ce qui, dans l'image, soutient ta note>

Ne produis rien d'autre que ce format.
```

## 4. Le prompt du témoin négatif

Identique. **Ne rien changer** : si l'on adapte le prompt au bruit, on ne mesure
plus la même chose. La réponse attendue est `AUCUNE LETTRE VISIBLE`.

## 5. ⚠ Ce que ce protocole ne remplace pas

Il mesure si un modèle **lit ou fabrique**. Il ne dit rien de la justesse
papyrologique d'une lecture : accents, ligatures, abréviations, variantes de main
et scriptio continua sont l'affaire d'un spécialiste.

**Un score élevé ici autorise à montrer le résultat à un expert. Il ne le remplace
pas** — et le cap fixé pour ce projet reste le jugement humain (`06` §1bis).

---

## 6. ⚠ Deux juges mécaniques essayés, deux échecs — avec leurs raisons

Tentative de remplacer le jugement humain par une mesure automatique, pour obtenir
un « pourcentage de cohérence ». **Les deux ont échoué**, et les raisons valent
d'être écrites : elles disent ce qu'il faudrait pour réussir.

### Kraken (HTR) — mauvaise modalité

Installé (7.1) avec le seul modèle grec de son dépôt, **CLLG Polytonic Greek**.

⚠ Sur les 65 modèles de reconnaissance disponibles, **aucun n'est entraîné sur des
papyri**. CLLG l'est sur des **éditions critiques imprimées**. Double décalage :
imprimé contre manuscrit, photographie contre carte de détection d'encre.

Mesuré :

| image | lignes segmentées | caractères |
|---|---|---|
| texte réel | 4 | **6** (`Eʹ 1 4 e`) |
| papyrus sans encre | 2 | 2 |

Six caractères de bruit contre deux. Un signal du niveau du bruit, et une sortie
absolue vide de sens. **Inutilisable comme transcripteur, et trop faible comme
détecteur.**

### Score structurel — bonne idée, région trop petite

Idée : ce qui distingue de l'écriture de taches est **structurel** et non
linguistique — lignes régulièrement espacées, épaisseur de trait constante, hauteur
de caractère constante. Aucune de ces grandeurs ne demande de savoir lire, donc
aucune ne peut inventer un sens. Implémenté dans `htr/src/coherence.py`.

Mesuré, et **il ne discrimine pas** :

| | texte réel | sans encre |
|---|---|---|
| périodicité verticale | 0,815 | **0,889** ⚠ mauvais sens |
| variation de trait | 0,944 | 0,977 |
| variation de hauteur | 1,151 | **0,821** ⚠ mauvais sens |

**Diagnostic, cherché avant de régler quoi que ce soit** : les interlignes trouvés
valent 8 et 12 px alors qu'une lettre fait ~400 px. Ce n'est pas du texte qui est
mesuré, c'est la **grille de ré-agrandissement ×16** du modèle. Et sur la vérité
terrain elle-même, l'autocorrélation ne trouve **aucun pic** — parce que la région
ne contient que **4 ou 5 lignes**, quand une autocorrélation a besoin de nombreuses
périodes.

### Ce que ces deux échecs établissent

**Aucune mesure de cohérence ne peut fonctionner sur 20 × 24 mm.** Il faut assez de
lignes pour qu'une régularité existe — donc le **segment entier** (`06` §3bis, A).

Et le protocole des §1 à 5 reste le seul juge disponible d'ici là. Son témoin
négatif — `B_negatif.png`, un vrai papyrus sans encre passé par le même pipeline —
a été construit après avoir jeté un premier témoin fait de bruit gaussien : trop
facile à rejeter, il n'aurait rien prouvé.

---

## 7. Première soumission réelle à un modèle, et ce qu'elle a appris

2026-08-17. L'auteur a soumis une image à Gemini. **Deux enseignements, dont un
imprévu.**

### ⚠ L'image envoyée était la mauvaise — et l'erreur est instructive

C'était `08_verite.png`, c'est-à-dire **la vérité terrain** : le tracé fait à la
main par un humain qui a suivi les lettres. Le modèle a donc analysé un dessin de
lettres grecques et conclu qu'il s'agissait de lettres grecques. Vrai, et **sans
aucune information sur notre pipeline**.

**Leçon de protocole** : les images destinées à un juge doivent être nommées de
façon à rendre cette confusion impossible. `A_positif.png` / `B_negatif.png` ne
disent pas ce qu'elles contiennent ; `08_verite.png` ressemble à un résultat.

### ⚠⚠ Et sa réponse contenait une affirmation fausse, vérifiable

Le modèle a écrit :

> « Régularité de l'interligne : la distribution verticale et le rythme des
> espacements correspondent **exactement** au calibre d'écriture d'un scribe
> régulier. »

Mesuré sur cette image exacte :

| grandeur | valeur |
|---|---|
| bandes horizontales portant de l'encre | **3** |
| espacements | **590 px et 1251 px** (facteur 2,1) |
| écart-type / moyenne | **0,36** |
| pic d'autocorrélation (200–1200 px) | **0,159** — une décroissance, pas un rythme |

Il n'y a **aucune régularité d'interligne** dans cette image, et il en affirme une
« exacte ».

### Ce que ça établit sur l'usage d'un modèle comme juge

Son identification des lettres est probablement **juste** — le tracé est franc.
Mais dès qu'il **quantifie**, il embellit. Ce n'est donc pas une hallucination
grossière, facile à repérer : c'est une **précision inventée posée sur une
observation correcte**, et c'est bien plus dangereux, parce que la partie vraie
donne du crédit à la partie fausse.

**Conséquence pour le protocole** : ne jamais accepter d'un modèle une affirmation
quantitative sur l'image (rythme, régularité, nombre de lignes, proportions). Ces
grandeurs se **mesurent**. Ce qu'on peut lui demander est une **identification de
forme**, et seulement avec son témoin négatif.

C'est pour cette raison que le format imposé au §3 réclame des caractères et des
confiances, jamais un commentaire libre : un commentaire libre est exactement
l'endroit où cette embellie se produit.

---

## 8. ⚠⚠ Le §6 s'était trompé de cause — corrigé le 2026-08-17

Le §6 concluait : *« aucune mesure de cohérence ne peut fonctionner sur 20 × 24 mm,
il faut assez de lignes — donc le segment entier »*.

**Le segment entier a été passé, et il n'a pas plus de lignes.** Mesuré sur ses
91,7 × 30,7 mm : **5 lignes de texte dans la vérité terrain, 4 dans la prédiction**,
d'interligne 3,6 à 7,1 mm. Ce segment est une bande étroite coupée *en travers* du
texte : l'allonger allonge les lignes, il n'en ajoute pas.

Le juge structurel a donc échoué une **troisième** fois, avec une troisième cause
(détail et deux défauts de ma propre mesure dans `10` §4) :

| tentative | cause de l'échec |
|---|---|
| Kraken | mauvaise modalité — aucun modèle entraîné sur papyri |
| score structurel, région | *croyait* manquer de surface |
| score structurel, segment | **manque de LIGNES**, et les glyphes fusionnent |

Ce qu'un juge mécanique demanderait réellement : (a) plusieurs dizaines de lignes,
donc un segment couvrant **plusieurs colonnes** de texte ; (b) des glyphes
**séparables**, alors qu'au seuil de décision du modèle les lettres voisines
fusionnent en composantes connexes géantes — 41 composantes dans une région qui en
montre des centaines.

**Le protocole des §1 à 5 reste donc le seul juge disponible**, et le cap reste le
jugement humain.

### Les images du protocole sont refaites, et le témoin négatif est meilleur

`data/juge/` porte désormais trois images tirées du **même segment**, du **même
passage** du modèle, ne différant que par leur contenu — donc tout écart de réponse
porte sur le papyrus et non sur la chaîne :

| image | ce que c'est | réponse attendue |
|---|---|---|
| `A_positif.png` | région de texte, lettres franches | il doit relever des lettres |
| `B_negatif.png` | bande **vierge**, accordée par l'humain **et** le modèle | `AUCUNE LETTRE VISIBLE` |
| `C_inconnu.png` | bande où le modèle produit du signal et l'humain n'a rien annoté | — |

⚠ **`B_negatif.png` est un bien meilleur témoin que le précédent** : il vient du même
segment et de la même passe, alors que l'ancien venait d'ailleurs. Un modèle qui
transcrit A et B avec la même assurance n'a rien lu — et c'est le seul test qui
puisse l'établir.

⚠ **L'ordre reste irréversible** : A et B d'abord, C seulement après. Montrer C avant
d'avoir calibré rend le calibrage impossible sans biais.

⚠ **Les images sont en orientation de lecture** (rotation 270°). Les versions
antérieures présentaient les lettres couchées, ce qui pénalise un juge pour une
raison qui n'a rien à voir avec la détection d'encre.

---

## 9. ⭐ Le calibrage a été fait, automatiquement — 2026-08-17

`analysis/src/judge_api.py`, modèle **`gemini-3.5-flash`**, 8 appels, température 0.

⚠ **Trois modèles ont été éliminés avant, par mesure et non par supposition** :
`gemini-2.5-flash`/`-pro` répondent `404` (« no longer available to new users »),
`gemini-3.1-pro-preview` et `gemini-pro-latest` répondent `429` (hors offre gratuite),
`gemini-3.7-flash` répond `503`. Le nom du modèle n'est pas codé en dur pour
exactement cette raison — un nom périmé produit une erreur qui ressemble à une panne
de l'expérience.

### Le résultat : il refuse quand il n'y a rien

| condition | panneaux | corrects | **fabriqués** | manqués |
|---|---:|---:|---:|---:|
| `texte \| vierge` | 4 | 4 | 0 | 0 |
| `vierge \| texte` | 4 | 3 | 0 | 1 |
| ⭐ `vierge \| vierge` | 4 | **4** | **0** | 0 |
| `texte \| texte` | 4 | 4 | 0 | 0 |

**15 sur 16, zéro fabrication.** Sur les 8 panneaux vierges : 6 refus au mot près,
2 abstentions par `·`.

L'unique manque n'en est pas vraiment un : sur une région de texte il a rapporté
`LIGNES: 2` — donc il a bien vu deux lignes — sans identifier les caractères.

### La confiance déclarée sépare, et c'est le critère qui compte

| panneaux | `LISIBILITE` | médiane |
|---|---|---:|
| **vierges** | 0 · 0 · 0 · 0 · 0 · 0 · 1 · 1 | **0** |
| **texte** | 3 · 3 · 4 · 4 · 4 · 5 · 5 · 6 | **4** |

**Aucun chevauchement** : max(vierge) = 1, min(texte) = 3. Sur 16 panneaux, sa note
de lisibilité discrimine parfaitement. C'est ce qui autorise à lui montrer de
l'inconnu.

### ⚠⚠ Et mon dépouilleur accusait à tort

Première version : un panneau vierge était compté correct **seulement** s'il portait
la phrase de refus au mot près. Or sur un essai le modèle a répondu uniquement des
`·` — c'est-à-dire le marqueur « je n'identifie pas » que le prompt lui-même
fournit, donc l'exact **contraire** d'une fabrication.

Le verdict imprimé était **« le modèle fabrique »**, sur un modèle qui s'était
correctement abstenu. Corrigé : fabriquer, c'est produire des caractères
**identifiables** là où il n'y en a pas ; un point n'en est pas un.

⚠ **Le contrôle des bandes a lui aussi servi** : ma liste de témoins « vierges »
contenait `7168–8192`, qui mesure en fait **3,75 %** d'encre prédite. Un témoin où le
modèle trouve du signal aurait compté comme une fabrication chacune de ses lectures
correctes. Vérifié avant l'appel, donc corrigé pour zéro jeton.

⚠ **Limite assumée** : la seule zone franchement vierge du segment fait ~2000 lignes,
donc les trois fenêtres de témoin **se recouvrent**. Ce ne sont pas trois observations
indépendantes, et un balayage complet n'en trouve pas d'autres.

## 10. ⭐ Le juge calibré tranche la bande douteuse : ce n'est PAS du texte

La question laissée ouverte par `10` §3bis — les bandes 8704–9728, où notre détecteur
produit 7,6 à 9,8 % d'encre et où personne n'a annoté. Soumise **avec son témoin dans
la même image**, dans les deux sens (2 appels) :

| | `LISIBILITE` | glyphes identifiés |
|---|---:|---:|
| bande douteuse, à gauche | **1** | 0 |
| bande douteuse, à droite | **2** | 1 |
| témoin vierge (les deux fois) | refus | 0 |

**1 et 2, c'est le régime du papyrus vierge** (0–1), pas celui du texte (3–6).

Quatre observations indépendantes convergent donc :

| source | ce qu'elle dit |
|---|---|
| notre détecteur | 7,6–9,8 % d'encre — autant que le texte dense |
| l'étiquetage humain | 0,00 % |
| le rendu | traits épais et **informes**, pas des lettres |
| le juge calibré | lisibilité **1–2**, régime du vierge |

⚠ **Ma lecture initiale — « trou d'annotation » — est donc réfutée.** Cette bande
porte du signal **sans écriture**. Reste à savoir *quoi* : faux positifs du détecteur,
matière encrée qui n'est pas de l'écriture, ou une feuille voisine vue à travers un
saut de spire. C'est la tâche D, et `10` §5 dit ce qui la bloque (le maillage `tifxyz`
de ce segment n'est pas dans notre jeu).

**Coût total du calibrage et du verdict : 10 appels, ~34 000 jetons.**

---

## 11. Transporter le juge sur un rouleau sans vérité terrain — 2026-08-18

Le calibrage tient sur `20230909121925` parce qu'un humain y a dit **où** est le
texte. Sur Scroll 4 personne ne l'a dit, et c'est précisément la situation qu'il faut
savoir traiter : un détecteur qui ne se juge que là où quelqu'un a déjà annoté ne se
juge nulle part d'utile.

### ⚠⚠ Les coordonnées de `TEXT_BANDS` / `BLANK_BANDS` ne se transportent PAS

Ce sont des lignes mesurées sur un segment précis. Les appliquer ailleurs revient à
**tirer des fenêtres au hasard en croyant tirer des témoins**. `--auto-bands` les
choisit sur la sortie du détecteur lui-même, au seuil **logit > 0** — celui qui a donné
l'AUC 0,925, et pas un autre : en inventer un ici ferait dépendre le choix des bandes
d'un réglage que rien ne valide.

⚠ **Et le mot « texte » devient un mensonge.** Sans étiquetage on ne sait pas qu'une
bande porte du texte, seulement que le détecteur y annonce de l'encre. Le genre
s'appelle **candidat**, et l'expérience teste alors : *le juge lit-il des lettres là où
notre détecteur annonce de l'encre, et refuse-t-il là où il n'en annonce pas ?* C'est
exactement la question quand on transporte un détecteur sur un rouleau qu'il n'a jamais
vu — et elle n'a pas besoin de vérité terrain pour être posée.

### 🎯 Le sélecteur retrouve la bande choisie à la main, et durcit une limite

`--bands-only` montre ce qu'on soumettrait, **sans clé ni appel** :

| bandes demandées | candidat | vierge |
|---|---|---|
| 1 | **3584** (13,91 %) | **6656** (1,14 %) |
| 2 | + 9728 (12,43 %) | — |
| 3 | + 1024 (9,46 %) | — |
| 4 | + 8192 (8,17 %) | — |

- ✅ La première bande candidate est **3584**, c'est-à-dire exactement
  `TEXT_BANDS[0]`, choisie à la main sur l'étiquetage humain. Le choix automatique
  **reproduit** le choix humain.
- ⚠⚠ **Le segment n'a de la place que pour UNE bande vierge**, quel qu'en soit le
  nombre demandé. `09` notait déjà que la seule zone franchement vierge fait ~2000
  lignes et que les trois fenêtres retenues à la main **se recouvraient** ; la règle
  « pas de recouvrement, 512 lignes d'écart » rend ce fait mesurable au lieu de le
  laisser en note. Les trois « témoins » n'étaient pas trois observations.

### ⚠ Un plafond de pureté, parce que la faute avait déjà été payée

Sans plafond, demander trois bandes vierges en rend trois — à **1,14 %, 6,58 % et
8,17 %** d'encre prédite. Les deux dernières portent **plus** de signal que la bande
(7168, 1024) déjà listée puis retirée à la main après mesure à **3,75 %**. Un témoin où
le détecteur trouve du signal n'est pas un témoin : chaque lecture correcte du modèle y
compterait comme une fabrication.

`--blank-ceiling` (défaut **0,02**) refuse d'en rendre plutôt que d'en rendre de faux,
donc **les listes reviennent plus courtes que demandé** — ce qui est l'information, pas
un défaut.

⚠ Deux témoins hors ligne gardent ça (`tools/temoins.sh`, 14 contrôles) : le compteur
du sélecteur doit **retrouver les 3,75 %** mesurés à la main sur (7168, 1024), et
**relever le plafond à 0,10 doit rendre plus de bandes** — sans ce dernier, « une seule
bande vierge » serait aussi ce que rendrait un sélecteur cassé.

⚠ Un bug réel trouvé par ces témoins : la séparation était imposée à l'intérieur de
chaque genre mais **pas entre les deux**. Une bande candidate recouvrant une bande
vierge met la même image des deux côtés de la barre noire — la condition
`candidat | vierge` n'oppose alors plus rien.

```bash
cd inference_xpu
uv run python ../analysis/src/judge_api.py <prediction.npy> --bands-only
uv run python ../analysis/src/judge_api.py <prediction.npy> --auto-bands \
    --model gemini-2.5-flash --trials 1
```

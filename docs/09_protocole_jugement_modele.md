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

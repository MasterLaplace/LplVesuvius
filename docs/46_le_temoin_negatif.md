# 46 — Le témoin négatif : deux cartes étrangères, une confiance égale

> ⚠⚠⚠ **REFAIT LE 2026-08-28, ET LA CONCLUSION A CHANGÉ DE NATURE.** La mesure du
> 2026-08-22 a été faite avec la constante de normalisation que [`60`](60_la_constante_qui_rendait_le_modele_muet.md)
> a corrigée : les piles `uint8` arrivaient au modèle **257 fois trop sombres**, donc les deux
> cartes étaient quasi **constantes** — et deux constantes corrèlent parfaitement. Le
> `ρ = +0,9979` publié alors n'était pas un fait sur le modèle, c'était **la signature du
> bug**. Le titre disait « rend la même carte » ; ce n'est pas vrai.
>
> ⭐ Le résultat refait est **différent, et plus dur pour le domaine** : les deux cartes sont
> étrangères l'une à l'autre — donc le détecteur répond bel et bien à ses entrées — et il
> répond avec **autant de confiance, davantage même**, sur la surface dont on a la preuve
> géométrique qu'elle ne porte pas de feuille.

2026-08-22. [`32`](32_educelab_le_papier_fondateur.md) §4.3 relève que le papier fondateur
n'a **aucun contrôle négatif au sens fort** : il rapporte un taux de faux positifs, mais sur
des images qui contiennent de l'encre tout autour. Il ne mesure jamais ce qu'un détecteur
produit sur un substrat dont on **sait** qu'il n'en porte pas. `29` M8 portait la question.
La voici mesurée — et le résultat n'est pas celui qui était visé.

![deux volumes différents, une seule réponse](images/46_temoin_negatif.png)

Instrument : [`src/encre/temoin_negatif.py`](../src/encre/temoin_negatif.py)
(33 témoins hors ligne) et [`figure_temoin_negatif.py`](../src/figures/figure_temoin_negatif.py)
(16 témoins).

---

## 1. ⭐⭐ Un témoin négatif meilleur que celui qui manque au domaine

Le témoin parfait était dans le scan d'EduceLab : **la feuille de papier de support** sur
laquelle les fragments sont montés, imagée dans la même session, au même voxel. Le nettoyage
manuel la supprime — *« These are removed manually. »*

Le nôtre est meilleur, et il était déjà mesuré. [`38`](38_ce_qui_bouge_avec_la_fenetre.md)
établit qu'une de nos traces sort à **α = +1,01** : sa distance à la matière **suit** la
fenêtre de rendu, donc il n'y a aucune feuille à portée — la surface est posée *en travers*
de l'empilement. Ce n'est pas une supposition sur la nature d'un substrat, c'est une
**preuve géométrique** qu'il n'y a pas de face de papyrus là.

Le contrôle positif est le segment **officiel du même rouleau**, à α = +0,00, rendu par le
même outil. Même volume, même voxel, même modèle, même taille de région, même pas de
balayage : la seule chose qui change est de savoir s'il y a une feuille sous la surface.

## 2. ⚠⚠ La thèse visée est hors de portée, et il faut le dire d'abord

| | σ | rapporté au modèle qui marche |
|---|---:|---:|
| Scroll 1, 2,4 µm — où le modèle atteint AUC 0,925 ([`36`](36_lorigine_de_la_pile.md) §5bis) | **0,7712** | 100 % |
| `PHerc1447`, contrôle **positif** de cette expérience | **0,0129** | **1,7 %** |

Le détecteur ne rend pas une prédiction faible sur ce rouleau : il rend une **constante**.
`36` §5bis l'avait déjà mesuré deux fois — sur notre rendu **et** sur le volume de surface
publié, donc notre chaîne n'y est pour rien.

> ⚠⚠ **Il n'y a donc pas de détecteur en marche à contrôler.** La thèse visée — *le
> détecteur signale de l'encre là où la géométrie prouve qu'il n'y a pas de feuille* — est
> **hors de portée** : il n'en signale nulle part ici. L'instrument **refuse** de la
> conclure, et le seuil de ce refus (10 % de la sortie du modèle là où il marche) est ce
> qui le rend capable d'échouer pour la bonne raison.

⭐ Sans cette garde, le script aurait imprimé *« le détecteur produit autant de structure là
où il n'y a pas de feuille »* — un verdict **faux**, parce que la cause n'est pas que le
témoin trompe le détecteur, c'est qu'il est éteint des deux côtés. Deux cartes plates
donnent un rapport de dispersions proche de 1, exactement comme deux cartes riches
équivalentes.

> ⚠⚠⚠ **À REFAIRE — le contrôle positif de cette expérience était plat pour une raison
> instrumentale.** Les deux piles qu'elle compare (`data/couches/PHerc1447_20250702235910`
> et `data/leur_graine/rendu_41`) sont **uint8**, et le lecteur les divisait par 65535 :
> le modèle recevait du noir dans les deux cas. Un détecteur muet rend évidemment « la même
> carte » sur deux entrées quelconques, donc **ρ = +0,9979 ne dit rien sur la géométrie** —
> il dit que les deux entrées étaient également noires. Voir
> [`60`](60_la_constante_qui_rendait_le_modele_muet.md). Le texte ci-dessous est conservé tel
> qu'il a été publié.

## 3. ⭐⭐ La thèse refaite, avec le modèle réparé

Le rapport des dispersions ne peut pas faire la différence entre *deux cartes de même
amplitude* et *la même carte*. C'est là qu'était la question restante : un détecteur qui rend
deux cartes **différentes** répond à ses entrées, même faiblement ; un détecteur qui rend
**deux fois la même carte** sur deux surfaces géométriquement incompatibles ne répond pas du
tout.

| | 2026-08-22 *(constante cassée)* | **2026-08-28 (refait)** |
|---|---:|---:|
| σ du positif, sur sa feuille | — | **0,5894** |
| σ du négatif, en travers | — | **0,7111** |
| rapport des dispersions | — | **×0,83** |
| σ du positif rapporté au modèle qui marche (0,7712) | 2,4 % | **76,4 %** |
| corrélation pixel à pixel | ~~+0,9979~~ | **−0,0100** |
| écart médian entre les deux cartes | ~~0,00038~~ | **0,4342** |
| … rapporté à ce que chaque carte varie | ~~2,9 %~~ | **66,8 %** |
| … ce que donneraient deux cartes **étrangères** | 95,4 % | 95,4 % |

⭐⭐ **Trois lectures, et il faut les tenir ensemble :**

1. **Le modèle répond.** ρ passe de +0,9979 à **−0,0100** : les deux cartes n'ont plus rien à
   voir l'une avec l'autre. L'ancienne thèse « il rend la même carte quoi qu'on lui donne »
   est **morte**, et c'est bien le bug qui la fabriquait.
2. ⚠⚠⚠ **Mais il répond avec la même assurance sur du vide.** Le négatif — une surface dont
   `38` prouve géométriquement qu'aucune feuille n'est à portée — est **plus dispersé** que
   le positif (0,7111 contre 0,5894) et **plus contrasté** (1,869 contre 1,471). Ce que le
   détecteur rapporte là est un faux positif **par construction**, et **rien dans la sortie
   ne le distingue** d'une vraie détection.
3. ⚠ **Les deux cartes ne sont pas non plus complètement indépendantes** : 66,8 % de variation
   partagée là où deux cartes sans rapport en donneraient 95,4 %. Il reste donc un signal
   commun aux deux volumes — la texture du bloc, probablement — que ce témoin ne sépare pas.

> ⚠⚠⚠ **La conclusion pour le domaine est plus dure que celle de 2026-08-22**, et non plus
> douce. Un modèle bloqué se repère : il rend deux fois la même chose. Un modèle qui
> **hallucine une structure différente et convaincante sur chaque entrée**, y compris sur des
> entrées qui ne peuvent pas porter d'encre, ne se repère par aucune inspection de sa sortie.
> C'est exactement ce que le papier fondateur ne mesure jamais, et c'est ce que `32` §4.3
> reprochait.

## 3 bis. ⚠⚠⚠ Ce témoin ne peut PAS encore répondre à la question typographique

Le résultat du 2026-08-28 sur `PHerc1447` ([`60`](60_la_constante_qui_rendait_le_modele_muet.md)
§4 quinquies) tient sur un contrôle par **mélange de pixels** : nos cartes portent des
fenêtres périodiques là où leurs propres pixels mélangés n'en portent aucune, p = 0,0007.

⚠ Le mélange est un contrôle **faible** : il détruit toute structure spatiale. Un témoin
négatif *réel* — une surface qui n'est pas une feuille mais qui garde la texture du volume —
pose une question bien plus dure : *nos cartes sont-elles périodiques là où une surface sans
feuille ne l'est pas ?*

**Mesuré, et la réponse est qu'on ne peut pas encore la poser :** au réglage calibré
(réduction 8, fenêtre 256), les deux témoins de 1100 × 1100 ne rendent qu'**une seule
fenêtre** chacun, et le test refuse à juste titre sous huit. Le positif lui-même — un segment
officiel sur une vraie feuille — rend **0 fenêtre périodique sur 1**, ce qui ne dit pas qu'il
n'est pas périodique mais que la question n'est pas posable sur une région aussi petite.

⭐ **L'expérience requise est donc nommée** : rendre un témoin négatif sur une région assez
grande pour porter au moins huit fenêtres au réglage calibré.

⚠⚠ **Et j'ai d'abord écrit « ~2100 × 2100 », ce qui est FAUX.** `par_fenetres` balaye
`range(0, dim - taille//2, taille)`, donc elle accepte une dernière fenêtre qui dépasse à
moitié — le compte n'est pas `dim/2048`. Vérifié contre une carte réelle
(`20250703034159`, 3620 × 5220 → 2 × 3 = 6 candidates, 4 retenues, ce que la mesure dit) :

| côté natif | réduit (8) | positions/côté | fenêtres |
|---:|---:|---:|---:|
| 1100 | 137 | 1 | **1** |
| 2100 | 262 | 1 | **1** |
| 3620 | 452 | 2 | 4 |
| **5200** | 650 | **3** | **9** |

Le seuil exact est **5128 × 5128** pixels de carte, pas 2100 (`src/encre/fenetres_par_region.py`, 11 contrôles). Se tromper de formule ici,
c'est dimensionner l'expérience décisive sur un nombre faux.

⭐ **Et elle est faisable** : les couches du témoin négatif font **5641 × 5721** (41 couches),
donc une région de 5200 y tient. Celles du contrôle positif ne font que **1200 × 1200**, mais
le positif n'est pas nécessaire à cette question-ci — ce qu'on demande est *le témoin négatif
est-il périodique*, contre son propre mélange, au réglage calibré et sans rien y changer.

⚠⚠ **Protocole déclaré avant de lancer, le 2026-08-28 à 05h55 :**

| issue | ce qu'on en conclura |
|---|---|
| le témoin négatif rend **0 fenêtre périodique** sur ≥ 8 | la périodicité de nos cartes n'est pas ce que ce détecteur produit sur n'importe quelle surface — le p = 0,0007 de `60` gagne un contrôle bien plus dur que le mélange |
| il en rend **autant que nos cartes** (~2/3) | la périodicité **n'est pas** une signature d'encre : elle apparaît là où la géométrie interdit une feuille, et le résultat de `60` doit être relu comme tel |
| entre les deux | on rapporte le taux et on ne conclut pas ; c'est un troisième chiffre, pas un demi-verdict |

⚠ Tant que cette mesure n'est pas faite, le p = 0,0007 de `60` reste ce qu'il dit —
*structuré là où son propre mélange ne l'est pas* — et rien de plus.

### ⭐ La référence « 95,4 % » est dérivée, pas choisie

Si deux cartes de même dispersion σ sont **indépendantes**, leur différence a un écart-type
σ√2, donc la médiane de sa valeur absolue vaut 0,6745·σ√2 = **0,9539·σ**. L'écart attendu
entre deux cartes sans rapport est donc proche de 1, et l'écart observé — 2,9 % — se lit
contre cette référence plutôt que contre un seuil.

⚠ Le témoin **vérifie la loi** plutôt que la valeur : deux cartes plates indépendantes
fabriquées sur place doivent s'écarter d'environ 0,954 de leur propre variation.

## 4. ⚠⚠ Le contrôle du contrôle : les deux fenêtres portent-elles de la matière ?

Deux prédictions identiques ont une explication ennuyeuse **avant** d'en avoir une
intéressante : si les deux fenêtres tombent hors des données, le modèle reçoit du noir deux
fois et rend deux fois la même constante. Ce serait une tautologie, et elle ressemblerait
exactement à un détecteur inerte.

| fenêtre reçue | moyenne | σ | part non nulle |
|---|---:|---:|---:|
| sur sa feuille — α = +0,00 | 89,45 | **39,26** | 93,4 % |
| en travers — α = +1,01 | 96,86 | **34,95** | 100,0 % |

⭐ **Les deux entrées sont pleines et distinctes** : leurs dispersions diffèrent de **11,0 %**,
et la figure montre deux textures qu'on ne confondrait pas — un tissage de fibres d'un côté,
des tranches coupées en biais de l'autre. L'explication ennuyeuse est écartée par la mesure,
pas par l'argument.

## 5. ⚠⚠ Quatre défauts d'instrument, tous les quatre à moi

1. ⚠⚠ **Le chemin d'impression du verdict était inatteignable.** « On n'a pas pu mesurer »
   et « on a mesuré, et ça ne conclut pas » partageaient la clé `raison`, donc le second
   sortait par le chemin d'erreur du premier : une ligne, un code de retour 1, **aucun JSON
   écrit**. Le cas où publier les chiffres compte le plus était exactement celui qui les
   jetait. Deux clés désormais, et un témoin qui exige qu'un résultat non concluant porte
   quand même ses deux mesures.

2. ⚠⚠ **Mon critère de « la même carte » était faux, et ce sont les témoins qui l'ont dit.**
   La première version demandait que l'écart médian soit petit devant l'échelle utile du
   modèle — critère que **deux cartes plates indépendantes satisfont**, puisqu'un petit écart
   *absolu* ne veut pas dire « la même carte », il veut dire « deux cartes plates ». Le bon
   dénominateur est la variation interne des cartes, et sa référence se dérive (§3).

3. ⚠⚠ **La figure peignait du hasard.** Les cartes portent **8784 pixels non finis** — un
   bord que le pas de balayage n'atteint pas — et une valeur non finie convertie en entier
   donne un octet arbitraire. Sur une figure dont toute la thèse est *« il n'y a pas de
   structure »*, c'est précisément l'artefact qui la contredirait.

4. ⚠ **Et mon premier remède se contredisait lui-même** : le commentaire annonçait une teinte
   « hors de la plage utile », et la valeur choisie — 0,5 — tombe au **milieu** de cette
   plage, donc au niveau le plus confusant possible. Aucun niveau de gris ne peut faire ce
   travail : il tombe forcément quelque part dans la rampe. Il faut une **couleur**, que la
   rampe ne peut pas produire, et le nombre de pixels concernés dans la légende.

> ⭐ Aucun des quatre n'a été trouvé en relisant le code. Deux viennent des témoins, un d'un
> avertissement du compilateur numérique, et le dernier d'avoir **regardé la figure**.

## 6. ⭐⭐ Ce que ça dit du point le plus profond du registre

[`29`](29_ce_qui_reste.md) §1 porte la question la plus fondamentale du dépôt — *réparer
une trace sert-il à quelque chose ?* — et nomme ce qu'il faudrait pour y répondre : **une
trace fautive, sa version réparée, et le MÊME aval appliqué aux deux**.

> ⚠⚠ **Sur `PHerc1447`, cet aval est aveugle, et c'est maintenant mesuré.** Le détecteur
> rend deux cartes étrangères (ρ = −0,010) mais également assurées sur une face de papyrus et sur une surface qui coupe
> l'empilement. Une différence de surface bien plus grande que celle entre une trace
> fautive et sa réparation ne le fait pas bouger — donc **aucune réparation ne peut
> montrer de gain à travers lui ici**, quelle qu'elle soit.

⭐ C'est une bonne nouvelle méthodologique : ça transforme « le lot 1 n'a pas abouti » en
« le lot 1 exige un rouleau où l'aval répond ». La condition est **nommable et
vérifiable avant de dépenser** — σ de la sortie du modèle sur le rouleau visé, rapporté
aux 0,7712 qu'il rend là où il marche. Ce document fournit la mesure ; elle coûte une
inférence sur une fenêtre.

## 7. Ce qui reste ouvert

- ⚠ **La thèse forte demande un rouleau où le détecteur fonctionne** — et une surface en
  travers de **ce** rouleau-là. Le dépôt a la seconde condition sur `PHerc1447`, où le
  modèle est inerte, et pas de trace à α élevé sur Scroll 1, où il marche. Ce n'est pas un
  obstacle de méthode, c'est un rendu à produire.
- ⚠ **Ce document n'établit pas qu'il n'y a pas d'encre là.** Il établit que ce modèle, sur
  ce rouleau, ne répond pas à ce qu'on lui donne. Laquelle des causes joue — la résolution,
  ce rouleau-ci, ou un papyrus réellement muet — reste ouverte, comme `36` le disait déjà.
- ⏳ L'instrument est réutilisable tel quel : deux cartes du même modèle, deux fenêtres
  d'entrée, et il dit à quelle portée la comparaison conclut.

## Reproduire

```bash
./src/outils/lancer.sh --fond src/campagnes/campagne_temoin_negatif.sh

# les témoins, hors ligne
uv run python src/encre/temoin_negatif.py --verifier
uv run python src/figures/figure_temoin_negatif.py --verifier
```

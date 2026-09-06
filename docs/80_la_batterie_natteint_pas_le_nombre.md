# 80 — Soixante-sept batteries vertes n'atteignent pas le nombre qu'elles publient

> ⚠⚠⚠ **Le 2026-09-05, un patch appliqué à moitié a laissé `derouler_des_deux_bords.py`
> avec un enregistrement qui référençait trois variables inexistantes — et la batterie est
> restée verte.** Elle testait ses briques une par une, jamais leur assemblage, et
> l'assemblage est exactement ce qui produit le nombre publié.

Ce document est la suite directe de [`61`](61_les_batteries_qui_ne_pouvaient_pas_echouer.md),
qui se terminait par la limite que celui-ci franchit : *« ce contrôle dit qu'une batterie
**peut** échouer, jamais qu'elle **teste** quelque chose d'utile »*.

![le chemin du nombre publié](images/80_le_chemin_du_nombre_publie.png)

## 1. Le défaut, et pourquoi il ne se voit pas

Une batterie verte sur un module dont le seul chemin non testé est celui qui produit le
nombre publié est une batterie **qui ne peut pas échouer là où ça compte**. C'est le cousin
du défaut de `61` — celle-ci *peut* échouer, mais pas sur ce qui compte — et il est plus
discret, parce que le verdict est vert **et sincère** : les contrôles écrits passent tous.

⚠ La raison pour laquelle il s'installe est mécanique et n'a rien à voir avec la
négligence : le chemin qui produit le nombre **lit le dépôt distant**. Il ne tourne donc pas
hors ligne, et `temoins.sh` exige que ses batteries tournent hors ligne — *« ni réseau, ni
volume distant, ni clé d'API, justement pour qu'aucune raison extérieure ne puisse les
empêcher de tourner »*. Le chemin le plus important du module était le seul qu'on ne pouvait
pas exercer.

## 2. ⭐⭐ Le balayage : la moitié du dépôt

`src/depot/le_chemin_du_nombre_publie.py` ferme le graphe d'appels de chaque module — ce que
`main` atteint, ce que `verifier` atteint — et rend la différence.

| | |
|---|---:|
| modules qui publient une mesure ou une figure | **152** |
| dont la batterie n'atteint pas ce chemin | **67** (44 %) |
| fonctions hors de portée, au total | **102** |

⚠⚠ **La portée a été resserrée en cours de route, et le premier chiffre publié était trop
large.** Ma première règle comptait comme publieur tout module *mentionnant* `docs/mesures` —
donc aussi ceux qui ne font que **lire** une mesure. Trouvé en voyant `le_corpus_des_spires.py`,
un pur lecteur, apparaître en dette pour la seule fonction qui lit le dépôt distant. Un lecteur
n'a pas de nombre publié, donc le défaut nommé ici ne peut pas lui arriver. Le signe retenu est
désormais l'**écriture**, sous ses deux formes : sérialiser **et** écrire un fichier (une
mesure), ou enregistrer une image (une figure). Exiger la première seule aurait effacé les
figures de la portée — or `dessiner` est la deuxième branche la plus souvent laissée dehors, et
c'est exactement le même défaut.

⭐ **Et la branche laissée dehors porte toujours le même nom.** Les têtes de chemin jamais
exercées, comptées par nom :

| branche | modules |
|---|---:|
| `mesurer` | **13** |
| `dessiner` | **10** |
| `rapporter` | 6 |
| `lire` | 4 |

Ce sont les deux verbes qui **publient** : l'un rend le nombre, l'autre l'image.

La dette n'est pas uniforme non plus — `graine` en porte 9 sur 10 et `encre` 23 sur 32, là où
`figures` n'en porte que 10 sur 50. `nappe`, la famille du déroulage, est passée de 15 à
**12 sur 29** en deux lots.

⚠ **Un chiffre a été retiré de la mesure après avoir été calculé** : « les modules dont la
tête de chemin est dehors », 67 sur 67. Ce n'est pas un constat, c'est une **identité** — la
couverture se propage vers le bas, donc si une fonction quelconque est hors de portée, celle
que `main` appelle en premier sur ce chemin l'est forcément. Un nombre qui ne peut prendre
qu'une valeur se lit comme une découverte et n'en est pas une.

## 3. Le remède, et un lecteur unique pour toute la famille

Le chemin de mesure reçoit désormais sa matière par paramètre, et le défaut par défaut est le
dépôt distant : **le nombre publié ne bouge pas d'une virgule.**

⭐ Et la lecture a été **promue** dès le deuxième appelant : `src/nappe/le_corpus_des_spires.py`
porte l'unique lecteur du corpus (l'index des spires, leur grille, l'écart inter-feuilles) et
l'unique fixture hors ligne. Cinq modules de `src/nappe/` en avaient chacun leur copie — et deux
dérouleurs comparés sur deux lectures différentes mesurent d'abord leur désaccord de lecture.

### ⭐⭐ La seconde matière : un volume fabriqué, seconde vue du même objet

Trois modules de la famille lisent **le volume brut** en plus des spires. Le seul point du
lecteur qui touche le monde — la requête — est devenu **injectable** ; tout le reste (les bornes,
le groupement par bloc, le cache, les reprises, la mémorisation d'une absence, l'interpolation)
est de l'arithmétique, et rien de tout ça ne pouvait tourner hors ligne.

⚠⚠⚠ **DEUX VUES D'UN MÊME OBJET, PAS DEUX OBJETS.** Un dérouleur lit les spires comme des
**surfaces** et le volume comme une **intensité**. Décrire l'objet deux fois ferait un corpus
dont les feuilles ne sont pas là où le volume les met : le raccrochage snapperait sur de la
matière qui contredit ses propres ancres, en rendant des nombres parfaitement stables et
absurdes. La géométrie est donc dite **une fois** (`geometrie_fabriquee`), et les deux vues la
lisent. L'intensité d'un voxel est **dérivée** de sa distance à la feuille la plus proche, jamais
dessinée.

Le contrôle qui lie les deux vues est celui sans lequel rien ne dirait qu'elles décrivent le même
objet : le gabarit lu **autour d'une spire** doit avoir sa crête sur **zéro**. Une sonde qui
décale le volume d'un demi-pas le fait tomber, et tout le reste de la mesure tournerait quand
même.

**Trois ronds-trips**, chacun injectant une grandeur connue et la relisant à travers la mesure :

| module | on injecte | la mesure rend |
|---|---|---|
| `le_raccrochage_a_la_matiere` | des feuilles à 135,5 µm | ne pas bouger coûte **136,3 µm** |
| `la_longueur_locale_du_pas` | des feuilles à 135,5 µm | longueur lue **136,1 µm** |
| `le_corpus_des_spires` | des feuilles à 61,2 voxels | pas entre crêtes **63,0** |

⚠ La tolérance est **dérivée**, pas choisie : deux feuilles voisines glissent chacune de son
amplitude d'ondulation et demie, donc leur écart local vaut le pas à **trois amplitudes** près.

⚠⚠ **Et le contrôle qui discrimine, pour la longueur locale** : un lecteur qui rendrait le centre
de sa fenêtre de recherche retrouverait AUSSI le nominal. On donne donc au volume un autre écart
que celui des spires — les spires ne disent que *où regarder* — et la lecture doit **suivre la
matière**. Elle ne la suit que partiellement, et c'est dit plutôt que caché : les ancres ne
tombent plus sur des crêtes, donc le gabarit n'est plus un profil de feuille. Ce qui est vérifié
est le **sens** du déplacement, pas son ampleur.

Les trois réponses du lecteur sont exercées elles aussi, et elles échouent différemment : une
**absence** se mémorise, un **incident** se réessaie, un incident qui **persiste lève**. Cette
logique avait été écrite après un incident réel — un délai dépassé a jeté deux cent trente-deux
blocs déjà téléchargés — sans qu'aucune batterie ne puisse l'exercer.

⚠⚠ **Ce qui est injectable est la MATIÈRE, pas le découpage.** La boîte, le seuil de
cellules, le choix des encadrements, le signe de la normale, la marche, la combinaison, la
pondération et l'enregistrement restent dans `mesurer`, donc restent couverts. Injecter un
corpus déjà découpé aurait fait sortir du test la moitié même de ce qu'on voulait tester.

⚠⚠⚠ **La fixture doit être ONDULÉE, et c'est le point le plus facile à rater.** Des spires
parfaitement décalées du pas sont atteintes **exactement** par un pas normal : toutes les
erreurs vaudraient zéro, et chaque comparaison de la batterie serait satisfaite par des
zéros. Une fixture sur laquelle la mesure ne peut rien trouver est le cas le plus pur d'un
contrôle satisfait pour la mauvaise raison. La phase de l'ondulation **tourne** d'une spire à
l'autre pour la même raison : en phase, c'est encore un décalage exact.

⚠ L'affichage a été sorti de `main`. Un bloc de `main` ne peut être exercé qu'en lisant le
dépôt distant, donc jamais par la batterie — et c'est précisément là que le patch de
septembre a laissé son enregistrement cassé.

**Ce que les batteries exercent désormais** — `derouler_des_deux_bords` (32 → **46
contrôles**) : la mesure de bout en bout (18 encadrements sur une matière fabriquée), ses deux
refus — une spire dont il ne reste que trois cellules est écartée, un corpus posé hors de la
boîte est **refusé** plutôt que rendu vide —, l'affichage jusqu'à son verdict, la sérialisation,
et la traçabilité dans l'autre sens : **la figure ne lit aucune clé que la mesure ne publie
pas**, les clés étant lues dans l'arbre syntaxique de la figure plutôt que recopiées à la main.

`derouler_par_le_pas_normal` (9 → **17 contrôles**) : la marche de bout en bout, le rétrécissement
du masque tour après tour, le **témoin du pas nul qui s'éloigne** — sans lui « le dérouleur
atteint la spire » serait satisfait par un dérouleur immobile —, et le refus d'une spire de
départ absente.

`le_corpus_des_spires` (**16 contrôles**) garde ce qui appartient à la matière elle-même : la
fixture a exactement la forme du vrai lecteur (clés lues dans l'arbre de `corpus_publie`), les
spires sont espacées du pas, **aucune n'est un décalage exact de sa voisine**, et le volume
fabriqué tombe sur les mêmes feuilles que le corpus.

`le_raccrochage_a_la_matiere` (46 → **54**), `la_longueur_locale_du_pas` (20 → **30**) et
`derouler_en_raccrochant` (63 → **75**) exercent chacun leur mesure de bout en bout, leur
affichage, et leur refus.

⚠⚠ Pour `derouler_en_raccrochant`, le **balayage de boîte** est exercé aussi — c'est lui qui a
rétracté une conclusion publiée, donc c'est le dernier endroit du module qu'on peut se permettre
de ne jamais lancer. Et le seul verdict vérifié sur la fixture est celui qui doit tenir sur
n'importe quelle matière : **un décalage tiré au hasard ne peut pas battre une méthode**. Quel
contendant gagne sur une fixture ne dit rien, et l'épingler ferait de la batterie une mesure de
la fixture.

### Les vingt-deux sondes

⚠⚠ Une batterie verte au premier essai ne prouve rien. Chaque défaut a été **remis** :

| défaut remis | ce que la batterie fait |
|---|---|
| fixture aplatie | rouge — *aucune spire n'est un décalage exact*, et la marche cesse d'être imparfaite |
| spires collées, plus d'espacement | rouge — *les spires sont espacées du pas* |
| la boîte ne découpe plus | rouge — *un corpus hors de la boîte est REFUSÉ* |
| le seuil de cellules ne filtre plus | rouge — *une spire de trois cellules est écartée* |
| le corpus publié gagne une clé | rouge — *la fixture a la forme du corpus publié* |
| l'affichage lit une clé renommée | rouge — `KeyError` rendu en contrôle nommé |
| la figure lit une clé absente | rouge — *la figure ne lit aucune clé absente* |
| la spire absente n'est plus refusée | rouge — *une spire de départ absente est refusée* |
| la demi-épaisseur devient l'épaisseur | rouge — *la demi-épaisseur est la moitié de l'écart lu* |
| le témoin du pas nul est figé | rouge — *le témoin s'éloigne tour après tour* |
| le volume est décalé d'un demi-pas | rouge — *le gabarit a sa crête sur la spire* |
| le volume a un autre pas que le corpus | rouge — *le pas entre crêtes est celui des spires* |
| un bloc loin rend du noir au lieu d'une absence | rouge — *l'absence est mémorisée* |
| une absence est réessayée comme un incident | rouge — *une absence n'est PAS réessayée* |
| un incident persistant devient une absence | rouge — *un incident qui persiste LÈVE* |
| la lecture rend le centre de sa fenêtre | rouge — *un volume plus écarté se lit plus long* |
| le témoin mélangé n'est plus mélangé | rouge — *le raccrochage bat son témoin* |
| le hasard n'est plus tiré au hasard | rouge — *le hasard est le pire de tous* |
| le balayage rend ses points à l'envers | rouge — *une boîte plus large contient plus* |

⚠ Une sonde a rendu un verdict **vert** et avait raison : « le corpus publié gagne une clé » ne
fait plus rougir `derouler_des_deux_bords`, parce que ce contrôle a déménagé chez le
propriétaire du corpus. Le dupliquer chez chacun de ses cinq appelants ferait cinq copies d'une
même exigence, libres de diverger.

### ⚠⚠ Deux de mes contrôles ne pouvaient pas échouer, et ce sont les sondes qui l'ont dit

**Un refus satisfait pour la mauvaise raison.** J'avais écrit, dans `la_longueur_locale_du_pas`,
« un corpus posé hors de la boîte est REFUSÉ » — en ne déplaçant que **les spires**. Le volume
fabriqué, lui, n'avait rien à lire là-bas, donc la mesure refusait pour **absence de matière** et
non parce que la boîte l'avait écartée : une sonde qui retirait le découpage laissait le contrôle
vert. Les deux matières sont désormais déplacées **ensemble** — les feuilles existent et se
lisent, elles sont seulement ailleurs que la boîte.

**Une inégalité large qu'une boîte inerte satisfaisait.** Dans le balayage de
`derouler_en_raccrochant`, « une boîte plus large ne contient jamais **moins** de cellules » est
satisfait par un découpage qui ne mord pas du tout — les deux points rendent alors le même
compte. La fixture débordant de la petite boîte, la comparaison est devenue **stricte** (20 contre
196 cellules), et la sonde tombe.

⭐ Les deux sont le même défaut de méthode : **un contrôle dont on n'a pas cherché par quelle
autre voie il pourrait passer au vert**. C'est pour ça que chaque batterie de ce lot a été
sondée, et pas seulement lancée.

## 4. ⚠⚠ Le second constat, trouvé en chemin : quarante-quatre batteries que rien ne lançait

En cherchant où inscrire la batterie corrigée, elle n'y était pas. Ni elle, ni quarante-trois
autres : `temoins.sh` rendait **184 batteries `ALL PASS`** sans les voir. Toute la campagne de
déroulage et ses figures étaient dans ce cas.

⭐ Le garde-fou qui les nomme existait déjà dans `temoins.sh` (*« batteries non lancées »*) —
il n'avait simplement pas tourné depuis, le harnais complet étant long. Un contrôle qu'on ne
lance pas est, pour la durée où on ne le lance pas, exactement un contrôle absent.

Les quarante-quatre ont été lancées **une par une avant d'être inscrites** : toutes vertes, la
plus lente en soixante secondes. Les inscrire sans les avoir lancées aurait fait rougir le
harnais entier sur un défaut qu'on n'aurait pas nommé.

## 5. Portée, dite plutôt que sous-entendue

⚠ **Une fonction atteinte n'est pas une fonction testée.** Ce balayage dit qu'une batterie la
**traverse**, jamais qu'elle y vérifie quoi que ce soit. Prendre l'un pour l'autre ferait de
cet instrument la mesure trop confiante qu'il traque.

⚠ **Le graphe ne suit que les appels par nom.** Un appel indirect — passé en argument, résolu
par un dictionnaire — n'est pas vu, donc une fonction peut être comptée dehors alors qu'elle
tourne. L'erreur va dans le sens prudent : la dette est **surestimée**, jamais cachée.

⚠ **La portée est les modules qui publient une mesure.** Un script qui ne publie rien peut
laisser du code hors de sa batterie sans que ce soit la faute nommée ici, et l'y compter
gonflerait le chiffre avec des cas qui ne sont pas celui-là.

## Reproduire

```bash
uv run python src/depot/le_chemin_du_nombre_publie.py             # le balayage
uv run python src/depot/le_chemin_du_nombre_publie.py --verifier  # ses propres contrôles
uv run python src/nappe/derouler_des_deux_bords.py --verifier     # 47 contrôles, hors ligne
uv run python src/figures/figure_le_chemin_du_nombre_publie.py \
    --sortie docs/images/80_le_chemin_du_nombre_publie.png
```

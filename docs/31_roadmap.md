# Roadmap — ce qu'il faudrait pour finir, et par où passer

2026-08-19. Écrit après la lecture intégrale des **quatre** articles primaires, de la
carte technique officielle, de l'écosystème d'outils, et des 34 documents de ce dépôt.
C'est une proposition, pas un plan validé : chaque étape porte ce qui la rend possible et
ce qui pourrait la tuer.

⚠ **Une roadmap est le genre de document qui vieillit le plus vite et se relit le moins.**
Celle-ci s'appuie sur des mesures datées ; quand l'une tombe, l'étape qu'elle porte tombe
avec. Les dépendances sont donc écrites, pas implicites.

---

## 1. Où est l'argent, et lequel est atteignable

| prix | montant | ce qu'il faut | atteignable ? |
|---|---:|---|---|
| **Progress Prize** | **20 000 $/mois** | la meilleure contribution open source du mois | ⭐⭐⭐ **oui, tout de suite** |
| **First Letters** | **50 000 $ × 10** | **10 lettres dans UNE zone de 4 cm²**, sur un rouleau où personne n'a rien lu | ⭐⭐ **oui, c'est la cible** |
| Titre de PHerc. Paris 4 | 50 000 $ | l'image du titre | ⭐ peut-être — c'est un problème de *où chercher* |
| **Grand Prize** | **800 000 $** | **100 %** du recto d'un rouleau, ≤ **8 h** d'annotation humaine | ❌ **pas nous, pas seuls, pas en dix mois** — voir §7 |

⭐⭐ **Le calcul qui décide de la stratégie** : le Grand Prize demande 100 % d'un rouleau
avec 8 h d'humain, quand l'état de l'art vient d'en faire un avec **775 h** (`27` §3).
Facteur ~100. First Letters demande **4 cm²** — et `24` a tracé **8,48 cm² en 13,9
secondes**. Ce ne sont pas deux difficultés du même ordre ; ce sont deux problèmes
différents.

> **La stratégie tient en une phrase : viser les dix First Letters, et laisser le Grand
> Prize émerger de ce qui aura été construit pour eux — ou pas.**

## 2. Le mur de la résolution — et pourquoi il ne ferme PAS First Letters

C'est le premier réflexe après avoir lu `27` §1, et il est faux.

| | résolution |
|---|---|
| cible de la voie **topographique** (`27` §1) | **~1 µm** |
| scan de production ESRF/BM18 de `27` §3 | 2,4 µm |
| **les 13 rouleaux du prix** | **8,64–9,36 µm** |
| ⭐ **le scan sur lequel le Grand Prize 2023 a été GAGNÉ** | **7,91 µm** |

⭐⭐ **La dernière ligne est celle qui compte.** Le texte de Scroll 1 a été lu à 7,91 µm,
par un modèle appris. Les rouleaux du prix sont à 8,64–9,36 µm — **10 à 18 % plus
grossier**, pas un facteur. La cible de 1 µm de `27` §1 vaut pour la détection **par le
seul microrelief**, sans modèle ; elle ne borne pas un détecteur appris sur du CT, qui
exploite autre chose.

⚠ **Ce qui reste vrai du mur** : voir l'encre *directement dans le rendu, sans modèle* —
ce que le règlement autorise explicitement — est bien hors de portée à 9 µm. Il faudra
donc un **modèle**, et donc une **surface assez bonne pour qu'il ait quelque chose à
lire**. Ce qui ramène au vrai goulot, qui est géométrique.

## 3. ⭐⭐⭐ Le levier découvert le 2026-08-19 : le traceur est un **tirage**

Mesuré ce soir, et c'est ce qui réoriente tout le reste (`30`).

La graine de `24` — celle qui a donné **240 auto-intersections** — rejouée avec **les
mêmes paramètres** rend **zéro**, plusieurs fois de suite. Le maillage archivé, lui,
remesure bien 240 aujourd'hui : **la mesure est fidèle, c'est le traceur qui est
instable.** Et un run rend **8,475839 cm²** contre **8,476817** pour l'archivé — soit
**0,01 % d'écart d'aire, et deux verdicts opposés.**

> **La différence entre une trace condamnée et une trace propre n'est pas dans les
> paramètres. Elle est dans le tirage.**

⭐⭐ **Conséquence stratégique, et c'est le cœur de cette roadmap :**

| fait | conséquence |
|---|---|
| une trace coûte **~14 s** | on peut en tirer beaucoup |
| notre juge coûte **0,05 s** et n'exige **aucune vérité terrain** | on peut toutes les juger |
| la qualité est un **tirage** | **échantillonner et sélectionner est une méthode, pas un bricolage** |

**Personne ne fait ça, et pour une raison précise : personne n'a de juge assez bon
marché.** L'équipe du concours corrige à la main (`27` §3) ; les outils communautaires
jugent *après coup* un maillage qu'on a déjà décidé de garder (`28`).

⚠⚠ **Et le piège qui va avec, à traiter dès la conception : la malédiction du
vainqueur.** Sélectionner le minimum de N tirages avec un juge bruité fait remonter la
chance autant que la qualité. Le protocole honnête est donc : **sélectionner sur un axe,
valider sur l'autre.** Nous avons exactement deux axes indépendants (§4), ce qui rend ce
protocole possible — c'est une chance, pas une élégance.

## 4. ⭐⭐ L'instrument qui n'existe nulle part : le **désaccord** entre deux axes

C'est la proposition technique centrale, et elle sort de `28`.

| axe | ce qu'il voit | ce qu'il **ne peut pas** voir |
|---|---|---|
| **géométrie** — auto-intersection (`vc_tifxyz_selfcross`, `03`) | une surface qui se traverse : un défaut **sans lecture innocente, sans seuil à débattre** | ⚠ *« no geometry-only test can separate [a one-wrap switch] from bending »* — l'auteur de `tifxyz-surgeon`, mesuré : l'écart inter-spires (18–58 vx) est à peine plus large qu'une cellule de grille (20 vx) |
| **volume** — notre instrument de profondeur (`12`) | où est **réellement** la matière le long de la normale, sans vérité terrain | ⚠ en zone **comprimée**, l'information n'est pas dans le CT : 78 % de pics uniques larges couvrant **deux** feuilles (`villa#191`) |

⭐⭐⭐ **Chacun est aveugle là où l'autre voit. Et leur DÉSACCORD est le signal que ni l'un
ni l'autre ne porte seul :**

> Un endroit où la **géométrie dit propre** et où le **volume dit que le pic de matière
> est à une distance inter-feuilles** est exactement la panne que Henderson nomme —
> *« the surface **wanders between two true windings**, instead of committing to one »* —
> et qu'**aucun test géométrique n'attrape**.

**Pourquoi c'est faisable ici et pas ailleurs** : il faut les deux instruments, et il faut
que le second n'exige pas de vérité terrain. Nous avons les deux. `27` §2 montre que la
seule métrique de saut de spire publiée (WJF) **exige un maillage de référence** — donc
elle est inapplicable aux treize rouleaux du prix, dont **aucun** n'en a.

**La forme du test, sans seuil à régler** : l'unité n'est pas le micromètre, c'est
**l'écart inter-feuilles du rouleau**, que `16` et `17` mesurent déjà rouleau par rouleau.
Un pli donne une dérive **lisse** du champ de profondeur le long de la surface ; un saut
donne une **marche d'une unité**. C'est la dérivée qui discrimine, et son unité naturelle
rend le seuil sans objet — c'est très exactement la forme que le concours a acceptée en
24 heures et refusée deux fois autrement (`28` §5).

## 5. ⭐⭐ La correction : un **gauchissement difféomorphe** piloté par la mesure

C'est le lot nº 2 de `29`, et il a maintenant une forme mathématique.

**Ce qui est acquis** : `20` a mesuré que l'erreur d'une trace est **structurée** et que
**translater ne la répare pas**. Le remède est donc un gauchissement.

**Le danger évident** : déplacer chaque sommet le long de sa normale d'une quantité
mesurée et bruitée **crée** des auto-intersections — on fabriquerait le défaut qu'on
prétend enlever.

⭐⭐ **La parade est déjà écrite, dans un papier qu'on vient de lire.** Henderson
paramètre sa déformation comme l'**intégrale d'un champ de vitesse lisse**, ce qui la
rend **difféomorphe par construction** : *« the space of flow fields is the Lie algebra
that generates the Lie group of diffeomorphisms »*. Un difféomorphisme ne peut ni
déchirer, ni recoller, ni replier — donc **il ne peut pas créer d'auto-intersection.**

> **La combinaison est neuve** : il pilote cette machinerie par un **a priori global** (la
> spirale) et des prédictions de réseau ; nous la piloterions par une **mesure locale
> directe du volume**. Même garantie, source d'information différente — et la nôtre ne
> demande pas de vérité terrain.

⚠ Trois choses à vérifier avant d'y croire, dans cet ordre :
1. l'intégration discrète **ne préserve pas** la garantie gratuitement — Henderson le dit
   lui-même (*« fewer [steps] could cause … not [to] be sufficiently close to the identity
   »*). Il faut borner le pas ;
2. le champ de profondeur est bruité : il faut le **régulariser**, et la régularisation
   est exactement ce qui peut effacer le signal qu'on veut appliquer ;
3. ⚠⚠ et surtout : **rien ne prouve encore que corriger serve à quelque chose** (§6).

## 6. ⭐⭐⭐ La question qui commande tout, et qui n'est pas au bout de la chaîne

> *« Une surface propre donne un meilleur texte » est une affirmation **sur le pipeline**,
> et **elle n'est pas prouvée. »* — `03`:137

**Aucun étage de cette roadmap n'a de valeur si la réponse est non.** Et ce n'est pas une
faiblesse locale : `28` montre que l'équipe du concours **ne publie aucun taux d'erreur de
traçage**, ni avant ni après correction. Personne n'a mesuré ce que coûte un défaut.

**Le dessin d'expérience est à notre portée, et il est apparié** :

1. prendre un segment **publié** de Scroll 1 (corpus où tout marche : 80 segments, cartes
   d'encre publiées, modèle qui tourne) ;
2. en produire deux versions — l'originale, et la **gauchie** par §5 ;
3. rendre les deux, passer le **même** modèle d'encre, comparer l'AUC contre la **même**
   carte publiée.

⚠ Le contrôle qui rend la mesure honnête : un **gauchissement nul** et un **gauchissement
aléatoire de même amplitude**. Sans eux, tout gain se lit comme un succès alors qu'il peut
n'être qu'une perturbation qui aide par hasard.

> ⭐ **Que la réponse soit oui ou non, c'est publiable.** Un « non » mesuré est un résultat
> que personne n'a, et il redirige tout le domaine. C'est exactement le genre de
> contribution que les Progress Prizes récompensent — *« amélioration quantitative sur
> données réelles »* et *« documentation qui permet à d'autres d'appliquer le travail »*.

## 7. Le Grand Prize — l'évaluation honnête

**Ce qu'il demande** : 100 % du recto d'un rouleau, 70 % des caractères lisibles sans
interpolation papyrologique, pipeline automatisé, **≤ 8 h** d'annotation humaine
documentée.

**Ce qui sépare l'état de l'art de ça** :

| obstacle | mesuré | qui peut le lever |
|---|---|---|
| **775 h → 8 h** d'annotation | `27` §3 | un traçage automatique fiable — le problème ouvert nº 1 du domaine |
| la **qualité des étiquettes** est *« one of the main unwrapping bottlenecks »* | page officielle | des annotateurs experts, du temps, une infrastructure |
| en zone comprimée **l'information n'est pas dans le CT** | 78 % de pics fusionnés | **un rescan plus fin** — donc du temps de synchrotron |
| le prédicteur de surface a un **Dice de 0,308** | `27` §3 | de l'entraînement à grande échelle |

⚠⚠ **Trois de ces quatre lignes ne sont pas des problèmes d'algorithme.** Ce sont du temps
de faisceau, des heures d'annotateurs experts, et des GPU. Un projet solo avec un iGPU
n'en lève aucune.

> **Verdict honnête : le Grand Prize n'est pas atteignable par ce projet seul d'ici juin
> 2027.** Ce qui l'est, c'est de fournir **la pièce qui manque à ceux qui peuvent** — la
> détection conservatrice de panne, que la page officielle réclame nommément et que
> personne n'a. Et si cette pièce marche, elle vaut une **place au classement** du Grand
> Prize (100 000 $ / 50 000 $ / 50 000 $) sans avoir à tout faire soi-même.

## 8. Le calendrier proposé

| quand | quoi | pourquoi maintenant |
|---|---|---|
| **avant le 31 août** | soumettre le Progress Prize | ⚠ échéance dans 12 jours, le texte existe (`21`), il manque **le dépôt publié** et les figures. ⚠⚠ Et `15` se déclare **périmé sur deux points** : à refaire avant l'envoi, pas après |
| **septembre** | §6 — *corriger sert-il à quelque chose ?* | c'est le socle ; tout le reste en dépend, et le résultat est publiable dans les deux sens |
| **septembre** | §3 — l'échantillonnage : N tirages, sélection sur un axe, validation sur l'autre | bon marché, et le levier est déjà mesuré |
| **octobre** | §4 — l'instrument de désaccord | c'est la contribution que le concours nomme, et elle a besoin des deux axes en place |
| **oct.–nov.** | §5 — le gauchissement difféomorphe | dépend de §6 : si corriger ne sert à rien, cette étape n'existe pas |
| **nov.–févr.** | **campagne First Letters** sur les 10 rouleaux sans lecture | c'est là qu'est l'argent atteignable, et ça consomme tout ce qui précède |
| **en continu** | un Progress Prize par mois | 20 000 $/mois, et c'est ce qui finance l'attention du jury |

⭐ **L'ordre n'est pas négociable sur un point** : §6 avant §5. Construire un correcteur
avant de savoir si corriger sert à quelque chose, c'est exactement ce que ce dépôt
s'interdit.

## 9. Ce qu'on ne peut pas faire, et qu'il faut cesser d'espérer

- **Rescanner** quoi que ce soit — le temps de faisceau ESRF ne s'achète pas.
- **Entraîner un gros modèle** — un iGPU Arc n'est pas un H100. Ce qui est à notre portée :
  faire tourner les modèles publiés, et mesurer.
- **775 heures d'annotation** — ni le temps, ni l'expertise papyrologique.
- ⚠ **Lire du grec** — le cap du jugement expert (`29` §3) ne se contourne pas. Trois juges
  mécaniques ont déjà échoué, dont un **définitivement** (un segment de ce type ne porte
  que 4 à 5 lignes, et les glyphes fusionnent au seuil du modèle).

## 10. ⚠ Les trois façons dont cette roadmap peut se tromper

1. **Si §6 rend « corriger ne change rien »**, les §4 et §5 perdent leur justification
   *pratique* — ils restent des mesures, ils cessent d'être une voie vers un prix. La
   roadmap bascule alors entièrement sur la **sélection** (§3), qui ne suppose rien.
2. **Si l'encre est illisible à 9 µm même avec un modèle**, First Letters se ferme et il ne
   reste que les Progress Prizes. ⭐ **C'est la première chose à mesurer** : passer le
   modèle du Grand Prize 2023 sur un rendu de rouleau du prix et regarder. Coût : une
   trace, un rendu, une inférence. **Cette mesure devrait passer avant tout le reste de
   cette roadmap.**
3. **Si le tirage de §3 n'a pas la variance qu'on croit** — cinq runs propres ne font pas
   une distribution. `30` la mesure sur vingt ; si la queue est trop rare pour être
   exploitée, l'échantillonnage devient un coût sans gain.

# 50 — Le rendu n'attendait pas le calcul, il attendait la mémoire

2026-08-23. Ce document est né d'une question simple posée sur un rendu qui durait :
*est-ce que le programme est optimisé, pour justifier le temps qu'il prend ?* La réponse
mesurée est non, et la cause n'était pas dans le programme — elle était dans nos arguments.

---

## 1. ⚠⚠ Ce que la machine faisait pendant qu'on croyait qu'elle calculait

Relevé sur le processus vivant, après 1 h 58 de rendu d'une surface de 3,656 cm² :

| grandeur | mesure |
|---|---|
| RSS du processus | **28,2 Go** sur 31,8 de RAM |
| mémoire libre | **274 Mo** |
| cache de pages du noyau | écrasé à **442 Mo** |
| swap occupé | **3,4 Go** |
| CPU moyen | **23,7 % d'un cœur** |
| cœurs disponibles | **22** |
| threads du processus | **59** |

> ⭐⭐⭐ Un processus à cinquante-neuf threads qui consomme un quart d'un cœur sur une
> machine qui en a vingt-deux **ne calcule pas** : il attend la mémoire. Les six heures que
> le renderer annonçait n'étaient pas du travail, c'était du swap.

⚠ Le journal du renderer disait `band 14/63 (22%) · 112m02s · eta 392m09s`. Cette ETA était
sincère et sans valeur : elle extrapolait un rythme qui n'était limité par rien de ce que le
programme faisait.

---

## 2. La cause est dans nos propres arguments

```
--cache-gb arg (=16)    Zarr chunk cache size in GB
```

⚠⚠ **Le cache de chunks vaut 16 Go par défaut** — la moitié de la RAM de cette machine.
Et **aucun des 28 appels à `vc_render_tifxyz` de ce dépôt, répartis sur 14 scripts, ne
réglait cette valeur.**

> ⚠ **Correction d'une première lecture.** J'ai d'abord écrit que « la cause, c'est
> `--cache-gb 16` ». L'étalonnage dit : *à moitié*. Sur la petite surface le pic sature à
> **4,53 Go même à `--cache-gb 16`** — le cache est alloué **paresseusement** et ne se
> remplit qu'à hauteur de ce que la surface touche. Ce n'est donc pas un plafond qu'on
> *paie*, c'est un plafond qu'on **atteint** quand la surface est assez grande.

C'est l'exacte forme d'un réglage qui attend son heure : inoffensif à toutes les tailles
qu'on avait essayées, décisif à la première qui compte.

---

## 3. ⭐⭐ L'arithmétique ferme, et c'est ce qui rend le diagnostic vérifiable

Un diagnostic plausible et un diagnostic vrai se ressemblent. Celui-ci se recoupe :

L'en-tête TIFF du rendu **terminé** de la petite surface donne **2361 × 2341** pixels pour
0,317 cm². Le rapport d'aire avec la grande est exact — 3,656 / 0,317 = **11,5×** — et une
surface aplatie est rendue à résolution fixe, donc la grande fait **64 Mpx par tranche**.

| | par tranche | × 41 tranches | × 161 tranches |
|---|---|---|---|
| tampons `float32` | 64 Mpx | **9,7 Go** | **38,2 Go** |
| cache de chunks (défaut) | | 16 Go | 16 Go |
| **total attendu** | | **25,7 Go** | **54,2 Go** |
| **observé** | | **28,2 Go** | — |

⚠ L'en-tête a dû être lu à la main : un décodeur d'image refuse un fichier tronqué, et les
tranches du grand rendu sont **pré-allouées puis abandonnées** (leur offset d'IFD vaut zéro,
parce que le renderer écrit son index à la fin). « Illisible » et « inachevé » sont deux
états différents et il faut les nommer séparément.

---

## 4. ⚠⚠ La conséquence : la fenêtre profonde ne rentre pas

α se lit à **deux** profondeurs. La seconde fenêtre fait 161 couches, soit **38,2 Go de
tampons à elle seule** sur une machine de 31,8 — **quel que soit `--cache-gb`**.

> Ce n'était donc pas une mesure lente, c'était une mesure **impossible**. On aurait attendu
> une journée et demie un résultat qui ne pouvait pas arriver.

C'est une panne qu'aucune relecture du script n'aurait trouvée, parce que le script est
correct : c'est la taille de l'objet qui a changé, et rien ne rapportait la taille.

---

## 5. L'étalonnage, et ce qu'il refuse de faire

`tools/etalonner_rendu.sh` rend **la même surface, la même fenêtre**, en ne changeant que
`--cache-gb`, et relève le temps de mur et le pic de RSS.

⚠⚠ **Le cache disque est chauffé une fois avant la série.** Sans cela, le premier essai
paie le téléchargement du volume et sort du lot pour une raison étrangère au réglage
mesuré — c'est « comparer une grandeur à elle-même » en costume de banc d'essai.

⚠⚠ **Et la première chose vérifiée n'est pas une performance : c'est que la sortie ne bouge
pas.** Chaque essai est empreint (`sha256` de la pile de tranches), et
`analysis/src/effet_du_cache.py` **refuse de parler de vitesse** si les empreintes diffèrent.
Un réglage qui change les pixels n'est pas un réglage de performance — ce serait découvrir
que tous les rendus déjà publiés dépendaient d'une valeur que personne n'avait posée.

⭐ **Le critère n'est pas « le plus rapide » mais « le plus petit à moins de 5 % du
meilleur ».** Prendre le plus rapide choisirait presque toujours le plus gros cache, donc
reconduirait exactement le défaut qu'on est en train de corriger.

⚠⚠ **Et chaque valeur est répétée trois fois** — leçon que ce dépôt avait déjà écrite
ailleurs (`tools/campagne_thread_limit.sh` : *« une seule exécution par valeur ne
distinguerait pas l'effet du réglage de la variance de run »*). Elle vaut double ici : le
répertoire passé à `-v` reste **vide**, donc le cache disque n'est jamais matérialisé et
chaque essai retélécharge — le chronomètre porte autant le réseau que le réglage.

### Le résultat, 15 rendus

![ce que coûte le cache de chunks](images/50_etalon_rendu.png)

| `--cache-gb` | temps médian | étendue | pic RSS médian |
|---|---|---|---|
| **1** | **71 s** | 13,1 s | **1,81 Go** |
| 2 | 110 s | **61,7 s** | 2,98 Go |
| 4 | 118 s | 21,9 s | 4,36 Go |
| 8 | 141 s | 23,8 s | 4,53 Go |
| 16 (défaut) | 135 s | 22,6 s | 4,52 Go |

> ⭐ **`--cache-gb 1`** : le pic le plus bas *et* la médiane la plus basse. Les **quinze
> sorties sont identiques** au `sha256` — donc plafonner ne déplace aucun résultat déjà
> publié, et c'est cette vérification-là qui autorise à poser le réglage dans le chemin
> commun (`tools/rendre_surveille.sh`).

⚠ **La conclusion sur le temps penche, elle ne tranche pas.** L'écart entre valeurs (70,3 s)
ne dépasse l'étendue à l'intérieur d'une valeur (61,7 s, à `--cache-gb 2`) que d'un facteur
**1,14** — le dépouilleur le signale plutôt que de rendre un « concluant » nu, parce qu'une
marge mince se lit exactement comme une conclusion solide. **La mémoire, elle, tranche** :
1,81 contre 4,53 Go, avec des étendues de quelques centièmes.

### Ce que le plafond change pour la grande surface

| | mémoire attendue |
|---|---|
| fenêtre 41 au défaut | 25,7 Go — **swap** |
| fenêtre 41 à `--cache-gb 1` | **10,7 Go** — tient |
| fenêtre 161 à `--cache-gb 1` | 39,2 Go — **ne tient pas** |

⭐ La fenêtre superficielle devient donc mesurable. La profonde reste hors d'atteinte au
niveau 0, et c'est la pyramide qu'il faut interroger — voir §6.

---

## 6. Ce que ce document n'établit pas

- ⚠ **Que la pyramide sauve la fenêtre profonde.** Le volume a six niveaux (`-g 0` à `-g 5`)
  et `-g 1` diviserait les pixels par quatre, ce qui ferait tenir les 161 couches. Mais α
  est un **rapport** entre deux profondeurs : une réduction uniforme *ne devrait pas* le
  biaiser, et « ne devrait pas » n'est pas « mesuré ». [`35`](35_le_tirage_sur_douze_rouleaux.md)
  a déjà établi qu'un seuil calé sur le niveau 0 ne se transporte pas à résolution réduite.
  Le contrôle est bon marché et il reste à faire.
- ⚠ **Que 16 Go soit un mauvais défaut en général.** Sur une machine à 128 Go il est sans
  doute raisonnable. Ce qui est mesuré ici, c'est qu'un défaut dimensionné pour une autre
  machine est un défaut, et qu'on ne l'avait jamais posé.

## Reproduire

```bash
tools/etalonner_rendu.sh                       # 5 valeurs × 3 répétitions
python3 analysis/src/effet_du_cache.py --json docs/etalon_rendu.json
cd inference && uv run python ../analysis/src/figure_etalon_rendu.py \
    --json ../docs/etalon_rendu.json --sortie ../docs/images/50_etalon_rendu.png \
    --projection "fenêtre 41 au défaut=25.7" \
    --projection "fenêtre 41 à --cache-gb 1=10.7" \
    --projection "fenêtre 161 à --cache-gb 1=39.2"
tools/controle_resolution.sh                   # la pyramide préserve-t-elle α ?

# les témoins, hors ligne
tools/etalonner_rendu.sh --verifier
tools/controle_resolution.sh --verifier
tools/rendre_surveille.sh --verifier
python3 analysis/src/effet_du_cache.py --verifier
cd inference && uv run python ../analysis/src/figure_etalon_rendu.py --verifier
```

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
| modules qui publient une mesure | **140** |
| dont la batterie n'atteint pas ce chemin | **67** (48 %) |
| fonctions hors de portée, au total | **104** |

⭐ **Et la branche laissée dehors porte toujours le même nom.** Les têtes de chemin jamais
exercées, comptées par nom :

| branche | modules |
|---|---:|
| `mesurer` | **17** |
| `dessiner` | **10** |
| `rapporter` | 7 |
| `lire` | 4 |

Ce sont les deux verbes qui **publient** : l'un rend le nombre, l'autre l'image.

La dette n'est pas uniforme non plus — `graine` en porte 9 sur 10 et `encre` 22 sur 29, là où
`figures` n'en porte que 10 sur 46.

⚠ **Un chiffre a été retiré de la mesure après avoir été calculé** : « les modules dont la
tête de chemin est dehors », 67 sur 67. Ce n'est pas un constat, c'est une **identité** — la
couverture se propage vers le bas, donc si une fonction quelconque est hors de portée, celle
que `main` appelle en premier sur ce chemin l'est forcément. Un nombre qui ne peut prendre
qu'une valeur se lit comme une découverte et n'en est pas une.

## 3. Le remède, sur le premier module

Le chemin de mesure de `derouler_des_deux_bords.py` reçoit désormais sa matière par
paramètre, et le défaut par défaut est le dépôt distant : **le nombre publié ne bouge pas
d'une virgule.**

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

**Ce que la batterie exerce désormais** : la mesure de bout en bout (18 encadrements sur une
matière fabriquée), ses deux refus — une spire dont il ne reste que trois cellules est
écartée, un corpus posé hors de la boîte est **refusé** plutôt que rendu vide —, l'affichage
jusqu'à son verdict, la sérialisation, et la traçabilité dans l'autre sens : **la figure ne
lit aucune clé que la mesure ne publie pas**, les clés étant lues dans l'arbre syntaxique de
la figure plutôt que recopiées à la main.

### Les six sondes

⚠⚠ Une batterie verte au premier essai ne prouve rien. Chaque défaut a été **remis** :

| défaut remis | ce que la batterie fait |
|---|---|
| fixture aplatie | rouge (`mesurer` lève avant même le contrôle) |
| la boîte ne découpe plus | rouge — *un corpus hors de la boîte est REFUSÉ* |
| le seuil de cellules ne filtre plus | rouge — *une spire de trois cellules est écartée* |
| le corpus publié gagne une clé | rouge — *la fixture a la forme du corpus publié* |
| l'affichage lit une clé renommée | rouge — `KeyError` rendu en contrôle nommé |
| la figure lit une clé absente | rouge — *la figure ne lit aucune clé absente* |

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

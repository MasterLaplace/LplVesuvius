# 122 — La re-course est écrite, testée, et pas lancée

> ⭐⭐⭐⭐ **`R4-P24` A MAINTENANT UN MÉCANISME, ET IL FAIT CE QU'ON LUI DEMANDE SUR UNE PILE DONT
> LA RÉPONSE EST CONNUE.** Sur un empilement dont le pas rétrécit de 173 µm à mesure qu'on
> s'enfonce : la fenêtre **fixe** se met **3 fois en butée** et confirme **21 pas sur 26** ; la
> fenêtre **locale** n'est **jamais en butée** et confirme **26 sur 26**, en descendant à
> **50,0 µm** — sous le bout court de la fenêtre fixe, qui est à **86,5 µm**.
>
> ⭐⭐⭐ **ET RIEN N'EST RECALIBRÉ**, parce que `121` l'a mesuré : le nul par candidat est
> invariant par changement d'échelle. La fenêtre reçue est **vérifiée** être celle de la
> calibration, et un refus vaut mieux qu'une barre fausse.
>
> ⭐⭐ **Le plafond de la re-course est DÉRIVÉ, pas choisi** : traverser 4,07 → 23,8 mm à
> l'espacement médian publié de 177 µm demande **112 pas**. `113` a levé son plafond de 6 à 20 et
> 28 marches sur 28 l'ont touché ; un plafond qu'on choisit est un budget, et il se republie en
> portée.
>
> ⚠⚠ **ELLE N'EST PAS LANCÉE.** La faire tourner demande des lectures distantes sur des heures,
> et c'est une décision de l'auteur, pas une conséquence de l'avoir écrite.

## 1. Ce que la re-course doit porter, et d'où chaque pièce vient

| pièce | d'où elle vient |
|---|---|
| fenêtre recentrée sur l'espacement local | `117` (63 pas refusés par la fenêtre), `118` (les deux bouts sont de vrais pas, la variation n'est pas radiale) |
| à **largeur constante** | `121` (recentrer laisse le nul inchangé à 2,6·10⁻¹⁶ ; élargir le déplace de 1,2 σ) |
| arrêt au premier pas aveugle | `116` (la cécité est absorbante : aucune des 11 marches qui cessent de lire ne relit) |
| plafond dérivé de la géométrie | `113` (28 marches sur 28 au plafond, donc la portée est censurée) |

⚠ Les deux options **défaillent à l'ancien comportement**. En faire les défauts changerait ce que
toute marche déjà publiée mesure ; c'est la règle que ce fichier suit déjà pour `selecteur`, où le
défaut `"calibre"` garde les chiffres publiés et `"deux_roles"` prend le sélecteur corrigé.

## 2. ⚠⚠ La garde qui rend le recentrage légitime

`121` autorise le recentrage **parce que** le nul ne dépend que des rapports des longueurs à la
plus longue. Cette autorisation ne vaut que si la largeur ne bouge pas. Le marcheur **vérifie donc
la fenêtre qu'on lui donne** : elle doit être exactement `candidats_de_pas(nominal)`, sinon il
refuse.

⚠ Un refus vaut mieux qu'une barre fausse : réutiliser `mu`/`sd` sur une fenêtre élargie
remettrait le biais vers les courts que `nul_par_candidat` existe pour tuer, et la mesure aurait
l'air d'une mesure.

## 3. ⭐⭐⭐⭐ La démonstration, sur une pile dont la réponse est connue

| | pas | en butée | confirmés | pas minimal | échelle minimale |
|---|---:|---:|---:|---:|---:|
| fenêtre **fixe** | 26 | **3** | **21** | 86,5 µm | 1,000 |
| fenêtre **locale** | 26 | **0** | **26** | **50,0 µm** | **0,278** |

La pile a un pas qui décroît de **0,04 µm par micromètre** parcouru. La fenêtre fixe finit par
demander un pas que ses candidats ne savent pas exprimer ; la locale suit.

⚠⚠ **C'est une démonstration ANALYTIQUE, pas une re-course.** Elle ne touche aucun volume et ne dit
rien du vrai rouleau. Ce qu'elle établit est que le mécanisme fait ce que `R4-P24` attend de lui
quand l'espacement varie — la condition pour que la re-course vaille ses heures de lecture.

## 4. ⚠⚠ Trois défauts de ma propre fixture, et ce qu'ils enseignent

La première version des contrôles a rendu **trois échecs**, et aucun ne venait du mécanisme.

1. ⚠⚠⚠ **Le chirp était référencé au coin du volume.** La projection d'un départ à
   (2000, 2000, 2000) voxels vaut **4800 µm** ; avec une pente de 0,05 µm/µm, le pas y était déjà
   **négatif**. La pile n'avait plus de sens là où le marcheur partait, et les deux fenêtres
   choisissaient le plus long candidat à tous les pas. Un chirp a besoin d'une **origine**, et la
   seule qui en ait une est le départ.
2. **Le recalage se faisait sur `proj / pas`.** Sur une pile à pas variable la phase est
   l'**intégrale de `1/pas`**, pas `proj/pas` : recaler sur des multiples du pas initial laisse le
   marcheur entre deux feuilles dès que la pile s'écarte de ce pas. `controle_fabrique` documente
   déjà ce défaut pour l'obliquité ; il se repaie à l'identique sur le pas.
3. ⚠ **Mon contrôle « l'échelle reste sous un cran » était le mauvais énoncé**, et il a échoué à
   0,094. La raison est réelle : sur une pile à 173 µm le marcheur **alterne** entre 181,7 et
   164,3 — les deux candidats de part et d'autre — donc l'espacement déduit alterne avec lui, et
   une fenêtre qui le suit alterne aussi. Ce n'est pas un défaut tant qu'elle **contient encore le
   pas vrai**. C'est ça qui est asserté désormais, plus la **médiane** de l'échelle sous un cran,
   qui attraperait une dérive systématique sans être sensible à l'alternance.

⭐ Le contrôle qui aurait attrapé le premier défaut existe maintenant : **le pas local au départ
doit être celui qui est déclaré**, et **le recalage doit poser le départ sur une feuille** (la
valeur lue y est le maximum de la pile).

## 5. Ce que ça change pour le graal

- Les deux portes qui restent — `R4-P20` (la portée sur matière lisible) et `R4-P24` (la fenêtre
  locale) — demandent **la même re-course**. Elle est maintenant **écrite et exercée hors ligne**,
  donc la décision de la lancer ne dépend plus que du temps de lecture.
- ⚠ Ce qui reste inconnu ne bouge pas d'un pouce : la démonstration porte sur une pile fabriquée.
  La borne supérieure de **0,9122** de `117` ne devient une mesure que si la re-course tourne.

## 6. Les registres

Fait `R4-F50` (sur une pile à réponse connue, la fenêtre locale retire la butée). Portes `R4-P20`
et `R4-P24` **resserrées** : elles portent le plafond dérivé et le mécanisme. Aucune porte ouverte.

## Reproduire

```bash
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier        # 59 contrôles
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --demonstration \
    --json docs/mesures/la_fenetre_locale_sur_une_pile_connue.json           # analytique
```

⚠ La batterie touche le volume réel sur sa fin ; la démonstration et tous les contrôles de ce
document sont **analytiques**. ⛔ **La re-course elle-même n'est pas lancée** : elle demande des
lectures distantes sur des heures.

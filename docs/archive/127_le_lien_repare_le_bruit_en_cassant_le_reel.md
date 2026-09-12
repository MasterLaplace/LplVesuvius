# 127 — Le lien répare la déchirure de bruit en cassant le décrochement réel

> ⭐⭐⭐⭐ **`R4-P25` DEMANDAIT CE QUI TIENT DEUX MARCHES VOISINES ENSEMBLE. UN LIEN LATÉRAL LE
> FAIT — ET LE TÉMOIN ANNULE LE RÉSULTAT.** À λ = 0,25, les déchirures passent de **6 lots sur 6 à
> 0 sur 6**, le saut maximal de **11,9866 à 0,2971 feuille**, et **le taux ne bouge pas** (coût
> −0,0006). Vu de la nappe, c'est une réparation complète et gratuite.
>
> ⚠⚠⚠ **MAIS SUR UN DÉCROCHEMENT RÉEL DE 1,156 FEUILLE, LE MÊME LIEN SE TROMPE DE 2,60 FEUILLES
> LÀ OÙ L'ABSENCE DE LIEN SE TROMPAIT DE 0,15.** Sans lien, le saut mesuré vaut **1,0058** pour une
> vérité de **1,1561** ; avec λ = 0,25 il vaut **3,7537**, avec λ = 0,50 **15,1439**. L'écart à la
> vérité est multiplié par **17,3**, puis par **93**.
>
> ⭐⭐⭐⭐ **ET IL NE LE MASQUE PAS, IL L'AMPLIFIE** — ce qui est l'inverse de ce que j'avais écrit
> avant de mesurer. Tirer une marche vers une voisine assise une feuille plus loin l'arrache à la
> sienne, et les dégâts se propagent de proche en proche.
>
> ⚠⚠ **LA FORCE N'EST PAS MONOTONE** : λ = 0,50 laisse **5 lots sur 6** se déchirer, contre 0 pour
> λ = 0,25. Un lien deux fois plus fort n'est pas un lien deux fois meilleur, donc λ ne se règle
> pas par un balayage.
>
> ⭐ **Zéro lecture distante.**

## 1. Pourquoi ce fichier

`124`, corrigé par `126`, mesure que huit marches parties de la même feuille se déchirent **12 fois
sur 12**, alors que chacune prise seule ne dérive ni en direction (`119`) ni en phase (`123`). Ce
qui manque n'est donc pas une correction de trajectoire — il n'y a rien à corriger sur une marche
qui va droit — c'est un lien **latéral**. C'est exactement le geste de l'humain qui recoud, et
`R4-P25` demandait ce qui le remplace.

Ce document construit le lien le plus simple qui puisse marcher, et le mesure contre la même base.

## 2. Le lien, et les quatre choix qui le définissent

Après chaque pas, chaque marche est ramenée d'une fraction **λ** vers la moyenne de ses voisines.

- ⭐ **La correction porte sur la POSITION, pas sur la direction.** Corriger la direction changerait
  ce que la marche lit au pas suivant : on ne saurait plus si le lien a tenu la nappe ou modifié la
  lecture. Corriger la position déplace le point de départ du pas suivant, et rien d'autre.
- ⚠⚠ **Elle est projetée sur l'axe d'AVANCE**, parce que c'est là que vit la phase. Une correction
  libre déplacerait aussi latéralement, et les huit marches finiraient par se rejoindre en une
  seule : la déchirure disparaîtrait en supprimant la nappe.
- ⚠ **Elle est calculée sur les positions d'AVANT**, sinon une marche dépendrait de la correction
  déjà reçue par sa voisine, donc de l'ordre d'itération.
- ⚠ **Les deux marches de bord n'ont qu'une voisine, et c'est elle qui sert.** Un rappel vers
  soi-même les laisserait libres, et la nappe se déchirerait toujours par ses bords.

⚠ Le pas n'est **pas** réimplémenté : `marcher` est appelé un pas à la fois. Il n'existe qu'une
seule marche dans le dépôt, et c'est elle qu'on mesure.

⭐⭐ **Le contrôle qui rend la comparaison possible : un lien NUL doit reproduire exactement la
nappe libre de `124`.** Ma première version pilotait la marche depuis les champs **arrondis** de
l'étape — avance au dixième de micron, direction à 10⁻⁶ — et les deux chemins divergeaient
complètement : 11,99 contre 2,11 feuilles sur la même graine. Un système chaotique ne pardonne pas
un arrondi de pilotage. La batterie exige désormais l'égalité.

## 3. ⭐⭐⭐⭐ Sur la nappe, λ = 0,25 répare tout

Six graines, huit marches, obliquité 35°, bruit 8, **112 pas** — la traversée entière. Test
**apparié** : la même réalisation de bruit est marchée à chaque force.

| λ | se déchirent | saut médian | saut max | taux médian | déchirures évitées | coût en taux |
|---:|---:|---:|---:|---:|---:|---:|
| **0,00** | **6 / 6** | 1,0446 | **11,9866** | 0,9994 | — | — |
| **0,25** | **0 / 6** | **0,2153** | **0,2971** | 1,0000 | **6** | **−0,0006** |
| **0,50** | 5 / 6 | 0,7410 | 4,7743 | 1,0000 | 1 | −0,0006 |

⭐ **Le coût est négatif** : le lien ne fait pas chuter le taux de confirmation, il le fait
remonter d'un demi-millième. Un lien qui aurait supprimé la déchirure en collant des marches qui ne
lisent plus rien se serait trahi là.

⚠ **Les six graines ne sont pas un sous-ensemble clément** : elles portent à la fois le **minimum**
(0,7769) et le **maximum** (11,9866) des douze de `126`.

## 4. ⚠⚠⚠ Le témoin, et c'est lui qui décide

Un lissage assez fort colle toujours les marches ensemble : « moins de déchirures » est satisfait
par construction passé une certaine force. La question n'est donc pas s'il supprime la déchirure,
c'est ce qu'il fait à ce qui n'en est **pas** une.

La moitié des marches part d'une feuille, l'autre moitié d'une feuille décalée de **200 µm**, soit
**1,156 feuille**. La nappe porte un décrochement **connu**, et il n'a rien d'exotique : `91`
mesure que la vérité de terrain **humaine** devient elle-même discontinue au bord du rouleau.

| | saut mesuré | écart à la vérité |
|---|---:|---:|
| vérité injectée | 1,1561 | — |
| sans lien | **1,0058** | **0,1503** |
| λ = 0,25 | **3,7537** | **2,5976** |
| λ = 0,50 | **15,1439** | **13,9878** |

⭐⭐⭐⭐ **Sans lien, la nappe mesure le décrochement à 13 % près. Avec lien, elle se trompe de
plus de deux feuilles.** Le mécanisme qui répare une déchirure de bruit est le même qui détruit une
discontinuité réelle, et il n'a aucun moyen de les distinguer : les deux se présentent à lui comme
un écart entre voisines.

⚠⚠ **Et l'erreur va dans le sens que je n'attendais pas.** J'avais écrit que le lien
**masquerait** le décrochement ; il l'**amplifie**. Tirer une marche vers une voisine située une
feuille plus loin l'arrache à la sienne, celle-ci tire la suivante, et la nappe s'éventre au lieu
de se refermer. Le prédicat mesure donc l'**écart à la vérité injectée**, qui couvre les deux
façons de se tromper — un prédicat qui n'aurait cherché que le masquage aurait rendu « le lien ne
masque rien » et serait passé à côté.

⚠ Le témoin tourne pour **chaque** force, pas seulement la plus forte : ne sonder que λ = 0,50
aurait laissé sans réponse la seule valeur qui répare.

## 5. ⭐⭐ La force n'est pas monotone

λ = 0,50 est **pire** que λ = 0,25 : cinq lots sur six se déchirent encore, et son saut maximal
remonte à 4,7743. Deux conséquences, et la seconde est méthodologique.

- Un lien plus fort ne tient pas mieux. Au-delà d'une certaine force la correction d'une marche
  dépasse l'écart qu'elle corrige, donc elle dépose la marche **de l'autre côté** de sa voisine, et
  le lot oscille au lieu de converger.
- ⚠⚠ Un paramètre non monotone ne se règle pas par un balayage, et surtout **chercher le meilleur
  λ sur le corpus qui sert à juger serait régler un seuil sur ce qui passe** — le péché capital du
  dépôt. Trois valeurs sont comparées pour savoir **si** un lien change quelque chose et ce qu'il
  coûte, pas pour trouver la bonne.

## 6. ⚠⚠ Le verdict ne peut pas être rendu par une moitié, et il l'était

Le fichier mesurait les deux moitiés et son verdict n'en lisait qu'une :
`le_lien_tient_la_nappe` valait **vrai** dès qu'une force évitait une déchirure sans coûter de
taux — donc vrai pour **λ = 0,50**, qui sauve un lot sur six et fausse un décrochement réel de
**13,99 feuilles**. Une conclusion qui contredisait le tableau imprimé deux lignes plus bas.

Corrigé : les deux verdicts sont désormais rendus au même endroit, par une fonction `juger` qui
voit les deux moitiés — `la_nappe_tient` d'un côté, `fausse_un_decrochement_reel` de l'autre, et
`le_lien_est_utilisable` seulement si les deux répondent. ⭐ **Un témoin ABSENT refuse le lien** au
lieu de le laisser passer : sans lui le verdict est indécidable, et l'inverse laisserait une force
non sondée passer pour utilisable au seul motif qu'on ne l'a pas regardée.

⭐ `juger` est **pure** : elle ne marche rien. C'est ce qui permet à la batterie de lui donner
exactement le cas qui a révélé le défaut — une force qui tient la nappe **et** fausse un
décrochement — et de vérifier qu'elle sait refuser. Une fonction qui aurait exigé de remarcher la
nappe n'aurait été sondable qu'au prix d'une traversée.

⚠ Le verdict est une **lecture** des marches, pas une marche : `--rejuger` le recalcule sur une
mesure déjà écrite, et le calcul reste dans l'arbre puisque c'est la même fonction que `mesurer`
appelle.

## 7. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **La réponse à `R4-P25` n'est pas « un lien latéral ».** Elle est : *un lien latéral qui
  sait quand se relâcher.* Le lien nu répare la déchirure de bruit en cassant la discontinuité
  réelle, donc il échange une panne contre une autre — et la seconde est pire, parce qu'une
  déchirure de bruit est une erreur locale alors qu'un décrochement effacé est une erreur sur la
  **géométrie du rouleau**.
- ⚠⚠ **Et ce qui manque pour relâcher est exactement ce que `R4-F53` dit indisponible** : la
  déchirure ne s'annonce pas (rho +0,5315, p 0,0754 au pas 16). Pour décider de relâcher, il
  faudrait distinguer « ces deux voisines s'écartent parce que le bruit les a séparées » de « elles
  s'écartent parce que le rouleau décroche » — et rien de mesuré ici ne le distingue avant coup.
  La porte se referme sur elle-même.
- ⭐ **C'est donc une borne sur le mécanisme, pas un échec de la mesure** : ce qui fait la valeur de
  l'humain n'est pas de recoudre, c'est de savoir **quand ne pas recoudre**.
- ⚠ **Analytique, et ça borne ce que ça dit.** La pile fabriquée porte un décrochement injecté,
  connu au centième de feuille. Le rouleau en porte de vrais, dont on ne connaît la taille par
  aucun moyen — le témoin établit que le lien fausse un décrochement, pas de combien il fausserait
  ceux du rouleau.

## 8. Les registres

Fait `R4-F55` : le lien latéral supprime la déchirure de bruit et fausse le décrochement réel.
`R4-P25` **reste ouverte**, avec sa demande resserrée — un lien qui sait se relâcher — et sa
dépendance à `R4-F53` écrite. Aucune porte nouvelle : ce qui manque est dans celle-ci.

## Reproduire

```bash
uv run python src/nappe/un_lien_lateral_entre_marches.py --verifier   # 16 contrôles
uv run python src/nappe/un_lien_lateral_entre_marches.py \
    --json docs/mesures/un_lien_lateral_entre_marches.json            # 3 forces × 6 graines
uv run python src/nappe/un_lien_lateral_entre_marches.py \
    --rejuger docs/mesures/un_lien_lateral_entre_marches.json         # le verdict seul
```

⚠ **Tout est analytique.** Le marcheur, la pile fabriquée, le calcul de phase et le prédicat de
déchirure sont **importés** — de `99`, `123` et `124`. Ce fichier n'ajoute que le lien.

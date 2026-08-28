# 63 — La première vérité terrain, et la résolution éliminée une seconde fois

> ⭐⭐⭐ **Ce dépôt n'avait jamais mesuré une AUC contre des étiquettes.** Tous ses contrôles
> positifs sont des **rendus publiés** — `ink_segment_complet.npy` est ce que quelqu'un d'autre
> a jugé lisible et a pris la peine de rendre, pas une vérité. Le 2026-08-28, en corrigeant
> l'angle mort de [`59`](59_la_campagne_plutot_que_le_rouleau.md), les fragments sont apparus :
> ils publient `inklabels.png`, aligné sur leurs couches de surface. C'est le jeu du concours
> de détection d'encre, et il permet une chose qui n'avait jamais été faite ici.

## 1. Ce qui a été mesuré

`PHercParis2Fr47` (`Frag1`), surface exposée à 54 keV, 65 couches publiées dont les **26 du
milieu** ont été prises. Fenêtre de 1024 px, notre chaîne complète — pont, normalisation par
le plafond du type, `infer_ink`, pas de balayage 21 — puis
[`src/volume/evaluate_segment.py`](../src/volume/evaluate_segment.py), qui existait déjà.

| domaine | pixels | encre | **AUC** | précision | rappel | F1 |
|---|---:|---:|---:|---:|---:|---:|
| tout le segment | 1 018 081 | 31,9 % | **0,746** | 0,552 | 0,609 | 0,579 |
| lignes annotées | 748 678 | 43,3 % | 0,701 | 0,609 | 0,609 | 0,609 |
| tuiles annotées (256 px) | 628 705 | 51,6 % | 0,677 | 0,654 | 0,609 | 0,631 |

⭐ **Le contrôle par mélange rend exactement 0,500** sur les trois domaines, et le gain de
précision sur le hasard vaut **1,7× / 1,4× / 1,3×**. Le signal est réel.

### ⚠⚠ La fenêtre a été choisie SANS regarder les étiquettes

Prendre la région la plus riche en encre flatterait le chiffre par construction — c'est le
même défaut que choisir un seuil pour que le tirage du jour passe. Le critère est la
**couverture de papyrus**, lue dans `mask.png`, et le tri est la distance au centre de masse.
La part d'encre que la fenêtre porte — **31,8 %** — est *rapportée*, jamais choisie. Le
contrôle qui porte cette garantie asserte que la signature de `fenetre_pleine` **ne prend
aucune étiquette** ([`src/encre/fenetre_sur_masque.py`](../src/encre/fenetre_sur_masque.py),
12 contrôles).

## 2. ⚠⚠⚠ 0,746 n'est pas 0,925, et la première explication qui vient est FAUSSE

Ce dépôt cite **AUC 0,925** comme « là où le modèle marche ». L'écart saute aux yeux, et
l'explication qui vient d'elle-même aussi : `Frag1` est scanné à **3,24 µm** quand le modèle a
été entraîné à **7,91 µm** ([`58`](58_resolution_ou_rouleau.md) §8 bis) — un écart de **144 %**,
là où `58` en éliminait un de **9 %**. La mesure est donc prise **hors du domaine
d'entraînement**.

Le test juste est de ramener le fragment au pas du modèle et de refaire la mesure. Fait :

| pas | facteur | **AUC** | précision | rappel |
|---|---:|---:|---:|---:|
| **3,24 µm** (natif) | ×1 | **0,746** | 0,552 | 0,609 |
| 6,48 µm | ×2 | **0,693** | 0,429 | 0,821 |
| 9,72 µm | ×3 | **0,686** | 0,408 | 0,864 |

⭐⭐⭐ **Ramener le fragment au pas d'entraînement N'AMÉLIORE PAS l'AUC — elle tombe, et de
façon monotone.** Les facteurs ×2 et ×3 encadrent les 7,91 µm de l'entraînement, et les deux
sont **sous** le natif. La résolution n'explique donc pas l'écart aux 0,925.

⭐ Et c'est la **seconde** élimination de cet axe, par une voie indépendante : `58` l'avait
éliminé par émulation sur `Scroll 1`, en comparant des σ contre une carte publiée. Ici c'est
un **autre objet**, contre de **vrais labels**, et la conclusion converge.

ⓘ Ce que le balayage montre aussi, et qui n'était pas prévu : décimer fait **dire l'encre plus
souvent**. Le rappel monte de 0,609 à 0,864 pendant que la précision tombe de 0,552 à 0,408.
Le modèle devient plus bavard et moins juste, ce qui est cohérent avec un signal dilué.

## 2 bis. ⚠⚠ La réplication NE CONFIRME PAS — et c'est le résultat le plus utile du lot

`Frag2` (`PHercParis2Fr143`) porte les mêmes étiquettes, et la campagne est la même à un
paramètre près. Fenêtre choisie sur le masque seul, à (7824, 4032).

| fragment | encre de la fenêtre | **AUC** | précision | rappel | gain sur le hasard |
|---|---:|---:|---:|---:|---:|
| `Frag1` | 31,8 % | **0,746** | 0,552 | 0,609 | **1,7×** |
| `Frag2` | 20,6 % | **0,600** | 0,257 | 0,345 | **1,3×** |

⚠⚠⚠ **0,746 n'est pas reproductible sur un second objet.** L'écart est de **0,146 d'AUC**,
et il ne s'explique **pas** par la densité d'encre : l'aire sous la courbe ROC est
indépendante de la prévalence par construction — c'est une mesure de **rang**, pas de taux.
Deux fenêtres choisies par la même règle, sur deux fragments du même corpus, au même
réglage, donnent deux réponses éloignées.

⭐ Ce qu'il faut en retenir, et c'est plus honnête que le premier chiffre : **notre chaîne,
contre vérité terrain, se situe entre 0,60 et 0,75 selon le fragment**. Citer « 0,746 » seul
serait publier le meilleur des deux tirages.

⚠ Le contrôle par mélange rend **0,500** dans les deux cas, donc les deux portent un signal
réel — le désaccord porte sur *combien*, pas sur *s'il y en a*.

⚠ Un troisième point est en cours (`Frag3`, 7,9 % d'encre sur l'ensemble du fragment, le plus
maigre des trois) : il dira lequel de 0,60 ou 0,75 est l'exception, ou qu'il n'y a pas
d'exception mais une dispersion.

## 3. Ce que ce document N'établit pas

1. ⚠⚠ **Si `Frag1` était dans l'entraînement du modèle.** `timesformer_GP_scroll1` vient des
   étiquettes du Grand Prize 2023 (Scroll 1), et les fragments sont le jeu du concours
   **antérieur** — donc probablement hors entraînement, mais **on ne peut pas le vérifier
   d'ici**, et une AUC haute sur du déjà-vu ne voudrait rien dire. Une AUC *basse* sur du
   déjà-vu serait en revanche encore plus mauvaise, donc la réserve ne va que dans un sens.
2. ⚠ **La décimation conserve le détail en profondeur** qu'un vrai scan grossier n'aurait pas
   (`58` §8). Les deux AUC décimées sont donc un **majorant** de ce qu'un vrai scan à 6,5 ou
   9,7 µm rendrait — ce qui **renforce** la conclusion, puisqu'elles sont déjà plus basses que
   le natif.
3. ⚠ **Un fragment n'est pas un rouleau.** Sa surface est ouverte, plate, et n'a pas traversé
   un déroulage virtuel. Ce qui est mesuré ici est ce que le modèle fait d'un papyrus dont la
   géométrie est facile ; un rouleau y ajoute tout le reste.
4. ⚠⚠ ~~**Une seule fenêtre, un seul fragment.**~~ **La réplication est faite** (§2 bis) et
   elle **ne confirme pas** : 0,600 sur `Frag2` contre 0,746 sur `Frag1`. Ce qui reste ouvert
   n'est plus « répliquer » mais **expliquer la dispersion**.

---

**Instruments** : [`src/encre/fenetre_sur_masque.py`](../src/encre/fenetre_sur_masque.py)
(12 contrôles), [`src/encre/decimer_couches.py`](../src/encre/decimer_couches.py)
(14 contrôles), [`src/campagnes/campagne_fragment_verite_terrain.sh`](../src/campagnes/campagne_fragment_verite_terrain.sh),
et [`src/volume/evaluate_segment.py`](../src/volume/evaluate_segment.py), qui existait déjà.
**Mesures** : [`frag1_verite_terrain.json`](mesures/frag1_verite_terrain.json),
[`frag1_echelles.json`](mesures/frag1_echelles.json).
**Voir aussi** : [`58`](58_resolution_ou_rouleau.md) §8 bis et §8 quater,
[`59`](59_la_campagne_plutot_que_le_rouleau.md) §1 pour l'angle mort qui a rendu tout ceci
visible, [`09`](09_protocole_jugement_modele.md) §2 bis pour le jeu du juge.

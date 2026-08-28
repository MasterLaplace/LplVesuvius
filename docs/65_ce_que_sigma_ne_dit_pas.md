# 65 — Ce que σ ne dit pas, et à quelle résolution l'encre est établie lisible

> ⭐⭐⭐ Deux inférences que ce dépôt fait depuis des semaines n'avaient jamais été testées :
> **qu'un σ élevé veut dire que le modèle lit**, et **que 0,686 d'AUC à 9,72 µm veut dire que
> l'encre y est lisible**. Les 23 tuiles étiquetées de [`63`](63_la_premiere_verite_terrain.md)
> permettent de tester les deux. Aucune des deux ne survit telle quelle.

![Deux intervalles qui contiennent leur point nul](images/65_ce_que_sigma_ne_dit_pas.png)

## 1. σ ne prédit pas la qualité mesurée

[`60`](60_la_constante_qui_rendait_le_modele_muet.md) fait reposer « le modèle n'est pas inerte
sur `PHerc1447` » sur un σ de **0,6558**, soit 1,2× le témoin. [`58`](58_resolution_ou_rouleau.md)
fait reposer l'élimination de la résolution sur des rapports de σ. C'est la grandeur avec
laquelle tout le raisonnement de ce dépôt sur « ce rouleau-ci » est mené.

⚠⚠ **Rien n'avait jamais vérifié qu'un σ élevé veut dire que le modèle LIT.** Les tuiles
étiquetées sont le premier endroit où la question se pose : chacune a un σ, mesuré sur les
logits bruts sans regarder les étiquettes, **et** une AUC contre ces étiquettes.

| grandeur | ρ de rang | IC 95 % | p permutation | **p Holm** |
|---|---:|---:|---:|---:|
| aire médiane des taches | −0,448 | [−0,70 ; −0,07] | 0,0312 | 0,187 |
| hauteur médiane | −0,319 | [−0,69 ; +0,11] | 0,1258 | 0,629 |
| composantes | +0,284 | [−0,11 ; +0,61] | 0,1848 | 0,739 |
| **σ** | **+0,263** | [−0,22 ; +0,64] | 0,2244 | 0,739 |
| épaisseur de trait | −0,108 | [−0,54 ; +0,32] | 0,6279 | 1,000 |
| couverture | −0,097 | [−0,50 ; +0,31] | 0,6529 | 1,000 |

⭐ **σ arrive quatrième sur six, et ne tranche pas.** Son signe est celui qu'on espère — plus
de dispersion, meilleure AUC — mais l'intervalle contient zéro et la valeur p corrigée vaut
0,739.

⚠⚠⚠ **Ce que ça N'établit PAS** : que σ soit inutile. À 23 tuiles, et contre une grandeur
dont l'écart-type vaut 0,2243 ([`64`](64_la_dispersion_netait_pas_un_effet.md)), rien ne peut
être établi dans un sens ni dans l'autre. Ce qui change, c'est le **statut** de l'inférence :
« σ est élevé donc il y a du signal » était traité comme un fait et n'est qu'une **hypothèse
non testée**, qui a maintenant été testée une fois sans succès.

⚠ Et la limite honnête du test : les tuiles viennent de **fragments** à 3,24 µm, pas du rouleau
à 8,64 µm. Un lien σ↔qualité pourrait exister là et pas ici. Mais c'est précisément l'argument
qui ne peut plus être avancé sans le dire.

## 2. À 9,72 µm, la lisibilité n'est PAS établie — et cette carte ne peut pas l'établir

[`63`](63_la_premiere_verite_terrain.md) §2 publie 0,686 d'AUC à 9,72 µm, dans un tableau qui
répond à une autre question — *la résolution explique-t-elle l'écart aux 0,925 ?* La réponse
était non. Mais `M1ter` demande autre chose : **l'encre est-elle lisible à 9 µm ?** Et 0,686
sans intervalle ne répond pas.

Découpé en 4 × 4 tuiles couvrant chacune le seizième du **même** morceau de papyrus à toutes
les échelles :

| échelle | µm | AUC groupée | moyenne des tuiles | **IC 95 %** | n | témoin par mélange |
|---|---:|---:|---:|---:|---:|---:|
| natif | 3,24 | 0,746 | 0,674 | **[0,541 ; 0,788]** | 11 | [0,498 ; 0,502] |
| ×2 | 6,48 | 0,693 | 0,594 | [0,468 ; 0,722] | 10 | [0,495 ; 0,500] |
| ×3 | 9,72 | 0,686 | 0,599 | [0,455 ; 0,745] | 10 | [0,495 ; 0,500] |

⭐⭐ **À 3,24 µm, la lisibilité est établie** — l'intervalle exclut 0,5, et c'est la première
fois que ce dépôt l'établit contre de vraies étiquettes plutôt que contre un rendu publié.

⚠⚠⚠ **À 6,48 et 9,72 µm, elle ne l'est pas** : les deux intervalles contiennent 0,5. Le
chiffre groupé de 0,686 se lit comme une réponse et n'en est pas une.

⭐ Le témoin par mélange est serré autour de 0,5 aux trois échelles ([0,495 ; 0,502]), donc
l'instrument fonctionne : ce n'est pas lui qui élargit les intervalles.

### ⚠⚠ Et découper plus fin ne sauve pas la mesure — c'est mesuré, pas supposé

Plus de tuiles rétrécit un intervalle en √n, mais des tuiles plus petites portent des AUC plus
bruitées. Lequel gagne dépend de la taille des structures d'encre par rapport à la maille, et
ne se décide pas sur le papier :

| échelle | 3×3 | 4×4 | 5×5 | 6×6 | 8×8 |
|---|---:|---:|---:|---:|---:|
| natif | 0,227 (7) | 0,248 (11) | 0,184 (16) | **0,155** (23) | 0,189 (35) |
| ×2 | 0,228 (7) | 0,250 (10) | 0,212 (16) | 0,202 (21) | 0,179 (33) |
| ×3 | 0,197 (7) | 0,288 (10) | 0,220 (16) | 0,212 (21) | 0,202 (32) |

*(largeur de l'intervalle, nombre de tuiles gardées entre parenthèses)*

À 9,72 µm la largeur reste autour de **0,20** quelle que soit la maille : l'écart-type grandit
aussi vite que le compte de tuiles. **Cette carte ne peut pas trancher.** Ce qu'il faut n'est
pas un meilleur découpage mais **plus de surface rendue**, ce qui est une campagne.

ⓘ Au natif, 6×6 donne la largeur la plus faible (0,155), et 8×8 remonte à 0,189 — le point où
la maille devient trop fine pour l'encre est visible dans le tableau.

## 3. La réserve qui voyage avec le résultat

⚠⚠ La décimation **conserve le détail en profondeur** qu'un vrai scan grossier n'aurait pas,
puisqu'un voxel plus large intègre aussi dans cette direction ([`63`](63_la_premiere_verite_terrain.md)
§3). Ce qui est mesuré ici est donc un **majorant** de ce qu'un vrai scan à 9,72 µm rendrait.

Un majorant qui reste au-dessus du hasard répondrait « oui, à cette borne près ». Un majorant
qui ne l'établit pas ne répond rien — et c'est le cas.

## 4. Ce que ce document N'établit pas

1. ⚠⚠ **Que l'encre soit illisible à 9,72 µm.** Un intervalle qui contient 0,5 dit que la
   différence n'est pas établie, jamais qu'elle est nulle. Dire l'un pour l'autre serait la
   faute que ce dépôt appelle « une vérification satisfaite pour la mauvaise raison ».
2. ⚠⚠ **Que σ soit sans valeur.** Voir § 1 : le test échoue à établir, il ne réfute pas.
3. ⚠ **Que `58` ait tort d'éliminer la résolution.** `58` compare **deux objets réels** à 9 %
   l'un de l'autre ; ce document décime **un** objet d'un facteur 3. Ce sont deux questions, et
   la seconde ne renverse pas la première — mais elle empêche de citer « 0,686 à 9,72 µm »
   comme preuve que la résolution ne coûte rien.
4. ⚠ **Un fragment n'est pas un rouleau.** Tout ceci est mesuré sur une surface ouverte et
   plate qui n'a pas traversé de déroulage virtuel.

---

**Instruments** : [`src/encre/lisible_a_neuf_microns.py`](../src/encre/lisible_a_neuf_microns.py)
(25 contrôles), [`src/encre/transport_de_calibration.py`](../src/encre/transport_de_calibration.py)
(40 contrôles), [`src/figures/figure_ce_que_sigma_ne_dit_pas.py`](../src/figures/figure_ce_que_sigma_ne_dit_pas.py)
(14 contrôles).
**Mesures** : [`lisible_a_neuf_microns.json`](mesures/lisible_a_neuf_microns.json),
[`transport_de_calibration.json`](mesures/transport_de_calibration.json).
**Voir aussi** : [`64`](64_la_dispersion_netait_pas_un_effet.md) pour le plancher de bruit qui
rend ces intervalles lisibles, [`45`](45_consistent_with_quantifie.md) §7 pour les cinq autres
grandeurs, [`60`](60_la_constante_qui_rendait_le_modele_muet.md) et
[`58`](58_resolution_ou_rouleau.md) pour les deux endroits où σ porte un raisonnement.

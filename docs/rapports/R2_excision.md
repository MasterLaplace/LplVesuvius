# R2 — L'excision et la réparation : réparer une trace sert-il à quelque chose de mesurable ?

> Rapport de campagne, écrit le **2026-09-11** d'une seule lecture des documents `archive/03`–`07`,
> `11`, `17`, `34` et `archive/75` §D1 (9 documents et une section, 2026-08-16 → 2026-09-05).
> Convention : `archive/NN §k` cite la preuve ; ce rapport est la lecture. Un fait porte un statut
> (`établi` · `borné` · `réfuté` · `rétracté` · `ouvert`) et son producteur (`src/excision/…` sauf
> mention ; JSON ou JSONL de même nom dans `docs/mesures/`).
>
> ⚠ Périmètre. Le fil commun est le **recensement d'auto-intersection** de `windcheck` — le seul
> vérificateur de trace du domaine qui publie ses chiffres — et ce qu'on peut mesurer avec lui,
> contre lui, ou à côté de lui sans trace du tout : la réparation qu'il propose (`03`–`05`, `07`),
> une métrique de proximité validée contre son recensement (`06`, `07`), la phase d'enroulement
> publiée (`17`), le volume lu sans trace (`11`, dont les producteurs vivent dans `src/excision/`),
> et le mode de panne de l'outil officiel du concours (`34`). `33` (la carte des treize) est
> rattaché à R3 avec `16` ; `62` à R5.

## 0. Fiche

| | |
|---|---|
| question | `windcheck` détecte qu'une trace se traverse elle-même et **répare** en excisant quelques quads. Son README dit : *« Whether removing it improves ink, texturing, merging or tracing has not been measured »* (`03` §6). Personne ne l'avait mesuré. Est-ce que la matière excisée était mauvaise ? Est-ce que la réparation change autre chose que le compte de contacts ? Et que peut-on mesurer d'une trace **sans** trace de référence ? |
| objets | `PHerc0172` (Scroll 5 : 53 traces, 52 atteintes, 7,91 µm) ; `PHercParis4` (Scroll 1 : 55 traces, 46 mesurables) ; `PHerc0139`, `PHerc1667`, `PHerc0814` (réplication du rayon) ; le maillage condamné de `PHerc0358` (`24`) pour `34` |
| ce qui a été construit | la reproduction de `windcheck` à trois niveaux (`03`) ; `measure.py`/`analyse.py` (l'excision contre le CT, `04`) ; `proximity.py` et sa famille (`baseline_sweep`, `variant_correlate`, `le_rayon_des_mesures`, `le_seuil_au_bon_rayon`, `le_bruit_de_lechantillon`, `reparation_et_proximite --apparie`, `07`) ; `radial.py`, `fusions.py`, `fusion_scan.py`, `track_z.py`, `sensibilite_centre.py` (le volume sans trace, `11`) ; le lecteur du champ `lasagna` (`17`) ; `lire_selfcross.py` et `repro_empty_verdict.py` (`34`) |
| ce qui a été payé | un rayon de recherche **quatre fois trop grand** pendant dix-sept jours, qui faisait paraître importants trois paramètres qui ne comptaient pas (`07` §9, §11) ; une conclusion de tête renversée par une mesure **sans producteur** puis restaurée (`07` §8–12) ; 12 249 « fusions » qui étaient des changements d'étiquette (`11` §5) ; un contrôle de reproductibilité pris pour un contrôle de stabilité (`07` §10) ; 3 h 15 de récupérateur à énumérer 20 To pour 400 Mo, et trois boucles `pgrep` qui se voyaient mutuellement pendant 15 h (`06` §2.2) |
| réponse au 11 septembre | **La réparation ne déplace pas le défaut.** Les cellules excisées sont du papyrus ordinaire (75 810 cellules, H₀ non rejetée) ; la réparation ramène les contacts à zéro et **ne déplace aucune des cellules** que la proximité anormale signale (7 traces sur 10 comptent exactement les mêmes, borne 0,6 %). Le prédicat vérifié — « sans contact transverse » — est plus étroit que le défaut — « une feuille unique bien plongée ». Et la proximité mesure un défaut de la **trace**, corrélé aux croisements à +0,84 au bon rayon, jamais un défaut du **résultat** (R1 `R2-F11`). Ce qu'on peut mesurer sans trace : un pas inter-feuilles invariant à 1,8 % sur toute la hauteur d'un rouleau (142,8 µm), et quatre sites où l'écart double, qui **migrent** |

## 1. Les faits — `REGISTRE_faits.tsv`

**20 faits** portent cette campagne, un par ligne dans
`REGISTRE_faits.tsv` (`R2-F01` et suivants) : l'énoncé, sa valeur, son statut, la
source qui le prouve et le producteur qui le recalcule. Le §2 les cite par leur
identifiant.

## 2. La campagne en six mouvements

```
 M1 reproduire, et mesurer l'excision     03 04 05          16–17 août
 M2 la proximité, et ses trois paramètres 06 07 §1–9        17–18 août
 M3 le volume sans trace                  11 · 06 §7        17–19 août
 M4 la phase publiée                      17                18–19 août
 M5 le verdict qui ne mesure rien         34                20 août
 M6 renverser, puis restaurer             07 §8bis–12 · 75 D1   3–5 septembre
```

**M1 — Reproduire, et mesurer l'excision.** `03` rattrape l'état de l'art en le reproduisant : le
segment nommé rend les 4 et 7 contacts annoncés, le recensement relancé sur les octets relus sous les
deux triangulations reproduit, et les 53 segments de Scroll 5 concordent trace par trace avec la
publication (`R2-F01`). Le fait qui compte est dans le README : *whether removing it improves ink […]
has not been measured*. `04` est écrit **avant** le code, avec son hypothèse nulle et le contrôle qui
attrape les bugs de l'échantillonneur (une cellule retenue doit rendre la même valeur depuis l'original
et depuis la réparée, au bit) : les cellules excisées sont **indiscernables** du papyrus gardé (`R2-F03`).
Un préliminaire sur 5 segments disait le contraire (δ −0,072, 4/4) : c'étaient les quatre pires
segments d'une seule famille, contigus par ordre alphabétique. `05` trouve la donnée que personne
n'exploitait — la séparation en tours — et montre que le résultat tient dans les deux bandes, que les
sévères sont les `auto_grown`, et que **la réparation retire le contact et laisse l'approche**
(`R2-F06`). Puis il paie le piège nº 6 : « 300 µm entre spires » venait d'un README sur Scroll 3 ;
mesuré, 177 µm, et la moitié du §4 tombe (`R2-F07`). La leçon de conception de toute la campagne est
là : **une proximité se normalise par l'espacement local, jamais par une constante.**

![Les deux distributions d'intensité se suivent sur les 256 niveaux : excisées contre témoins appariés](../images/04_excision.png)

*`archive/04` §6 · `src/figures/figure_excision.py` (19 témoins), depuis `excision_samples.tsv`. Les écarts par segment s'étalent sur ±15,6 niveaux et s'annulent en agrégat : « pas de différence en moyenne » n'est pas « pas de différence ».*

**M2 — La proximité, et ses trois paramètres.** `07` construit la métrique que `05` §5 réclamait :
part des cellules dont la distance à une partie **non adjacente dans la paramétrisation** vaut moins
d'un tiers de l'espacement local. Trois traces du même rouleau et de même longueur l'ordonnent
(0,09 / 0,15 / 0,37 % pour 0 / 52 / 408 croisements), 46 traces la corrèlent à +0,769 sans confond de
longueur (`R2-F08`), et le test qui tranche est qu'elle **survit à la réparation** (`R2-F09`). `06` §3
mène les mesures satellites : le seuil d'un tiers défendu par un plateau (3.7, 3.14), la référence en
boule 3D « nettement pire » (3.2), le second rouleau où la métrique est **inapplicable** parce que 44
traces sur 53 ne font pas un tour (`R2-F11`) — et la mesure 3.8, qui appartient à R1 : la proximité
ne prédit pas la lisibilité (rho +0,019, n = 89). Puis `07` §9 trouve, en cherchant pourquoi la
métrique réplique sur `1667` et pas sur `0139`, que le rayon de recherche en voxels valait **749 µm**
à 9,362 µm — plusieurs écarts inter-feuilles, donc il trouvait la spire voisine. Le bon rayon est
choisi par la **physique**, pas par la courbe : 142,8 µm, le pas que `11` §3 avait mesuré ailleurs et
avant (`R2-F12`). Le gain est le plus grand sur `0139`, à la résolution du prix.

![Ce qu'un rayon de recherche trouve, selon sa taille : à gauche la spire voisine, à droite l'anomalie seule](../images/07_le_rayon_trouve_la_voisine.png)

*`archive/07` §11 · `src/figures/figure_le_rayon_trouve_la_voisine.py`. Le cercle de gauche est un minorant (≥ 382,6 µm = 2,7 pas) ; le pas de 142,8 µm vient de `11` §3.*

**M3 — Le volume sans trace.** L'idée de l'auteur — *envoyer une onde traversant toutes les couches
depuis le centre* — donne un compte de feuilles indépendant de tout traçage. Le code de la première
mesure avait été perdu en `python -c` et récupéré du transcript (158 feuilles, 22,7 mm, 11,2 m, centre
re-dérivé à 0,0 voxel) : c'est la naissance de la règle *un chiffre dont le calcul n'est pas dans
l'arbre est une anecdote* (`06` §5.6, `11` §1). Le balayage en z donne un profil en U régulier
(150–176 feuilles) et **l'invariant** : rayon/feuilles à cv 1,8 %, donc le compte suit le rayon et
l'espacement ne bouge pas (`R2-F19`) — c'est ce 142,8 µm que `07` §9 réutilise. Le maximum sur z, pas
la moyenne, estime le nombre de spires (une soudure ne peut que réduire le compte) : ~14 m. Puis quatre
formulations pour localiser les fusions sur l'image dépliée, dont trois échecs instructifs : compter par
rayon (475 sites, tous au centre : une carte du détecteur), suivre les spires (**12 249 « fusions »**
pour 158 feuilles : des changements d'étiquette, 125 murs sur 126 étant appariés à chaque colonne ; le
Hongrois est pire que le glouton pour une raison de fond), chaîner des marques intermittentes. La
quatrième — densité de doublement d'écart par cellule, normalisée par l'espacement local, cœur exclu
sous 4,7 mm parce que trente colonnes y lisent le même pixel — rend **4 candidats stables** groupés
dans le tiers externe (`R2-F20`). Ils tiennent en z quand les coupes sont à l'échelle de la structure
(0,8 mm, pas 22,3), et le site **migre** : 1,50 mm de rayon par mm de hauteur, ce qu'une inclinaison
d'axe ne peut pas expliquer (elle va dans le sens opposé). Le crible au niveau 2 (89 % des murs pour
1/64 du coût) ne trouve **pas les mêmes sites** : c'est un crible, pas un substitut.

![La coupe dépliée en (rayon × angle) : les spires deviennent des lignes suivables](../images/11_polaire.png)

*`archive/11` §4 · `radial.py deplier --png`. À grande échelle les spires ne sont pas horizontales : le rouleau est écrasé, et le dépliage n'exige que la douceur (0,125 voxel par colonne).*

**M4 — La phase publiée.** Le groupe `lasagna` expose un canal `cos` de la phase d'enroulement, la
quantité que `00` §2 nommait comme celle qui rend le saut de spire nommable. Sa période vaut 3 à 7 pas
inter-feuilles (le champ est diffusé, donc un saut y laisse une marche). Le premier code comparait une
cellule sur quarante quand le docstring disait « voisines » ; corrigé en segments contigus. Puis
l'effet fond avec n : +0,517 (8), +0,306 (30), **+0,150 (38)** — *un effet réel ne fond pas quand on
l'échantillonne mieux*. Le soupçon du niveau 3 est levé deux fois : c'est le niveau le plus fin publié,
et la quantification n'écrase rien (médiane 12,2/255, 0 trace nulle). Échec **définitif et propre** ;
le lecteur du champ reste.

**M5 — Le verdict qui ne mesure rien.** `34` relit les 240 auto-intersections de `24` sous neuf
`--maxedge` : elles survivent à la désactivation du filtre (le verdict est une propriété de la trace),
et le maillage propre apparié rend 0 partout. La découverte est à `maxedge 20` : `clean: true`,
**`pairs_tested: 0`**, 48 040 quads jetés — *propre et rien mesuré sortent par le même champ*, et
`--fail-on-crossing` rend le code 0. Ça arrive **au réglage par défaut** dès qu'un maillage grossit :
sur une géométrie qui ne change pas, 240 → 123 → 0 → 0 (décimation ×1 à ×4), deux pertes distinctes
(le maillage, puis le filtre qui transforme 72 et 49 en zéros muets). Six scripts du dépôt lisaient
`transverse` sans regarder `pairs_tested` ; `lire_selfcross.py` est le seul lecteur désormais et
refuse (code 3). La mesure a été **perdue** par un commit de rangement qui a écrit `"lignes": []`
par-dessus, restaurée depuis l'historique et vérifiée par l'image régénérée octet pour octet ; le
maillage source n'existant plus, la copie est la seule.

![La géométrie ne change pas, sa description devient plus grossière : le détecteur perd la moitié des croisements puis le filtre transforme le reste en zéros muets](../images/34_sensibilite.png)

*`archive/34` §0 · `src/figures/figure_sensibilite.py`, depuis `sensibilite_maillage.json` (restauré depuis `79fba93`).*

**M6 — Renverser, puis restaurer.** Le 3 septembre, en voulant rendre recalculable le « 0,37 → 0,38 % »
pour l'article, une mesure sur deux `auto_grown` de Scroll 5 montre la réparation **faisant baisser**
la proximité de 50 et 22 % : la conclusion de tête de `07` est déstabilisée, et `75` D1 est ouvert.
Deux jours de mesures la restaurent, pour une bien meilleure raison :
1. la mesure qui a renversé **n'avait aucun producteur** (faite au terminal) ; `reparation_et_proximite.py`
   existe désormais (`07` §8) ;
2. le « cas non montable » était une généralisation depuis le mauvais rouleau : Scroll 1 a **34**
   traces éligibles (sales et > 1 tour), curatées ; à provenance égale, le **signe** change
   (+398 % / −17 %) ;
3. le contrôle écrit pour protéger ce résultat **ne pouvait pas échouer** : trois runs de la même
   commande vérifient la reproductibilité, pas la stabilité sous ré-échantillonnage (`07` §10) ;
   `choice(points.shape[0])` change de tirage dès qu'un quad disparaît, et 12 graines déplacent
   `fbt` de 35 à 229 % — plus que la réparation sur 9 traces sur 10 (`R2-F15`) ;
4. `shortfall`, déjà publié par l'outil, a un bruit sous 5 % ; sur lui la réparation ne déplace rien
   de mesurable (`R2-F16`) ;
5. le producteur `run_proximity.sh` **ne tournait plus** (`python -m excision.proximity`, erreur
   avalée, « 0 mesurées, 55 sans mesure », code 0) — c'est pourquoi personne n'avait rejoué le §8 au
   bon rayon ; rejoué, trois paramètres cessent de compter ensemble (`R2-F13`) et le mécanisme du §6
   survit (`R2-F14`) ; les fichiers se datent eux-mêmes par `measured` (`le_rayon_des_mesures.py`) ;
6. le tirage **par position de grille** retire le bruit au lieu de le borner : 7 traces sur 10
   comptent exactement les mêmes cellules avant et après (`R2-F17`). **D1 est fermé.**

Et en chemin, la réparation elle-même : non déterministe (affirmé sur deux sorties de terminal),
rétracté (trois certificats identiques), **rétabli** (six runs, trois géométries) — la rétractation
était fausse par chance, et son propre commentaire disait que trois répétitions étaient une preuve
faible. La cause est dans la politique gelée de `windcheck` (`R2-F18`) : *« an optimization failure
[…] costs an optimality claim, never an artifact »*. Réparer une fois et garder la sortie.

![L'effet de la réparation, bruit retiré au lieu d'être borné : tirage par index en rouge, par position en ambre](../images/07_tirage_apparie.png)

*`archive/07` §12 · `src/figures/figure_tirage_apparie.py` (9 contrôles). Le trait vertical est le bruit de graine propre à chaque trace.*

## 3. Chronologie, document par document

| doc | date | question | ce qui est établi | ce qui est rétracté ou borné |
|---|---|---|---|---|
| `03` | 16 août | `windcheck` fait-il ce qu'il annonce ? | 4/7 contacts reproduits ; recensement indépendant sous les deux diagonales ; 53/53 sur Scroll 5 ; réparation 99,9989 % conservée ; Scroll 5 = 1 saine sur 53 ; `auto_grown` 9× (médiane 192 contre 21) | « réparer sert » : non établi, par le README lui-même ; le 9× est un effet de longueur (`05`) ; 80 tests sautés ≠ verts |
| `04` | 16–17 août, recalculé 22 août et 5 sept. | les cellules excisées étaient-elles mauvaises ? | H₀ non rejetée (p 0,859, δ −0,0004 ; sans niveau 0 p 0,504) ; le 512 ms/voxel était un chunk par accès (×8 en groupant) ; recalcul dans l'arbre identique | le préliminaire (−0,072 sur 4/4) : biais alphabétique ; la ligne par segment (30/22, −0,011) reste irreproductible ; `n = 1761` mal lu |
| `05` | 17 août | le prédicat vérifié | deux bandes (43 < 0,15 tour ; 9 ≥ 1,6, jusqu'à 5,04) ; les sévères = `auto_grown` ; la réparation laisse l'approche (8/9 à 79 µm) ; espacement 177 µm, p5 101, p90 303 | « le même papyrus rendu deux fois » (40 vx = spire voisine) ; le résultat à 20 vx (158 µm est banal : 37,2 %) ; « 300 µm » emprunté |
| `06` | 17 → 19 août (+ 4 sept.) | le carnet : faites, en attente, écartées | 1.1–1.18 ; 3.1 (+0,769 par tercile), 3.2 (boule pire), 3.5 (niveau 2 : 89 % des murs, ×64), 3.7 (plateau 0,15–0,40), 3.8 (proximité ≠ lisibilité), 3.9 (pas de plancher), 3.10 (le défaut dérive), 3.13 (domaine : un tour), 3.14 ; §2.4 dommage en cœur (20 %), pas un U ; §2.4bis rouleau elliptique 1,26–1,57 ; §5 sept règles | 2.1 `winding.py` supprimé ; 2.3 clos sans ombilic ; « facteur trois » → +28 % ; 3.2 et 3.14 **périmés** au bon rayon (`07` §11) |
| `07` | 17 août → 5 sept. | la réparation déplace-t-elle le défaut ? | métrique ordonne à longueur contrôlée ; survit à la réparation ; +0,769 sur 46 ; domaine = un tour ; rayon physique 142,8 µm (+0,840) ; bruit de graine ; `shortfall` ; trois paramètres tombent ensemble ; mécanisme survit 34/34 ; tirage apparié ×22 ; non-déterminisme = budget d'horloge | « quatre fois une saine » ; « nettement pire » (boule) ; §8 seuil ni arbitraire ni supprimable ; la déstabilisation de l'en-tête (sans producteur) ; signe instable à n = 2 ; « déterministe » à 3 runs ; « même ensemble de valeurs » |
| `11` | 17–19 août | compter les feuilles sans trace | 158 → 176 feuilles, ~14 m ; invariant 142,8 µm cv 1,8 % ; profil en U ; 4 candidats groupés à 17–18 mm ; tiennent en z à 0,8 mm (p 0,0001) ; migrent 1,50 mm/mm (p 0,0010) ; inclinaison écartée (sens opposé) ; niveau 2 = crible ; centre faux de 3,16 mm → 1,75 % ; migration = exception (2/6, témoin positif) | « 11,2 m » (moyenne → maximum) ; sens de la borne noté à l'envers ; 12 249 fusions = étiquettes ; « 20 000 tirages » → 2 000 ; premier test en z (22,3 mm) ne pouvait rien détecter ; rectitude p 0,82 ; 3 tranches fabriquaient une marche |
| `17` | 18–19 août | la phase publiée détecte-t-elle un saut ? | le canal `cos` se lit (période 3–7 pas) ; le lecteur existe ; l'instrument de profondeur tient sur `0139` (+0,369, p 0,045, 3ᵉ corpus) | ❌ **échec définitif** : +0,517 → +0,306 → +0,150 ; une cellule sur 40 au lieu de voisines ; le niveau 3 est le plus fin publié ; la quantification n'écrase rien |
| `34` | 20 août, restauré 4 sept. | les 240 survivent-ils au filtre ? | oui, à tous les réglages > 30 ; propre apparié 0 partout ; `pairs_tested: 0` → `clean: true` ; 240 → 123 → 0 → 0 au défaut ; `26` §9 audité : ses zéros ne sont pas muets mais ne se valent pas (pas 40 = 51 %) ; `lire_selfcross.py` seul lecteur ; `repro_empty_verdict.py` hors ligne | la mesure écrasée par `a5901be` (`"lignes": []`), restaurée ; le maillage source a disparu |
| `75` D1 | 3–5 sept. | re-fonder l'arc | voir M6 ; `shortfall` référence ; tirage par position opt-in ; grille inchangée (142/2 M) ; D1 fermé | `sweep_PHerc0139*`, `sweep_s1_pas` sans déclaration d'échelle : à régénérer |

## 4. Le tableau des statuts

| statut | faits |
|---|---|
| **établi** | `R2-F01` à `R2-F20` ; la reproduction à trois niveaux (`03`) ; le contrôle bit-identique de l'échantillonneur (`04` §3) ; les sévères = `auto_grown` (`05` §1) ; la métrique n'a pas de plancher (7 saines de 0,020 à 0,372 %, `06` 3.9) ; le niveau 2 conserve 89 % des murs (`06` 3.5) ; le cœur de `0172` est le plus dégradé (20 %), l'extérieur non (`06` §2.4) ; le rouleau est elliptique (1,26–1,57, `06` §2.4bis) ; le cœur du dépliage est dégénéré par construction (`11` §6) ; l'inclinaison d'axe ne peut pas expliquer la migration (`11` §8) ; `pairs_tested` doit être lu (`34` §5) |
| **borné** | l'effet de la réparation sur `shortfall` : < 0,6 % au pire, 0,07 % médian (`07` §12) ; la migration : 2 bandes sur 6, Fisher 0,079 (`11` §13) ; les 4 candidats : compatibles avec soudure, déchirure ou vide, non tranché (`11` §7) ; la longueur du papyrus : ~14 m, borne inférieure (`11` §3) ; le signe de l'effet à n = 2 : non lisible (`07` §8) ; 15 à 35 chunks par rouleau pour la carte de `16` (→ R3) ; la fréquence du verdict muet en pratique : non mesurée (`34` §6) |
| **réfuté** | « les cellules excisées lisent de la mauvaise matière » (`04`) ; « 300 µm entre spires » (`05` §4bis) ; « le même papyrus rendu deux fois » (`05` §3) ; la référence en boule comme remède de principe (`06` 3.2, `07` §6) — nuancé au bon rayon ; le seuil d'un tiers comme sélecteur de régime (`07` §11) ; « aucune grandeur sans seuil ne l'égale » (`07` §8 → §11) ; le glouton comme cause de la fragmentation, le Hongrois comme remède, les pistes en sursis, le détecteur qui perd les murs (`11` §5) ; la rectitude comme discriminant (`11` §11) ; la phase d'enroulement comme détecteur de saut (`17`) ; « le niveau 3 était notre choix » (`17` §10) ; « la réparation fait baisser la proximité » (`07` en-tête → §12) ; graine + un fil comme remède au non-déterminisme (`07` §10) |
| **rétracté** | « les `auto_grown` sont 9× plus atteints » (`03` → `05`) ; « quatre fois au-dessus d'une trace saine » (`07` §3) ; « nettement pire » pour la boule (`06` 3.2 → `07` §11) ; « la réparation est déterministe » (3 runs → 6 runs) ; « les deux séries tombent sur le même ensemble » ; « le signe n'est pas stable » (n = 2 → bruit de graine) ; « la déstabilisation » de l'en-tête de `07` ; 12 249 fusions ; « 11,2 m » ; « 20 000 tirages » ; « la mesure de `07` ne se généralise pas » ; « 8 à 16 » et « 7 à 12 voxels » (`16`, → R3) |
| **ouvert** | voir §8 |

## 5. Les contradictions — `REGISTRE_contradictions.tsv`

**34 disputes** tranchées pendant cette campagne,
une par ligne (`R2-C01` et suivants) : *A a dit · B a dit · C tranche · statut*.

## 6. Les lois — `REGISTRE_lois.tsv`

**16 mécanismes** que cette campagne a payés
(`R2-L01` et suivants), rendus en prose groupée dans `FILS_ROUGES.md`.

## 7. Ce que la campagne dit des prix

1. **Progress Prizes — la matière la plus directement soumissible de R2.** Le goulot *conservative
   failure detection* et le problème nº 7 (*métriques d'évaluation*) sont nommés par le concours
   (`07` §6). Ce que le dépôt a : *la vérification que tout le monde utilise laisse passer quelque
   chose, voici la mesure et voici le contrôle* — l'excision est du papyrus ordinaire (`04`), la
   réparation ne déplace pas la proximité (`07` §12), le rayon physique (`07` §9), le verdict muet de
   `vc_tifxyz_selfcross` (`34`), le non-déterminisme déclaré de `windcheck transform` (`07` §10). Plus
   deux résultats négatifs documentés avec leur puissance (`17`, la boule 3D). Et le pas inter-feuilles
   sans trace (`11`) recoupe l'atlas `winding-ruler` (R6 `R2-F12` : 187 µm médian sur la collection ;
   142,8 sur `0172`, 172,8 sur Paris4).
2. **Grand Prize — où le graal a commencé.** `11` est l'ancêtre de R4 : compter les feuilles sans
   traceur, déplier en polaire, localiser où l'écart double, mesurer qu'un défaut migre. La règle
   « un pas d'indice = une feuille » de `76` et le champ d'enroulement de `77` sont la même question
   posée avec le référent humain en plus. Et `34` borne ce que « zéro croisement » veut dire pour tout
   marcheur : nécessaire, jamais suffisant, et muet au-delà d'un pas de maillage.
3. **First Letters et le titre** : rien de direct. `06` 3.8 (→ R1) dit que la proximité ne prédit pas
   la lisibilité ; R2 ne juge que la trace.

## 8. Les portes ouvertes — `REGISTRE_portes.tsv`

**9 portes** que cette campagne laisse
(`R2-P01` et suivants), classées par prix dans `PORTES_OUVERTES.md`.

## 9. Sources pour un article

- **La réparation ne déplace pas le défaut** : `03` §6, `04` §1–6, `05` §4, `07` §3, §10–12,
  `75` D1 — reproduction, hypothèse nulle écrite avant le code, tirage apparié par position, borne
  0,6 %. Antériorité : le README de `windcheck` (*has not been measured*), sa politique gelée
  (`round28-greedy-first-v1`, `failure_rule`).
- **Une métrique de proximité et ses trois paramètres qui ne comptaient pas** : `07` §2, §4bis, §6,
  §9, §11 — le rayon dérivé de la physique, la contamination de la référence, l'ordonner/différence.
  Antériorité : six vérificateurs qui s'arrêtent au même endroit (R6 `R2-F11`).
- **Compter les feuilles sans trace** : `11` §3, §6–8, §11–13 — l'invariant à 1,8 %, le doublement
  d'écart, la migration, le crible. Antériorité : `winding-ruler` (R6), l'ombilic de ThaumatoAnakalyptor
  (non publié pour ces rouleaux).
- **Un verdict qui ne mesure rien** : `34` — le mode de panne d'un outil officiel, son reproducteur
  hors ligne, et la perte-restauration d'une mesure.
- **Deux échecs propres** : `17` (la phase publiée), `06` 3.2/`07` §6 (la boule) — chacun avec la
  puissance qui l'aurait détecté.
- Tout chiffre de ce rapport se recalcule par le producteur nommé ; `src/depot/verifier_chiffres.py`
  lit `docs/rapports/`.

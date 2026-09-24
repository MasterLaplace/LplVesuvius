> ⚠ FICHIER GÉNÉRÉ depuis les `REGISTRE_*.tsv` — ne pas éditer à la main. Régénérer : `./lplv registres --ecrire`.
>
> Source : `docs/rapports/REGISTRE_contradictions.tsv`.

# Les contradictions, et qui a tranché

**233 disputes** que ce dépôt a eues avec lui-même, et comment chacune s'est finie. Une ligne : *A a dit · B a dit · C tranche · statut*. Les lire coûte moins cher que de les repayer.

## R1 — 42 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R1-C01` | `08` §5 : la précision est un plancher, l'étiquetage est partiel | `10` §2 bis : le hasard monte aussi (10,8× → 2,8×) | effet de taux de base ; l'argument est remplacé par rho +0,796 | tranché |
| `R1-C02` | `10` §3 bis : bandes 8704–9728 = trou d'annotation | `09` §10 : le juge note 1–2 | régime du vierge ; nature du signal **ouverte** | tranché |
| `R1-C03` | `09` §6 : il manque de la surface | `10` §4 : le segment entier n'a pas plus de lignes | il manque des **colonnes** et des glyphes séparables | tranché |
| `R1-C04` | `12` §2–3 : le contraste localise la feuille | `12` §10 : courbe en U à 2,4 µm | l'intensité ; validé par le doublement de la corrélation `windcheck` (`12` §11) | tranché ; a coûté deux campagnes de `C2` le 5 sept. |
| `R1-C05` | `12` §10 : > 50 µm ⇒ pas d'encre lisible | `12` §14 : 60 pire que 50 et 70 ; médiane 67 µm | ordinal, aucun seuil absolu (règle nº 1) | tranché |
| `R1-C06` | `12` §6 : l'écart vaut une épaisseur de feuille (142,8 µm) | `12` §6 bis : pas de `0172` emprunté à `1667` | `stack_structure.py` : distance dans sa propre pile | tranché (piège nº 6) |
| `R1-C07` | `12` §13, `19` §7 : 72 segments | `compter_corpus.py` : 80 segments, 50 fenêtres ; 72 = treillis fibres | un compteur par entrée n'est pas un nombre de segments | tranché |
| `R1-C08` | `14` §5 : +0,330 (n = 12) | `14` §8 : −0,192 (n = 54) | puissance : n = 12 ne détecte que 0,73 | tranché ; voie close |
| `R1-C09` | `19` §5 : plateau 15–25 % | `19` §9 : artefact de grille (rho +0,280) | `19` §10 : deux grandeurs différentes ; même outil 72 vs 392 points rho +0,841, plateau intact | tranché |
| `R1-C10` | `19` §11 : ne réplique pas sur Scroll 5 = effet de plancher | `19` §12 : `0139` a une étendue plus grande et le signe opposé | règle propre à Scroll 1 ; publier les quatre corpus | tranché |
| `R1-C11` | `20` §4 : le gauchissement n'est pas implémentable ici | `20` §9, `22` R1 : VC3D construit le jour même | déplacer → ré-aplatir → rendre | tranché |
| `R1-C12` | `20` §5 : 4 segments au-dessus d'un pas (142,8 µm) | `20` §5 : pas de Paris4 = 172,8 ; 1 segment | `--pas-um` sans défaut | tranché |
| `R1-C13` | `20` §8 : la censure ne déplace aucune décision | `20` §8 : Scroll 4 pire encadrement 82,8 µm > 40 | énoncé sur un rouleau, faux sur le suivant | tranché |
| `R1-C14` | `20` §8 : le taux reclassé suit 1/pile | pile de 33 : 2,17 % vs 3,03 attendus ; Scroll 4 (saturation la plus forte) tombe sur l'uniforme | deux piles de 109 s'accordaient pour rien | tranché |
| `R1-C15` | `20` §9 : ré-aplatir est strictement meilleur | un lecteur voit le bas moins lisible ; 1 087 trous, 2 % d'aire | les statistiques d'étirement excluaient les mailles perdues par construction | tranché |
| `R1-C16` | `20` §6 (19 août) : −0,275, n = 80 | `20` §6 (26 août) : −0,242, n = 79 | trois causes non décomposées : un segment retiré, **trois volumes amont changés**, la règle « au bord » corrigée | tranché ; une mesure distante porte une date |
| `R1-C17` | `21` §4 : puce citant +0,384 / +0,463 / −0,382 sous `material` | `19` : ces chiffres sont ceux d'`ecart_a_la_trace`, nominal seulement | corrigé le 19 août | tranché |
| `R1-C18` | `24` : la trace coupe les spires, trois instruments | `25` §5 : la fenêtre de 21 couches est une demi-feuille ; l'officiel échoue plus mal | deux instruments ; puis `36` : cet officiel-là n'était pas une référence | tranché |
| `R1-C19` | `24` §4 : cause = `direction_fields` absent | `26` : le champ ne déplace rien ; `30` : 13/14 tirages propres | 240 = tirage dans la queue | tranché (R3) |
| `R1-C20` | `36` §1 : notre chaîne décale la pile (facteur 79) | `36` §2 : même segment, 3,00 vs 17,28 µm | c'est le **segment**, pas le producteur | tranché |
| `R1-C21` | `36` §5bis : Scroll 1 à 2,4 µm | `58` §1 : volume `20230205180739`, 7,91 µm ; `12` disait déjà 47 µm pour 6 voxels | `--voxel-um` exigé | tranché |
| `R1-C22` | `36` §5bis, `46` §2 : σ 0,0171, le modèle est inerte à 9 µm | `60` : `uint8` / 65535 ; σ 0,6558 | **annulé** ; M1ter rouvert | tranché |
| `R1-C23` | `46` (22 août) : le détecteur rend la même carte (ρ +0,9979) | `46` §3 (28 août) : ρ −0,0100, plus dispersé sur le vide | le bug fabriquait la thèse ; la conclusion refaite est plus dure | tranché |
| `R1-C24` | `46` §3 bis : ~2 100 px pour huit fenêtres | `fenetres_par_region.py` : 5 128 px | `range(0, dim − taille//2, taille)` accepte une fenêtre débordante | tranché |
| `R1-C25` | `46` §3 ter : le témoin ne franchit pas (p 0,50) | à 5 fenêtres un sujet identique rendrait 0,083 | n'établit rien ; second témoin + groupé | tranché |
| `R1-C26` | `46` : `rendu_161` est vide (forme `(0,)`) | `dimensions_tiff.py` : IFD à zéro = rendu interrompu (68 %) ; une seule trace dans `data/leur_graine/trace/` | même surface, pas un second témoin | tranché |
| `R1-C27` | `45` §4 : le trait est la meilleure grandeur (AUC 0,857) | `45` §7 : la pire sur 23 tuiles (ρ −0,108) | deux questions (classer des cartes / prédire une tuile) ; rien ne survit à Holm | tranché ; transport **ouvert** |
| `R1-C28` | `58` §8 bis : l'énergie, 114,8 % d'écart, est le suspect | `66` §3 : 116 keV est dans le sweet spot publié ; témoin 2,4 µm/78 keV inverse les axes | sensibilité, pas distance ; `58` §8 ter : 1,243 vs 1,176 | tranché |
| `R1-C29` | `58` §8 quater : rien à émuler, sept paires d'énergie | même jour : étiquettes sans recalage, recalage sans étiquettes | faisable sur `Frag6` sans labels seulement | tranché |
| `R1-C30` | `59` §1 : les rouleaux lisibles ont été rescannés fin | `59` §1 (corr.) : la référence 0,925 est sur le scan 2023 à 7,91 µm | le rescan n'explique pas la lisibilité | tranché |
| `R1-C31` | `59` §3 : p 0,0081 | `59` §3 bis : 31 jamais tracés ; p 0,50 sur les tentés | trois états, pas deux | tranché |
| `R1-C32` | `59` : aucun rouleau ne fait varier les grandeurs indépendamment | `58` §8 quater : les fragments, 9 paires | vrai des rouleaux, faux du corpus | tranché |
| `R1-C33` | `60` §4 quinquies (1ʳᵉ exécution) : groupé [16, 8, 0, 24], p 0,0000 | le groupe contenait le témoin Scroll 1 | `--temoin` nommé par l'appelant ; 4 contrôles | tranché |
| `R1-C34` | `63` §2 bis : 0,746 vs 0,600, la dispersion est réelle et inexpliquée | `64` : σ intra 0,2243, inter 0,0391 | une fenêtre par fragment n'a pas de barre d'erreur ; 27 tuiles nécessaires | tranché |
| `R1-C35` | `64` §3 : décalage de niveau par tuile explique l'écart groupé / par tuile | aligner les niveaux rend l'AUC pire sur les trois | les niveaux portent du signal | tranché |
| `R1-C36` | `60`, `58` : σ élevé ⇒ le modèle lit | `65` §1 : 4ᵉ sur 6, Holm 0,739 | hypothèse testée une fois sans succès | tranché ; σ **ouvert** |
| `R1-C37` | `63` §2 : 0,686 à 9,72 µm | `65` §2 : IC [0,455 ; 0,745] | non établi ; ne peut être cité comme preuve | tranché |
| `R1-C38` | `72` : rendre la case vide et scorer, rien à faire d'autre | `75` §C1 : deux aplatissements ; recalage affine | Dice 0,971, 3,2 % d'aspect | tranché |
| `R1-C39` | `75` §C1 (1ʳᵉ campagne) : appariement des repères ×8 / ×7,7 | témoin de même forme : vraie place 6ᵉ sur 21, p 0,29 | groupement, pas correspondance | tranché |
| `R1-C40` | `75` §C2 (1ʳᵉ campagne) : fenêtre « face » sur le pic de contraste | `12` §10 : le contraste pique aux interfaces | couple inversé ; AUC 0,50 failli publiée ; gardes | tranché |
| `R1-C41` | `75` §C2 : fenêtre trop mince (62 µm) | `la_profondeur_lue.py` : σ tombe avec l'épaisseur | profondeur innocentée, troisième élimination de l'échelle | tranché |
| `R1-C42` | `69`, `73` : le débinage vaut ≤ 1,3–1,5 / rien | `75` §C3 : 1,01 | courriel non justifié ; envoi = auteur | tranché |

## R2 — 34 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R2-C01` | `03` §5 : les `auto_grown` sont 9× plus atteints | `05` §1 : la bande sévère **est** les `auto_grown` ; `06` 1.10 | tautologie ; normaliser par l'aire | tranché |
| `R2-C02` | `04` préliminaire : δ −0,072, répliqué 4/4 | `04` §6 : 52 segments, δ −0,0004 | famille `20250926*` (8 segments, −0,0242) contre les 44 autres (+0,0047) ; ordre alphabétique | tranché |
| `R2-C03` | `04` §6 : par segment 30 négatifs / 22 positifs, médiane −0,011 | recalcul : 29 / 23, −0,478 (moyennes) ; 29 / 17 / 6 nuls, −1 (médianes) | une troisième quantité dont le code n'est pas dans l'arbre | **irreproductible**, signalé |
| `R2-C04` | `05` §3 : à 40 vx le même papyrus est rendu deux fois | 40 vx = 316 µm = l'écart entre spires | à 5 vx l'effet disparaît ; énoncé restreint à 79–158 µm | tranché |
| `R2-C05` | `05` §4 : le résultat à 20 vx (158 µm) | `05` §4bis : 37,2 % des cellules sont aussi proches | espacement médian 177 µm, mesuré sur la trace | tranché ; 10 vx tient (2,1 %) |
| `R2-C06` | `06` §5.1 : l'espacement varie d'un facteur trois | `06` 1.11 : 158 → 203 µm, +28 % | le chiffre était faux, la règle (ordinal) tient | tranché |
| `R2-C07` | `06` §2.3 : le centre est un barycentre biaisé, il faut l'ombilic | `11` §12 : `umbilicus.txt` n'existe nulle part ; le centre est ajusté sur la monotonie (1,000) ; 3,16 mm → 1,75 % | l'invariant ne dépend pas du centre | tranché |
| `R2-C08` | `06` 3.2 : la boule 3D est nettement pire (+0,560 vs +0,769) | `07` §11 : au bon rayon +0,803 vs +0,840 | écart 0,209 → 0,036, sous le bruit du rho (0,125) ; ce qui reste est la couverture | tranché ; « nettement » rétracté |
| `R2-C09` | `07` §3 : la réparée vaut quatre fois une saine | `06` 3.9 : les 7 saines vont de 0,020 à 0,372 % | un seul témoin, bas | tranché |
| `R2-C10` | `07` §5, `06` §C : il faut un second rouleau | `07` §7 : Scroll 5 est hors du domaine (44/53 sous un tour) | la population, pas les chiffres ; les vrais seconds rouleaux sont `0814`, `1667`, `0139` | tranché |
| `R2-C11` | `07` §8 : le seuil d'un tiers n'est ni arbitraire ni supprimable (plateau puis effondrement) | `07` §11 : au bon rayon, plateau sur toute la plage ; `shortfall` +0,785 | l'effondrement était l'artefact du rayon (la spire voisine admise) | tranché ; §8 périmé |
| `R2-C12` | `07` §9 : la métrique réplique sur `1667` et pas `0139` = résolution | balayage du rayon sur la donnée grossière : +0,609 à 20 vx, −0,143 à 160 | ce n'est pas la résolution, c'est le rayon | tranché |
| `R2-C13` | `07` §9 (3 sept.) : `1667` n'a aucun volume à 7,91 µm, la ligne est illisible | `1667` publie `20231117161658-7.910um` ; l'artefact déclare `voxel_um 7,91`, 18 vx = 142,4 µm | erreur de catégorie (volumes de surface ≠ scans) ; `ou_vit_ce_rouleau.py` | tranché ; la ligne est lisible |
| `R2-C14` | `07` en-tête (3 sept.) : la réparation fait baisser la proximité (−49,8 %, −22,3 %) | `07` §8 : à provenance égale le signe change ; §10 : le bruit de graine dépasse l'effet ; §12 : apparié, 0,07 % | la mesure de l'en-tête n'avait pas de producteur, comparait deux rouleaux et deux provenances, sur une colonne dominée par son bruit | tranché ; titre restauré |
| `R2-C15` | `07` §8 : trois runs identiques donc les écarts sont réels | `07` §10 : reproductibilité ≠ stabilité sous ré-échantillonnage | 12 graines, même fichier : 35–229 % | tranché (péché capital, dans une précaution) |
| `R2-C16` | `07` §10 : `transform` non déterministe (2 sorties) → déterministe (3 runs) | 6 runs : 3 698 / 3 696 ×4 / 3 691 | la rétractation était fausse par chance ; budget d'horloge de la politique gelée | tranché ; rétabli |
| `R2-C17` | `07` §10 : les deux séries tombent sur le même ensemble | un second échantillon : 3 698 n'est pas réapparu | inclusion dans un petit ensemble, union ≥ 3 | tranché |
| `R2-C18` | `07` §10 : graine + `thread_limit: 1` (remède de `44`) | `--threads 1` : trois géométries encore | ni parallélisme ni flottant : un budget d'horloge | tranché |
| `R2-C19` | `06` 3.8 (D) : bloqué, le maillage de `20230909121925` n'est pas dans le jeu | `ppm_to_tifxyz.py` : le `.ppm` porte la même information | prudence mal placée | tranché (→ R1) |
| `R2-C20` | `06` §2.2 / `07` §11 : `run_proximity.sh` produit `proximity_scroll1.jsonl` | il appelait `python -m excision.proximity` qui ne résout plus, erreur avalée, code 0 | corrigé ; le fichier au bon rayon est écrit à part | tranché |
| `R2-C21` | `11` §1 : 158 feuilles, 11,2 m | `11` §3 : le maximum sur z informe (176, 13,87 m) ; le biais est à sens unique | moyenne → maximum | tranché |
| `R2-C22` | `11` §2 : borne supérieure | deux feuilles fondues comptent pour une | borne **inférieure** ; ordre de grandeur | tranché |
| `R2-C23` | `06` §7 / `11` §5 : 12 249 fusions | 125 murs sur 126 appariés ; 1 piste neuve par colonne | changements d'étiquette | tranché |
| `R2-C24` | `11` §5 : le glouton fragmente → Hongrois | 17 pistes longues contre 69 | l'optimalité globale n'est pas le bon objectif | tranché |
| `R2-C25` | `11` §8 : 0 coïncidence sur 21, indistinguable du hasard | coupes espacées de 22,3 mm ; fond stable à 6,4–7,0 % (20 σ) | à 0,8 mm : 7,0 % vs 1,1 %, p 0,0001 | tranché ; dose-effet |
| `R2-C26` | `11` §8 : p sur 20 000 tirages | les quatre artefacts portent `trials: 2000` | facteur dix | tranché |
| `R2-C27` | `11` §10 : rien ne coïncide au-delà de 0,8 mm = défauts d'un millimètre | `11` §11 : le défaut migre 1,50 mm/mm, la fenêtre fixe le perd | appariement prédictif ; 3 bras | tranché |
| `R2-C28` | `11` §11 : la rectitude discrimine | 1,000 observé, p 0,82 | trois points sont monotones une fois sur deux ; l'étendue tranche | tranché |
| `R2-C29` | `11` §12 (3 tranches) : marche de 4 % dès la plus petite perturbation | 6 tranches : 1,75 %, aucune marche | bruit d'échantillonnage ; même forme que fibres n = 12 et phase n = 8 | tranché |
| `R2-C30` | `17` §2 docstring : continuité entre voisines | le code prenait une cellule sur 40 | signal inversé = aucun signal | tranché |
| `R2-C31` | `17` §8 : refaire au niveau 0 ou 1 changerait peut-être tout | `17` §10 : le niveau 3 est le seul publié ; médiane des marches 12,2/255 | échec définitif | tranché |
| `R2-C32` | `34` §0 : la mesure existe dans l'arbre | `a5901be` a écrit `"lignes": []` par-dessus | restaurée depuis `79fba93`, image identique octet pour octet ; `sensibilite_maillage.sh` refuse d'écrire vide | tranché |
| `R2-C33` | `26` §9 : `step_size ≥ 20` rend une trace propre (zéros aux pas 15–40) | `34` §4 : `quads_dropped = 0`, `pairs_tested` non nul partout, donc pas de zéro muet ; mais pas 40 ne retrouve que 51 % | la règle tient ; ses zéros ne se valent pas | tranché (→ R3) |
| `R2-C34` | `75` D1 (4 sept.) : le remède du non-déterminisme est connu (`44`) | `07` §10 : testé, réfuté | politique gelée | tranché |

## R3 — 51 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R3-C01` | `16` (18 août) : espacement quantifié « 8 à 16 » puis « 7 à 12 voxels » | `16` refait (27 août) : 8,3–12,0 sur 108 sondes | les deux formulations étaient fausses ; le corpus est plus dur | tranché |
| `R3-C02` | `16` §6 : `0358` désigné par sa queue de 4 % | `33` : IC [0,1 ; 18,3 %], indistinguable du témoin ; campagne dense : 6ᵉ | choix par défaut, pas conclusion | tranché |
| `R3-C03` | `16`/`33` : la marge du prix « < 10 % » se lit en fenêtres | `33` §3 : c'est une fraction de surface | les 4–24 % ne se confrontent pas aux 10 % | tranché |
| `R3-C04` | `24` : les 240 auto-intersections viennent du champ de direction | `25` : de l'occupation à 1,000 de la graine | `30` : 13/14 tirages propres — c'était un tirage | tranché ; les deux diagnostics tombent |
| `R3-C05` | `25` §2 : la planéité ramène 240 → 0 et 8,48 → 19,82 cm² | `25` §2 : la même aire à six décimales sur deux rouleaux différents, gén. 119/120 | l'aire est le plafond du budget | tranché |
| `R3-C06` | `25` §5 : profondeur en fenêtre de 21 couches | `25` §5 : 21 couches = demi-pas, 61 % de profils plats | jambe retirée, refaite à 1,2 mm | tranché |
| `R3-C07` | `25` §5 : l'officiel du témoin transporte 2 % au tiers central | `36` : cet officiel n'était pas une référence | témoin changé (→ R1) | tranché |
| `R3-C08` | `26` §4 : le champ organise (densité ÷12) | `26` §4 : sans filtre `maxedge` la densité double | artefact du filtre ; mesure perdue par `a5901be`, restaurée | tranché ; rétracté |
| `R3-C09` | `26` : le README nomme dix poids `surface_sdt`/`spaceline` | `poids_growpatch.py` : douze, `sdt_weight`/`space_line_weight`, `NORMAL` pèse 10 et rend 0 sans grille | la table est dérivée du source | tranché |
| `R3-C10` | `26` §9bis : α dit que les quatre poids améliorent | tiers central : 32 % témoin contre 6–9 % | α comparait des bornes censurées (84,26 = 9 couches) | tranché |
| `R3-C11` | `24` §4 : `step_size` petit est plus propre | `26` §9 : 5 détruit (~800/cm²), ≥ 20 propre, 10–15 non reproductible | l'inverse ; et 10–15 est un tirage | tranché |
| `R3-C12` | `35` : « un test exact donne p ≈ 0,55 » | aucun producteur dans l'arbre | recalculé : p 0,10 | tranché ; anecdote retirée |
| `R3-C13` | `35` : dispersion 0,3 % vs 12,8 % sépare les rouleaux | `35` §3bis : à 400 gén. 0,55 → 86 % | confond du plafond (×40) | tranché |
| `R3-C14` | `37` : sélectionner sur la géométrie, valider sur la profondeur | 1 accord sur 8 ; condamné = meilleur sur 2/4 | sélectionner sur les deux ; puis `38` : distances sans objet | tranché |
| `R3-C15` | `38` matin : une spire / deux spires / la forme | `38` : α +1,01, l'écart suit la fenêtre | la mesure suivait le réglage | tranché |
| `R3-C16` | `38` : beaucoup de croisements = coupe l'empilement | `essai_scale1` 0 croisement α +0,99 ; `ng2` 112 139 → +0,65 ; l'officiel converge sans croisements | symptôme, jamais critère | tranché |
| `R3-C17` | `38` : `--flip-normals` teste l'hypothèse du sens de normale | A[k] = B[n−1−k] 41/41 octet pour octet | le drapeau renumérote la pile ; hypothèse inexprimable | tranché |
| `R3-C18` | `41` : « graine non couverte » (chunk `None`) | 19,3 % de matière ; `numcodecs` absent | panne d'installation prise pour un fait ; `decode` lève `CodecIndisponible` | tranché |
| `R3-C19` | `41` §6ter : sans les poids de données il ne reste que la géométrie | `thresholdedDistance` existe (terme de données non suivi) | « trop fort » ; deux leviers jamais essayés → `26` §9bis (dégradent) | tranché |
| `R3-C20` | `42` : 318 points corrigent | témoin +0,98, corrigé +1,03, 0 → 11 753 | change la trace, pas sa nature | tranché |
| `R3-C21` | `42` §7 : 187,24 µm = demi-fenêtre explique le tiers central | fenêtre valide de 19 couches (0,95 pas) : témoin 22 % bat toutes les corrections | fausse piste | tranché |
| `R3-C22` | `43` (3 tours) : le pas 0,5 ne change rien | 6/7 contre 4/7 au tour 7 | une chaîne se juge au tour où la référence cède | tranché ; publié faux |
| `R3-C23` | `43` : optimum au pas 0,25 | `neighbor_exit_count` × pas ; `exit_count 2` à 0,125 = 0,25 | c'est la portée, pas le pas | tranché |
| `R3-C24` | `43` : érosion 4,0 %/tour | `44` §5 : 15,6 % sur l'aire utile (58 → 23 % valides) | la grille compte des cases, pas de la matière | tranché |
| `R3-C25` | `43` : le rayon de courbure caractérise la chaîne | `44` §5 : deux estimateurs ×2, résidu 0,5 mm pour 0,113 | un cercle n'est pas un modèle | tranché ; refusé 9/9 |
| `R3-C26` | `44` §7 : enchaîner est strictement pire (×2,38) | 3 × 95 µm : ×1,01 comme le bond | c'était le pas ; l'alerte est le pas réel parcouru | tranché |
| `R3-C27` | `44` §7 : bond et chaîne se croisent à 1 920 µm | 35,4 % contre plancher 37,1 % : sous le hasard | deux mesures mortes | tranché ; rétracté |
| `R3-C28` | `44` §7 : zéro contact à 7,5 mm par extrapolation | 60 maillons : +6,9 à 5 760 µm, plateau | trop pessimiste | tranché |
| `R3-C29` | `44` §7 : la chaîne sort par le bord | sonde à marge de 5 cases : ne pouvait pas se déclencher ; corrigée : 0,1 % | écartée pour la bonne raison | tranché |
| `R3-C30` | `44` : `resume_generations` contrôle l'extension | variable locale, lue par personne ; le vrai bouton est `generations` | `spires_repousse` tournait à 100 gén. | tranché |
| `R3-C31` | `43` §6 : la repousse est établie | `44` : l'extension ×3 est un tirage sur trois | 17 essais `seed` renforcés ; repousse non établie | tranché |
| `R3-C32` | `44` : le seuil α vaut 0,70 | ailleurs 0,75 ; `spire04` +0,722 rend deux verdicts | seuil importé une fois ; 11/48 verdicts fragiles | tranché |
| `R3-C33` | `44` : 49 segments hors portée | 45 ≥ 318 µm + 4 hors portée | compte corrigé | tranché |
| `R3-C34` | `44` : le total des séries publié quatre fois le 21 août | `--depuis` recalcule ; 75 → 48 après dédoublonnage (`spire00` ×9) | écrit une seule fois | tranché |
| `R3-C35` | `47` : deux séries comparables | 92 séries disponibles (la cohorte) | « deux » = deux traces à deux profondeurs | tranché |
| `R3-C36` | `48` : « l'aval ne répond pas sur `1447` » | `60` : σ 76,4 %, ρ −0,01 | renversé (→ R1) | tranché |
| `R3-C37` | `48` : rendre coûtera plus de douze heures (57 Ko/s) | 1 108–5 861 Kio/s mesurés | extrapolation d'un seul échantillon de débit | tranché |
| `R3-C38` | `48` §7 : huit aires égales = coût du rendu | 0,3174–0,3176 cm² = plafond de la gén. 59 | un réglage pris pour un coût | tranché |
| `R3-C39` | `48` 2×2 : « c'est l'endroit » | `54` : les 8 cellules `m7` sont vides ; `51` : identité +1,0135 | non porté | tranché |
| `R3-C40` | `49` : le refus « max des amplitudes » juge la série | `51` : juste pour « y a-t-il quelque chose », faux pour « quelle pente » | appui au bord = borne | tranché |
| `R3-C41` | `50` : 60 vs 200 gén., α +0,89 → +0,95 | `51` : ces séries sont sans appui | « même calcul rend le même nombre » tient, « α » non | tranché |
| `R3-C42` | `51` : rendu 41/83 au niveau 2, α +1,06 | fenêtre paire asymétrique (182,4 = l'autre bord) | majorant ; `juger_serie` prend le plus large couple qui mesure | tranché |
| `R3-C43` | `51` §7 : seuil 2,25× du plancher | `52` : relief 0,046 → 0,146 de 1 024 à 256 px, exposant −0,830 | se compare à l'intérieur d'un instrument, jamais entre deux | tranché ; retiré du README |
| `R3-C44` | `52` : notre trace est plate (0,046) | à la géométrie du corpus : 0,1978, pas plate, mais 1ᵉʳ/80 | artefact de fenêtre en partie | tranché |
| `R3-C45` | `52` : `m7` rend 0,0000, coupure entre familles | `54` : rendus vides ; `m7_c0` lisible 0,1589 | coupure réfutée | tranché |
| `R3-C46` | `52` : « 65 couches » | `tracecheck` écrit `layers` : 109 | géométrie lue, pas supposée | tranché |
| `R3-C47` | `54` : cinq surfaces plates | cinq piles à max 0 ; `alive = peak >= floor × max` vrai sur des zéros | rendus vides ; pile vide refusée | tranché |
| `R3-C48` | `54` : le maillage suit le volume ouvert | il suit le repère de la **graine** (produit `-L2-`) | 4 913 blocs lus dans le mauvais repère, aucun refus | tranché |
| `R3-C49` | `54` : `voxelsize 2,4` pour `m7` | 9,6 réel ; aires ×16 | `min_area_cm` évalué dans deux unités | tranché |
| `R3-C50` | `53` : garde `find -path "*rendu*"` | prenait le maillage (119 px) | composant de chemin ; `GARDER_RENDU=1` | tranché |
| `R3-C51` | `44` : pas 0,25 = 9 nappes = presque un tour | ~10 % d'un tour par nappe ; deux nappes consécutives séparées par la circonférence | colonne, pas bande | tranché |

## R4 — 44 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R4-C01` | `77` §2 : « les deux populations ne se recouvrent pas » (propriété du prédicat) | `77` §7 : sur `0172` elles se recouvrent | `77` §8 : un trou de matière ; le prédicat rapporte sa `separation` par rouleau | tranché : propriété du **rouleau** |
| `R4-C02` | `77` §10 : référent à 23–38 µm ; Paris4 « à part » (37,7) | `77` §12 : le centre de masse enjambait deux feuilles | borné à ±0,5 écart : 17,8–23,8 µm, Paris4 dans la distribution | tranché |
| `R4-C03` | `77` §10 : Paris4 publie deux volumes à 7,91 µm | `77` (09-05) : cinq volumes, aucun à 7,91 ; 7,91 est le voxel de `0172` | `le_volume_du_maillage.py` : un seul volume contient le maillage de `44`, 2,400 µm | tranché ; `couverture_publiee.py` reconstructible |
| `R4-C04` | `laxe_nest_pas_une_ligne.py` : seul Scroll 1 publie un ombilic | `78` §0 : cinq rouleaux, sur le bucket | angle mort d'un seul serveur, 3ᵉ fois | tranché |
| `R4-C05` | `78` §2 : fibres en `nx/ny/nz` | `78` (09-05), `75` A2 bis : `nx/ny/presence`, niveaux 3–4 | ce qui borne est la résolution, pas `nz` | tranché |
| `R4-C06` | `la_portee_du_raccrochage` : borne oracle 6 | `82` : 6 = plafond du corpus sur 5/5 ancres | censure à droite ; borne ≥ 6 | tranché ; `81` §3 bis : le 6 n'est pas 13/2 |
| `R4-C07` | `85` : second régime de la bande du cœur (838 mm) | `90` : axe = courbe ; 460 mm | rétractation portée en tête de `85` | tranché |
| `R4-C08` | `91` (brouillon) : le pas quadruple au bord | `91` §4 : artefact de fenêtre | contrôle sur une seule bande de dix tours | tranché avant publication |
| `R4-C09` | `92` : sauts ↔ gonflement r = 0,80 | `92` §5 : retirer les lignes à saut change la pente de 0,2 % | corrélation ≠ mécanisme | tranché ; cause du gonflement **ouverte** |
| `R4-C10` | `93` (exploration) : désaligné au cœur, parallèle au bord | `93` §5 : les deux bandes comparées étaient dans le tiers intérieur | par tiers sur le corpus entier : U | tranché |
| `R4-C11` | `94` (brouillon) : la sagitta explique le pli en 1/R (accord 1,11) | `94` §5 : fixture → 0 là où la sagitta prédit 20,2 µm | gardée nommée | tranché |
| `R4-C12` | `94` attribuait le pli prédictif à `78` | c'est `75` (section « une cellule peut-elle savoir ») | citation non vérifiée = inventée | tranché |
| `R4-C13` | `75` A5 bis : « juger la chaîne par l'identité, expérience que personne ne pouvait poser » | `44` l'avait faite : la chaîne glisse | lecture des fiches, sur renvoi de l'auteur | tranché |
| `R4-C14` | `75` A5 bis : `44` mesure sur `1447` | `44` mesure sur `PHercParis4` (2,4 µm) | vérifié dans le code | tranché |
| `R4-C15` | `98` docstring : « le segment radial traverse l'empilement perpendiculairement » | `100` : la normale est à 34° du rayon | ce qui sauve `98` : le pas ne dépend pas de la direction (raison ouverte) | tranché, cause ouverte |
| `R4-C16` | `99` (brouillon) : le pas que la matière montre = 147 µm | le bruit pur rend 147 aussi | nul par candidat, comparaisons multiples → 198,9 | tranché |
| `R4-C17` | `99` : 198,9 µm (×1,15 nominal) | `105` : sélecteur biaisé +18,4 % ; corrigé 164,3 (×0,95) | `99`–`102` non recalculés ; le sens de l'écart s'inverse | tranché ; écart 164/182 **ouvert** |
| `R4-C18` | `100` : 1/cos explique l'écart (1,212 vs 1,213) | `100` §6 : rapport 1,018 vs 1,184 ; `106` : 1,000 vs 1,155 | coïncidence numérique | tranché ; anomalie **ouverte** |
| `R4-C19` | `102` : la matière porte 2,00 pas | `109` : run consécutif depuis le départ ; confirmés 4,0 | le compte ne peut pas dire « cinq sur six » | tranché ; portée → `113` |
| `R4-C20` | `102` : le critère confirme un pas | `104` : il confirme 0,68–1,38 feuille | `feuilles_franchies` (continu) | tranché |
| `R4-C21` | `107` : deux populations de la matière | `111` : surtout celles de l'instrument (bande relative) | mêmes échantillons, bande bornée : écart +0,965 → +0,134 | tranché ; le mode bas reste plus bas **en score** |
| `R4-C22` | `107` : « un seuil de score écarterait le bon mode » | `108` : c'est le score du **pas** qui sépare à l'endroit | `111` : ce score prédisait quand l'estimateur non borné perd le signal | tranché ; conséquence opérationnelle tombée |
| `R4-C23` | `107` : (1 − 0,105)^120 = 2·10⁻⁶ | `109` : suppose « manque = chute », réfuté | 18 confirmations manquées, pas une mort | tranché |
| `R4-C24` | `110` §4 : biais de −42 spires sur 120 | `110` §5 : mélange dont les proportions changent | partage par mode | tranché |
| `R4-C25` | `111` docstring : la barre monte avec la longueur | `111` §4 : elle baisse (pente −0,1149) | 1/√n l'emporte sur l'élargissement | tranché |
| `R4-C26` | `114` (brouillon) : témoin « décalé d'une spire », verdict OUI | `114` §5 : no-op par construction ; inégalité stricte | rotation de secteurs ; critère dérivé | tranché |
| `R4-C27` | `fusions_0172.json` : 12 249 fusions, 735 ruptures | `114` §1 : changements d'étiquette du tracker d'avant | ne plus citer comme fait sur le rouleau | tranché |
| `R4-C28` | `75` §C : le raccrochage gagne 33,3 µm sur un pas | `75` §C l. 1886 : à l'itération l'aveugle bat tous les raccrochages | le gain ne survit pas à un tour ; les normales, puis leur dispersion comme symptôme (4 soupçons écartés) | tranché |
| `R4-C29` | `75` §C l. 1905 : un décalage unique par tour déroule (−19,5 µm) | 494 cellules : +67,3 ; 906 : +56,3 | la boîte était un choix de coût | rétracté le jour même |
| `R4-C30` | `75` §C l. 2360 : la dérive accélère | le critère omettait l'incrément 0 → 1 (41,1 / 22,0 / 37,7 / 48,6) ; coût par tour stable 31,6–37,4 | erreur au bras k < k × bras 1 | rétracté |
| `R4-C31` | `75` §C l. 2665 : quatre affirmations sur la lecture du raccrochage | l. 2770 : `lecart_apparie.py` | trois tombent (gain 5,6 µm : −1,2 [enjambe 0] ; déplacement d'ensemble : +1,0), une est renforcée (oracle −23,8, 7/7) | tranché ; règle : différence de médianes → écart apparié |
| `R4-C32` | `75` §C l. 2932 : les deux tranches précédentes jugeaient le raccrochage | le critère mesuré n'était pas celui qui tourne (cellules au hasard, accord de voisinage inappelable) | déployé 37,5 vs 43,6 ; le gain est le voisinage | tranché |
| `R4-C33` | `75` §C l. 3137 : l'oracle de direction par cellule est une borne | l. 3267 : 96,6 % des cellules choisissent le **bord** du cône | plancher de balayage, pas une borne | tranché |
| `R4-C34` | `75` §C l. 3185 : la vérité est plate, donc lisser est la recette | l. 3313 : surfaces lisses par construction pires (+3,5 à +4,0) | nécessaire, jamais suffisant | tranché |
| `R4-C35` | `75` §C : le raccrochage déployé gagne (un pas) | l. 3453 : il porte 2 bras contre 4 (une marche) | deux questions : le meilleur pas ≠ aller le plus loin | tranché |
| `R4-C36` | `75` §C l. 3453 : fenêtre d'acceptation ±100,6 µm ; glissement 22 µm/bras | rectifié : ±67,8 µm (une demi-feuille exactement) ; 14 µm/bras | ce qui dérive est la somme | tranché |
| `R4-C37` | `75` §C l. 3616 : le pas normal ne glisse pas donc rien ne se compose | sa nappe se froisse par les normales (0 → 19,9 µm) | la mauvaise grandeur | tranché |
| `R4-C38` | `75` §C l. 6458 : refuser ses plis porte 5 (58,0 µm) | écart apparié sur les cellules communes +0,0 [0,0 ; 0,0] ; part gardée 0,453 | arbitrage couverture / justesse, pas gain de méthode | tranché |
| `R4-C39` | `75` §C l. 6498 : `rien_elague` et `rien_lisse_elague` mesurés | leur rugosité de champ était celle du raccrochage : ils tournaient dans la mauvaise branche | `FAMILLE_DU_PAS_NORMAL` + 2 contrôles | tranché (attrapé par une sortie de contrôle) |
| `R4-C40` | `75` §C l. 6610 : `median_8` optimal, −26 µm hors échantillon | l'optimum était au bord de la famille ; étendue à 16/32 ; l'ancre vivante passe de 5 à 0 bras | porte fermée par défaut : trois conditions | tranché |
| `R4-C41` | `31` §10 : la carte des 13 décide avec 50 fenêtres | `75` §C l. 3756 : 315× le budget ; puis l. 3836 : 0 rang de spire sur 13, pas exécutable | critère non mesurable, puis sans objet | tranché |
| `R4-C42` | `HANDOFF`:567 publie **1,213** sans record (`chiffres_sans_record`) ; `HANDOFF`:3210, :3222 `cd experiments`, `cd inference_xpu` (dossiers disparus) ; `86` §4 et les fiches lient `33_incertitude_de_la_carte.md`, qui n'a jamais existé (`33` s'appelle `la_carte_nest_pas_resolue`) | — | archive gelée : notés, non corrigés | à noter |
| `R4-C43` | `214` §6 : « le triangle SUR-DÉTERMINÉ réfute le modèle additif », pire résidu **3,6279 erreurs** sur `197-198` | `216` : ce résidu vaut **2,4281** une fois le budget d'erreur corrigé, et **4**/**19** tirages du modèle déclaré font aussi fort — la réfutation est un artefact de la formule d'erreur | les deux mesures sont justes ; c'est le DÉNOMINATEUR qui diffère, et `214` ne l'avait pas mis en procès | tranchée par `216` : `214` corrigé sur place par un renvoi, sa mesure et ses autres conclusions intactes |
| `R4-C44` | `239` §1 : la portée est « la plus longue traversée que `235` publie », de la première à la dernière coupe au-delà du demi-feuillet, **40** rangées | `245` : entre ces deux coupes, le cumul repasse en deçà aux coupes 183 et 193 ; ce sont deux traversées, dont la plus longue dure au plus **30** rangées, et une suite de coupes à 40 les évite toutes | la garantie de `239` reste exacte pour une traversée d'au moins 40 rangées ; c'est sa prémisse qui tombe : la traversée d'où la portée vient n'en est pas une | tranchée par `245` : la portée qui voit les traversées de `235` est **29** ; `239` et `243` coupent au-delà |

## R5 — 42 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R5-C01` | `56` §1.1 : les venvs pèsent 16,6 Go | compte de liens : 4,24 Gio réels, rien sans `uv cache prune` | trois `du -sh` séparés, et `du` ne voit pas les liens durs | tranché ; rétracté |
| `R5-C02` | `56` §1.1 : « le seul environnement qui porte Pillow » | la racine déclare `pillow>=10.0` ; `inference/` n'a **pas** `numcodecs` | les 25 sites étaient des emprunts à un environnement plus pauvre | tranché |
| `R5-C03` | `56` §1.1 : `inference/` reste, c'est le témoin CPU | l'auteur : le témoin doit être un **mode**, pas un dossier | deux dossiers = deux builds de torch, donc la comparaison mélangeait l'appareil et la build ; `--device auto/cpu` | tranché ; ma conclusion corrigée |
| `R5-C04` | `56` §1.1 : sept dossiers de scripts, donc deux dossiers et cinq environnements à la racine | `src/xpu/pyproject.toml` | un environnement n'a pas besoin d'être à la racine, il a besoin d'être **avec son code** | tranché |
| `R5-C05` | `56` §1.3 : 17,4 Go téléchargés en double | hachage réel : le proxy surcompte les chunks zarr homonymes **et** rate ce qui ne porte pas le même nom | 35,58 Gio, et ce ne sont pas les mêmes fichiers | tranché |
| `R5-C06` | `56` B : ranger `data/` par rouleau | `data/` gitignoré, 11/81 dossiers nomment un rouleau, 296 citations, 177 Gio | le plan cède ; la vraie question est « qu'effacer » | tranché ; chantier clos |
| `R5-C07` | `56` D : la purge de `.lances` garde 5 fichiers par script | premier passage : 197 → **4**, et le mécanisme n'a pas été reproduit | le remède n'est pas un meilleur motif mais un **plafond de refus** (50 %) | tranché ; perte réelle |
| `R5-C08` | `56` D : la fixture de la purge vérifie la rétention | elle demandait d'effacer 62 %, donc le plafond la bloquait | le contrôle mesurait le plafond en croyant mesurer la rétention | tranché |
| `R5-C09` | `56` C : `telecharger.py` est un orphelin | il est **importé** par trois modules | une bibliothèque ne se lance pas, elle s'utilise ; catégorie « importé » ajoutée (0/263 masque la stdlib) | tranché ; corrigé le 5 sept. |
| `R5-C10` | `56` C : `valider_blocs.py` a besoin d'un appelant | il a besoin de sa **référence** : le maillage fait 45 M de cellules | le 0,00025 est une valeur de bloc, pas une validation ; il lui faut un maillage assez petit | tranché |
| `R5-C11` | `56` D : le garde « scripts sans appelant » signale trois orphelins | silencieux au run suivant parce qu'un document venait de les nommer | une mention n'est pas un appelant — c'est même souvent le contraire | tranché |
| `R5-C12` | `56` D : `verifier_chiffres.py` lit ses 50 mesures | 44 littéraux séparés, chacun gardé par `if p.exists()` | un `docs/` rangé aurait fait sauter 50 sources **en restant vert** | tranché ; `DOSSIER_MESURES` + `_source()` |
| `R5-C13` | `56` D : `deplacer.py` refuse les citations pendantes | il refusait celles qu'il avait décidé exprès de ne pas réparer | un refus que personne ne peut satisfaire ; 125 chemins désormais **nommés** | tranché |
| `R5-C14` | `56` D : `verbes.json` est un registre | il est **produit** par `./lplv --verbes --json` | le classer en registre le mettrait hors de portée d'une purge de sorties | tranché |
| `R5-C15` | `57` §1.1 : `PHerc1667` n'est pas dans le corpus | `data/traces/PHerc1667/` existe avec ses 20 traces et ses 4 grilles | j'avais mesuré sur un autre corpus ; les nombres étaient justes et parlaient d'autre chose | tranché |
| `R5-C16` | `57` : « 36 fenêtres » contre « 72 » | l'un est le défaut de `--windows`, l'autre un compte réalisé | deux grandeurs qui portaient le même mot ; les deux outils doublent leur nominal | tranché |
| `R5-C17` | `42` : la correction fait passer α de +0,98 à +1,03, donc elle dégrade | les deux sont à 0,0375 et 0,0200 du plafond +1,0135, sous la résolution 0,20 | ni gain ni perte mesurés ; la vraie dégradation est 0 → 11 753 croisements | tranché (→ R3) |
| `R5-C18` | `57` : le rouleau de M1ter est `PHerc0172` | `36` §5bis : c'est `PHerc1447` ; `0172` est à 7,91 µm et n'est pas des treize | erreur de libellé | tranché |
| `R5-C19` | `61` : une batterie dont tous les `return` valent 0 ne peut pas échouer | le cas d'origine porte un `return 1` sur un refus d'argument | la règle qui décide est la sortie **qui suit le verdict imprimé** | tranché |
| `R5-C20` | `61` §3bis : la garde du verdict illisible cherche `ALL PASS` dans le fichier | satisfaite par le commentaire qui explique la règle et par la docstring | l'arbre syntaxique, et seulement les littéraux dans un `print` | tranché ; sonde muette |
| `R5-C21` | `62` §1 : la contention est écartée, 1586 % de CPU | la machine en offre **2200** | six cœurs faisaient autre chose : c'était exactement la contention déclarée écartée | tranché ; l'erreur qui a tout déclenché |
| `R5-C22` | `62` §2 : la falaise de cache explique l'écart | pas de coude à 3780 ; 6000 coûte moins que 4260 ; 0,167 ms contre 356,6 | réfutation par ordre de grandeur, ×2142 | tranché |
| `R5-C23` | `62` §1 : le segment 2 coûte ×4,6 du segment 1 | même crop : 0,132 → 0,5785 → 1,4616 selon ce qui tournait à côté | l'écart n'existe pas ; c'est un artefact de contention | tranché ; le §6 conservé pour ce qu'il dit de la méthode |
| `R5-C24` | `62` : la référence « machine libre » de `cout_du_rendu.py` vaut 0,635 | le même crop sur machine libre rend **1,4616** | cette référence était elle-même contendue ; sa colonne binaire ne pouvait pas le dire | tranché |
| `R5-C25` | `80` : est publieur tout module mentionnant `docs/mesures` | un pur lecteur n'a pas de nombre publié | le signe est l'**écriture**, sous ses deux formes | tranché ; portée resserrée |
| `R5-C26` | `80` : « 67 modules sur 67 ont leur tête de chemin dehors » | la couverture se propage vers le bas | c'est une identité, pas un constat ; retiré | tranché |
| `R5-C27` | `80` : « un corpus hors de la boîte est refusé » | seules les spires étaient déplacées ; le volume n'avait rien à lire là-bas | la mesure refusait pour **absence de matière** ; sonde verte | tranché ; deux matières déplacées ensemble |
| `R5-C28` | `80` : « une boîte plus large ne contient jamais moins de cellules » | un découpage inerte rend le même compte des deux côtés | inégalité devenue stricte (20 contre 196) | tranché |
| `R5-C29` | `87` : « aucun test n'est réellement fait » | 267/356 exposent `--verifier`, 0 batterie non enregistrée | la plainte est fausse sur ce point, et le corriger change les priorités | tranché |
| `R5-C30` | `87` : mon compte de batteries enregistrées vaut 0 | `Path(champ).name` sur une chaîne avec guillemets | et mon contrôle n'assertait que « c'est un entier » — une vérification incapable d'échouer dans le module qui les diagnostique | tranché |
| `R5-C31` | `87` : 348 artefacts nommés nulle part, puis 240 | la première ne captait que les chemins littéraux, la seconde ignorait la troncature | deux mesures jetées avant publication, gardées au journal | tranché |
| `R5-C32` | `88` : le run à sec signale 6 étages muets | rien n'avait tourné | un rapport qui signale l'absence d'un effet qu'il a lui-même empêché est pire qu'un rapport muet | tranché |
| `R5-C33` | `88` : ma sonde « valider au fil de l'eau » échoue comme il faut | elle passait les **trente** contrôles | je vérifiais que l'exception nomme le verbe, jamais que rien n'avait tourné | tranché |
| `R5-C34` | `89` : trois enregistrements créditent un fichier disparu | les trois PNG existent et sont commités | je testais « disparu » contre la liste **filtrée**, pas contre le disque | tranché |
| `R5-C35` | `89` : les barreaux couvrent tout le corpus | 3 + 1111 pour 1115 − 2, à une unité près | je soustrayais les exemptés en supposant qu'ils sont tous rencontrés — et l'unité manquante cachait une **exemption morte** | tranché |
| `R5-C36` | `75` D2 : le rapport « budget » n'est ni dans `docs/`, ni dans `src/`, ni dans `store/` | il est à `registres/anteriorite_resultats_de_tete.md:593` | j'avais cherché un fichier **nommé** « budget » au lieu du concept — la règle du dépôt, enfreinte par celui qui l'écrit | tranché |
| `R5-C37` | `75` D2 : le ×15,9 est vérifié par un script du scratchpad | ce fichier n'existe pas | un nombre publié dont le calcul n'est nulle part ; reproduit dans l'arbre (12 085 → 192 541, ×15,93) | tranché |
| `R5-C38` | `75` D2 : compter toutes les cellules, ou un seul plan, casserait la mesure | les deux sondes restent vertes | les trois plans déclarent les mêmes absents **sur ces grilles** — une propriété des données, désormais mesurée | tranché ; `concordance_des_plans` |
| `R5-C39` | `75` D3 : `juger_nappe.sh` est mort | il a été écrit pour dédupliquer deux copies qui avaient divergé | ni l'un ni l'autre ne l'appelle : c'est une **troisième** copie ; le remède est de l'adopter | tranché ; adopté le 4 sept. |
| `R5-C40` | `75` D3 : les trois copies de jugement sont équivalentes | `spire_suivante` n'avait pas la garde `REPLIEE` | il payait des rendus sur des surfaces manifestement repliées ; plafond rendu désactivable | tranché ; un refactor ne change pas le comportement |
| `R5-C41` | `75` D3 : `appelants.py` voit tous les appelants | aucune forme `. fichier` / `source fichier` | sourcer une bibliothèque shell, c'est l'exécuter | tranché |
| `R5-C42` | `75` D3 : le registre des fiches est à jour | 3 dérivées, 10 invisibles au motif, **10 documents sans fiche** ; puis 7 fiches invisibles à cause d'une ligne vide | un garde-fou ne doit pas dépendre d'un blanc ; le séparateur est capturé et recopié | tranché ; 81 fiches, 0 sans |

## R6 — 20 lignes

| id | A a dit | B a dit | C tranche | statut |
|---|---|---|---|---|
| `R6-C01` | `00` §2 (v1) : le spiral fitting est immunisé au sheet switching | `27` §2 : WJF 3,20 %, « wanders between two true windings » | correction écrite dans `00` le 08-19 | tranché |
| `R6-C02` | `27` (v1) : cible « 4 µm », citation paraphrasée | `27` §1 : 1,02 µm, verbatim | lecture intégrale | tranché ; règle : un résumé dit ce qu'un papier revendique |
| `R6-C03` | `27` §2 : AD 0,0568 vs 0,1567 (×2,76) | Thaumato aplatit avec SLIM → 0,0933 (×1,68) | lecture du texte | tranché |
| `R6-C04` | `00` §4 : « six vérificateurs, saturé » ; §9.3 : « n'existait dans aucun des six » | `67` : quatre équivalents dormaient dans leur code | audit des outils | tranché : juste sur les conclusions, faux sur le contenu |
| `R6-C05` | `66` : « nous n'avons rien découvert, juste des instruments » | l'article l'écrivait déjà (*« It measures »*) ; remarque de l'auteur | `66` §6 | tranché ; `deja_dit.py` |
| `R6-C06` | `66` recommandation : citer cinq dépôts | ils l'étaient (`windcheck` dans 20 docs) | vérifié le jour même | tranché ; auditer dedans avant dehors |
| `R6-C07` | (moi) : `selfgap.py` porte le test de convergence | `67` §6 : il mesure le détecteur, pas l'objet | audit | tranché ; s'accuser trop vite est aussi peu fondé |
| `R6-C08` | `68` §3 : F décide si la frange est résolue | `69` §1.1 : Paganin supprime les franges ; F = noyau en pixels ; bande perdue | calcul | tranché ; le rang de F tient, son sens change |
| `R6-C09` | `69` §6 : candidat `PHerc0826` (60 spires) | `73` §1 H6 : le pire des treize par la carte dense (22,8 %) | carte dense | tranché |
| `R6-C10` | `73` §1 H2 : courriel ESRF sans expérience | `73` (09-04) : `69` §1.2 chiffrait 1,3–1,5× ; C3 mesure 1,01 | mesure | tranché : courriel non justifié |
| `R6-C11` | `73` §2.3 : 113 µm = face à face (+ épaisseur) | `74` §2 : `43` — le rayon peut rentrer dans sa nappe ; 116 → 102 selon le réglage | source | tranché : valeur d'un réglage |
| `R6-C12` | `73` §4 : 57 segments, 2 rouleaux | `74` §3 : 101 segments, 3 rouleaux, 81 consécutives ; Paris4 58 plages | `les_indices_de_spire.py` | tranché |
| `R6-C13` | `73` §3.3 : extraire sur `0800` ou `1447` | `74` §4 : zéro indice ; `PHerc0139` porte les deux | mesure | tranché ; réserve : la queue ne prédit pas le traçage (`55`) |
| `R6-C14` | `73` §2.3 appuie sur l'atlas 172,8 µm | `74` §2 : 10 voxels entiers, IQR 121–250 ; appui = `16` (156) | lecture du CSV | tranché |
| `R6-C15` | `70` §5 : écrire l'arc excision | rejoué le jour même : la proximité baisse de 22–50 % | `07` refondé ; `75` D1 : `07` confirmée (0/10 au-delà du bruit) | tranché |
| `R6-C16` | `27` §4 : « corrigés ci-dessous » | rien ne suivait ; les corrections sont dans `06` | lecture | tranché (renvoi faux) |
| `R6-C17` | `71` : la doc de VC affirmerait « aucun seuil de distance ne sépare » | citation non retrouvée à la source | — | **ouvert** ; non citée |
| `R6-C18` | `66` : fold GP = `20231210121321` | nom du checkpoint : `20230702185753` | mesurer le modèle sur les deux segments | **ouvert** |
| `R6-C19` | `32` : v3 lue | une v4 existe (20 mai 2024) | — | ouvert (non lue) |
| `R6-C20` | `PRIX.md` : Stevens 20 000 $ sur la question de R4 | aucun document du dépôt ne le cite | — | à lire, à citer |

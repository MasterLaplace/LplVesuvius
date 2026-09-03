# Prompt pour Fable 5.1 — seconde passe : lis ce qu'on a fait, et dis-nous ce que ça change

> Tu as déjà répondu une fois. Ta réponse est dans ce dépôt, à
> `docs/69_reponse_dun_chercheur_exterieur.md`, et elle est bonne : elle corrige le cadrage du
> prompt sur deux points, elle chiffre le goulot à deux ou quatre années-personne par rouleau,
> elle pose sept hypothèses falsifiables et elle doute d'elle-même au §7.
>
> **Cette passe-ci te demande autre chose, et une seule chose.**

---

## 0. ⚠⚠⚠ LE CADRAGE — il manquait au premier prompt, et c'est la faute la plus chère

Il est dans ce dépôt depuis le 2026-08-17, l'auteur l'a redonné plusieurs fois, et **aucun des
deux prompts ne te l'avait transmis**. Le voici verbatim (`HANDOFF.md` §0 et §1) :

> **Le but est le DÉROULEMENT, pas la lecture.** Traduire n'est pas notre métier. Repérer
> quelques lettres sert à **s'assurer que le rouleau assemblé et déroulé fait du sens** —
> **l'encre est la règle graduée, pas l'ouvrage.**
>
> ⚠ **Pousser l'AUC plus haut, chercher un meilleur détecteur d'encre ou faire transcrire
> davantage NE SERT PAS l'objectif.**
>
> Le projet vise à **fermer la chaîne géométrique** : une pipeline assez intelligente pour
> cartographier un papyrus cabossé et carbonisé, **automatiquement**, puis **la leur donner à
> lancer**. Les **775 heures d'annotation** de l'état de l'art ne sont pas une barrière à
> l'entrée — **elles sont la cible à supprimer**.

Et c'est ce que le prix demande mot pour mot : *« The unrolling pipeline should be **fully
automated** »*, *« consider a **Docker image that we can easily run** »*.

### ⚠⚠ Ce que ça dit de ton rapport, mesuré

| | |
|---|---:|
| tes hypothèses portant sur la règle graduée | **3 clairement** (H1, H2, H7) **+ 1 discutable** (H3) |
| mois de ton plan consacrés à l'encre (mois 1, puis 6–8) | **4 sur 10** |
| titre de ton mois 1 | *« trancher la physique avant la géométrie »* |

⚠ H3 est comptée à part exprès, parce que le compte doit survivre à ton examen : son gain
déclaré est une *« scan-quality metric »*, donc côté règle, mais elle promet aussi une carte
co-localisée avec les régions où le **traçage** échoue — et ça, c'est le cœur du sujet. **Si tu
la réorientes vers ce second usage, elle change de camp**, et c'est peut-être le meilleur
arbitrage de tout ton rapport.

**Ton mois 1 titre l'inversion exacte du cadrage**, et tu ne pouvais pas le savoir. Ton §1.3
est pourtant juste et central — *« le goulot est géométrique, et il est dix fois plus large que
dans le papier »*, 2 à 4 années-personne par rouleau — mais ton plan ne le suit pas.

⚠ **Ce n'est pas un ordre de tout jeter.** Ton argument « mesurer la règle avant d'investir »
est légitime : si le régime du prix ne peut porter aucune encre, dérouler ces rouleaux-là ne
sert à rien. **Ce qu'on te demande, c'est de le défendre ou de le changer**, en sachant que le
critère du prix est *« 100 % du recto, colonnes visibles partout »* — donc une surface, pas une
lisibilité.

⚠ Et le biais vient de nous : le premier prompt mettait en tête le **nombre de Fresnel** et les
**103 cases vides**, deux résultats sur *si l'encre est lisible*, jamais sur *comment dérouler*.
Tu as suivi ce qu'on t'a montré.

---

## 0. Le constat qui justifie cette seconde passe

Mesuré sur ton propre document :

| | |
|---|---:|
| documents de ce dépôt que tu cites | **6 sur 74** |
| fois où tu cites l'article qu'on écrit | **0** |
| fois où tu nommes l'un de nos quatre résultats de tête | **0** |
| fois où tu nommes Hanley–McNeil, l'ICC ou Holm | **0** |

⚠ **Ce n'est pas un reproche, c'est un défaut du premier prompt**, et il est nommable : il te
donnait nos résultats **comme une liste d'hypothèses éliminées** — « ne repropose pas ça » —
donc comme des *contraintes sur ta recherche*, jamais comme *du travail à juger*. Il te
demandait d'élargir le champ. Tu l'as fait, remarquablement. Il ne t'a jamais demandé de
regarder ce qu'on avait construit.

⚠ Et il était déjà périmé quand tu l'as lu : trois des documents ci-dessous n'existaient pas,
l'article a gagné trois sections, et l'un de nos résultats a été **détruit** depuis.

**Ta mission cette fois : lire ce qu'on a fait, et dire ce que ça change à ce que tu as
écrit.** Pas de nouveau tour d'horizon. Pas de nouvelles analogies — les tiennes sont bonnes
et on les garde.

---

## 1. Ce qu'il faut lire, et ce que chaque chose contient

**En premier, et en entier :**

| quoi | pourquoi ça compte pour toi |
|---|---|
| **`docs/article/article.typ`** (27 p., 17 réf.) | ce qu'on publie. Tu ne l'as jamais ouvert. Sa §3 définit le test de convergence $\alpha$ que tu utilises neuf fois sans savoir ce qu'il ne distingue pas ; sa §6.2 est la couche statistique ; sa §6.7 est le pinceau et son fichier |
| **`docs/registres/fiches_de_lecture.md`** | les **70 documents lus intégralement**, une fiche chacun : nature, conclusions falsifiables avec leurs chiffres, **rétractations internes**. C'est le chemin le plus court vers tout ce que tu n'as pas lu, et il n'existait pas |
| **`docs/70_ce_que_larticle_condense.md`** | ce que l'article condense et ce qu'il laisse dehors, avec le compte |
| **`docs/71_les_trois_resultats_de_tete_audites.md`** | l'audit d'antériorité de nos trois résultats de tête. **PARTIELLEMENT** tous les trois |
| **`docs/72_le_second_papier.md`** | le cadrage du second papier — celui qui porte **ton** sujet, la physique du régime |

**Ensuite, ciblé** : `docs/17_saut_de_spire_par_la_phase.md`, `docs/51_une_pente_a_deux_appuis.md`, `docs/65_ce_que_sigma_ne_dit_pas.md`, `docs/07_reparee_nest_pas_propre.md` (son en-tête), `docs/46_le_temoin_negatif.md`.
Les raisons sont au §2.

⚠ Le registre des fiches s'arrête à `68` : les `70` à `73` se lisent en direct.

---

## 2. ⭐⭐ Deux collisions frontales avec tes hypothèses

Elles sont dans le dépôt depuis des semaines et le premier prompt ne te les a pas montrées.
**Je ne te dis pas qu'elles te réfutent — je te dis qu'il faut que tu juges.**

### 2.1 Ton **H5** contre notre `docs/17_saut_de_spire_par_la_phase.md` — un détecteur de saut de spire par la phase, essayé, mort

Ton H5 pose que les résidus du champ d'orientation prédisent les sauts de spire. Nous avons
essayé de détecter un saut de spire depuis la **phase d'enroulement publiée** (canal `cos` du
groupe `lasagna`), et le verdict est **définitif** :

> ρ **+0,517 (n = 8) → +0,306 (n = 30) → +0,149 (n = 38)**, p = 0,37.
> *« L'effet s'est évanoui à mesure que l'échantillon grandissait — ce qui est la signature de
> l'absence d'effet, pas d'un effet modeste. »*

⚠ Ce n'est **pas** ton H5 : la nôtre était une marche de phase entre cellules voisines, la
tienne est une charge topologique dans un champ intégré. Mais c'est exactement le doute que tu
écris toi-même au §7 — *« les résidus pourraient être partout où le champ d'orientation est
bruité […] A2 est un détecteur de bruit avec un beau nom »*. **Lis `17` en entier, y compris
son §10 qui ferme la dernière porte, et dis si H5 survit, et par quoi elle en diffère
mécaniquement.**

### 2.2 Ton **H1** contre notre `docs/65_ce_que_sigma_ne_dit_pas.md` — l'échelle a déjà été mesurée contre de vraies étiquettes

Ton H1 demande si l'évidence d'encre survit à la bande perdue, et propose de le mesurer par
passe-bas. **La moitié de cette expérience est déjà faite**, sur `PHercParis2Fr47`, contre les
`inklabels` du concours :

| pas | AUC groupée | IC 95 % par tuiles |
|---:|---:|---|
| 3,24 µm | 0,746 | [0,541 ; 0,788] |
| 6,48 µm | 0,693 | [0,468 ; 0,722] |
| 9,72 µm | 0,686 | [0,455 ; 0,745] |

⭐ Deux choses à en tirer, et elles tirent en sens opposés. Les **points** bougent à peine —
ce qui va dans le sens de ton H1. Mais **les trois intervalles contiennent ou frôlent 0,5** :
au niveau où l'incertitude est honnête (bootstrap par tuiles, parce que Hanley–McNeil est
**109 fois trop étroit** sur une carte auto-corrélée), **aucune des trois n'est distinguable
du hasard**. ⚠ Et c'est une **dégradation par décimation**, pas une acquisition native.

**Dis ce que ça fait à H1** : est-ce que ça la confirme, est-ce que ça dit surtout que
l'expérience est sous-dimensionnée, et **combien de tuiles faudrait-il** ? (`docs/64_la_dispersion_netait_pas_un_effet.md` dit qu'il
en faudrait 27 par fragment pour séparer un écart de 0,171 ; on en avait 10, 11 et 2.)

---

## 3. Ce qui a changé depuis que tu as écrit

- ⚠⚠ **Un de nos résultats est mort, et c'est celui sur lequel ton A5 s'appuie de loin.** Le
  `docs/07_reparee_nest_pas_propre.md` publiait que réparer une auto-intersection **ne déplace pas** la proximité anormale
  (0,37 → 0,38 %). En rendant le chiffre recalculable on a réparé une trace et remesuré : la
  proximité **baisse de 22 à 50 %**, et **pas proportionnellement à ce qui est retiré**. Ce qui
  survit du `07` : la corrélation ρ = +0,769 sur 46 traces à longueur contrôlée, et le rayon
  dérivé de la physique. Ce qui tombe : sa phrase-titre.
- **L'article a gagné trois sections** parce qu'il annonçait trois apports et n'en livrait
  qu'un : §6.2 (ce que coûte un point estimé), §6.6 (**un juge avec condition de contrôle** —
  16 panneaux, **zéro fabrication**, et la condition `vierge | vierge` qu'aucun protocole publié
  ne contient), §6.7 (le pinceau et son `approval.tif`).
- **L'audit d'antériorité** porte maintenant sur **17 résultats : 6 déjà connus, 11
  partiellement, aucun intact.** Le motif est constant et il te concerne : *le domaine publie
  les mécanismes et les questions ; ce qui résiste est la mesure, sa répétition, et son
  incertitude.*
- ⚠ **Trois défauts vivants corrigés**, dont un qui devrait t'intéresser : l'ombilic **est**
  publié (`dl.ash2txt.org`, 241 points) et il dit qu'**un axe de rouleau n'est pas une
  droite** — 21,6 mm d'errance sur 108 mm de hauteur. Ton §3.2 et ton A3 supposent un dépliage
  polaire autour d'un axe ; regarde `src/excision/laxe_nest_pas_une_ligne.py` avant de le
  poser.

---

## 4. Ce qu'on attend de toi, précisément

**Quatre livrables, dans cet ordre. Rien d'autre.**

1. **Révision de H1–H7 contre ce que tu viens de lire.** Pour chacune : *déjà répondue* /
   *moins chère que je le croyais* / *inchangée* / *morte*. Avec la mesure du dépôt qui tranche,
   citée par son fichier. ⭐ **C'est le livrable principal** : sept hypothèses dont plusieurs
   ont peut-être déjà leur réponse dans l'arbre.
2. **Ton avis de relecteur sur l'article.** Pas des compliments : *qu'est-ce qu'un relecteur
   adverse tue en premier ?* Sa thèse tient-elle ? Y a-t-il une affirmation que nos propres
   mesures contredisent ? Une limite qu'on ne déclare pas ? ⚠ Nous avons déjà trouvé qu'il
   promettait trois choses et en livrait une, et qu'il s'appuyait en silence sur deux mécanismes
   publiés par d'autres. **Trouve ce qu'on n'a pas trouvé.**
3. ⭐⭐ **Ton plan du §6, RÉPONDÉRÉ contre le cadrage du §0.** Quatre de tes dix mois et quatre
   de tes sept hypothèses portent sur la règle graduée. Deux réponses acceptables, et une seule
   inacceptable :
   - **tu défends la répartition** — dis pourquoi mesurer la règle d'abord est le chemin le plus
     court vers le déroulage, et **combien de temps** ça mérite vraiment (une semaine ? un
     mois ?) ;
   - **tu la changes** — et alors dis ce que devient le mois 1, et quelles hypothèses tu
     remplaces par des hypothèses **sur le traçage, l'approbation et l'aplatissement** ;
   - ⚠ ce qui n'est pas acceptable, c'est de laisser la répartition telle quelle sans la traiter.

   Et la question qui vaut le prix, posée franchement : **qu'est-ce qui remplace le pinceau ?**
   Ton H4 et ton A5 y touchent ; c'est là qu'on attend ton meilleur travail, pas sur l'AUC.
4. **Une chose qu'on n'a pas vue.** Une seule, la plus forte. Tu as un avantage qu'on n'a pas :
   tu lis notre travail **sans l'avoir fait**, donc sans le défendre.

---

## 5. Les règles, inchangées et non négociables

- **Marque chaque énoncé** : `[établi]` (lu dans une source citée, avec son chemin),
  `[calculé]` (arithmétique dans un script de l'arbre), `[conjecture]`, `[je ne sais pas]`.
  Tu l'as fait la première fois et c'est ce qui rend ton document utilisable.
- ⚠ **Cherche le CONCEPT, jamais le nom.** C'est la faute la plus chère de ce dépôt : 22 de nos
  98 outils existaient déjà sous un nom anglais qu'on n'avait pas cherché. Avant d'affirmer
  qu'une chose est neuve, cherche-la sous **trois** vocabulaires.
- **Une vérification qui ne peut pas échouer n'est pas une vérification.** Ce dépôt l'a payé
  cinq fois — dont une garde qui comptait **88 citations sur 140** parce qu'elle ne savait lire
  qu'un format sur trois, et une batterie de 39 tests sur 105 qui imprimaient « ALL PASS » et
  retournaient 0. Si tu proposes une mesure, dis **ce qui la ferait échouer**.
- **Un chiffre publié dont le calcul n'est pas dans l'arbre est une anecdote, pas un résultat.**

---

## 6. Où sont les choses

| | |
|---|---|
| l'article | `docs/article/article.typ` — et `README.md` à côté dit comment il est construit |
| les 70 fiches | `docs/registres/fiches_de_lecture.md` |
| les documents | `docs/NN_*.md`, 74 en tout ; `docs/00_carnet_de_bord.md` est la table |
| les mesures | `docs/mesures/*.json`, relues par `src/depot/verifier_chiffres.py` |
| les outils | `./lplv --help` liste **154 verbes** ; `./lplv <verbe> --help` rend son aide |
| la suite | `bash src/outils/temoins.sh` — **171 batteries, 4500 contrôles**, hors ligne |
| ta première réponse | `docs/69_reponse_dun_chercheur_exterieur.md` |

⚠ Le dépôt est **hors ligne par défaut** : les 35 dépôts du domaine sont clonés dans
`data/repos/`, le site est miroité dans `data/site/` (81 pages), et l'index du corpus est
`data/metadata.min.json`. Le réseau existe mais rien n'en dépend.

---

> ⭐ **Ce qu'on cherche vraiment.** Pas une validation. On a passé la session à découvrir que
> nos résultats étaient partiellement connus, qu'une de nos conclusions était fausse, et que
> deux de nos gardes ne voyaient pas ce qu'elles gardaient. **Ce dépôt se porte mieux quand on
> lui prouve qu'il a tort.** Si en lisant l'article tu penses qu'il ne vaut pas d'être publié,
> dis-le, et dis pourquoi.

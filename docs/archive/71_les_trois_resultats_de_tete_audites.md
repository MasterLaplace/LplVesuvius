# 71 — Les trois résultats de tête, audités pour antériorité

> ⚠⚠ [`70`](70_ce_que_larticle_condense.md) §5 nommait la seule tâche à faire avant tout
> envoi : **trois des quatre résultats de tête de l'article n'avaient jamais été audités**.
> Aucune des 14 clés de [`66`](66_audit_danteriorite.md) ne les couvrait. C'est fait.
>
> **Les trois rendent PARTIELLEMENT.** Aucun n'est un doublon, aucun n'est intact.

Trois agents adversariaux, un par résultat, cadrés pour **réfuter**. Rapports intégraux :
[`registres/anteriorite_resultats_de_tete.md`](registres/anteriorite_resultats_de_tete.md).
⚠ Les citations qui portent une correction de l'article ont été **revérifiées à la source**
par moi, ligne par ligne, avant d'être écrites — c'est la discipline qui a payé cinq fois
cette session.

---

## 1. « Le traceur est un tirage » (§5.1) — le mécanisme était sous nos yeux

⭐ **Le mécanisme est dans le code publié, littéralement**, et l'article ne le nommait pas :

    apps/src/vc_grow_seg_from_seed.cpp:357     srand(clock());
    core/src/GrowPatch.cpp:99-108              std::mt19937(std::random_device{}())

⚠ **Et une phrase de l'article était attaquable** : « draws from an **unseeded** generator ».
C'est vrai **par défaut**, mais `VC_GROWPATCH_RNG_SEED` existe — donc le comportement est
connu de ses auteurs. L'article dit désormais « unseeded *by default* » et note l'échappatoire.

⭐⭐ **Et l'audit a trouvé un argument à RÉCUPÉRER, pas à craindre.** La documentation
officielle publie que le vérificateur est déterministe : *« Two runs on the same surface
produce identical reports regardless of thread count »*, et `windcheck` le remesure sur neuf
configurations. **Donc une bascule de verdict ne peut pas venir de l'instrument** — elle
prouve que la surface a changé. C'est une garantie de l'amont qui rend notre observable plus
fort, et l'article la cite maintenant.

**Ce qui reste sans équivalent** : la mesure (78 exécutions, 0/13 rendant deux fois la même
aire, 5/13 basculant, 5/78 = 6,4 %) ; la **bascule de verdict** comme observable — personne
ne compare des verdicts, on compare des comptes ou des hachages ; et le fait que l'aire ne
signale pas le mauvais tirage.

---

## 2. « La stabilité et la propreté sont des artefacts du budget » (§5.2) — une moitié était publiée

⚠⚠⚠ **La moitié « propreté » est DÉJÀ PUBLIÉE, quantifiée, sur 278 traces**, et presque mot
pour mot. `windcheck/docs/FULL-CORPUS.md` :

> *« a larger surface has more opportunities to fold through itself; **a small trace is clean
> substantially because it is small** […] the 86% figure published for the original five
> samples **is not a property of those samples** — it is what happens when you trace large
> surfaces. »*

L'article écrivait « *The traces were clean because they were short* » et « *It was not a
property of the scroll* ». ⚠ C'est l'omission qu'un relecteur adverse trouve en premier,
d'autant que l'article cite `windcheck` **trois fois** pour d'autres vertus.

**Corrigé** : la moitié propreté est présentée comme une **confirmation intra-instance** d'une
loi publiée, avec sa citation. Ce que notre dessin ajoute est le **sens de l'inférence** —
leur loi est transversale sur des tailles réalisées, la nôtre change le budget *sur le même
rouleau, tout le reste égal*, donc la taille cesse d'être une propriété de l'objet.

⭐ **Et la moitié « stabilité » ne trouve rien**, pour une raison que l'audit établit :
**personne ne tire le traceur plusieurs fois à configuration identique pour en mesurer
l'étalement.** C'est le cœur défendable de la section.

---

## 3. « Les segments ne pavent pas une feuille » (§5.7) — l'idée et le discriminant sont antérieurs

⚠⚠ **Trois composants sur quatre sont antérieurs**, et le tutoriel officiel porte la prémisse
en tête :

> *« all produce **patches** — pieces of papyrus surface […] you end up with a big pile of
> small pieces […] **gluing the pieces together directly is hard, especially where there are
> gaps between them.** »* — et sa note sur le traceur : *« it **requires the patches to
> physically overlap or touch** »*.

⚠ **Le discriminant aussi** : `QuadSurface::overlap()` traite la boîte englobante comme un
rejet bon marché puis décide sur une **distance point-à-surface de deux voxels**. Le
présenter comme notre discriminant n'était pas défendable.

**Ce qui survit, et c'est plus étroit que la formulation d'avant** : le **recensement**. Les
antérieurs mesurent 6 paires, 150 paires échantillonnées, 9 fenêtres — personne n'a fait **les
105 paires d'un rouleau**, et `PHerc1447` n'apparaît même pas dans le papier de référence. Et
la formulation « **une pièce par feuille** » est absente du corpus, qui dit « sparse »,
« scattered », « pieces with gaps » — la nôtre est plus forte et plus falsifiable.

**Corrigé** : la section s'ouvre en créditant la prémisse et le discriminant, et s'annonce
comme *un recensement*, pas comme une méthode.

---

## 4. ⚠ Ce qui reste ouvert après cet audit

- **La contre-position du rapport « pavage »** — la doc de `volume-cartographer` affirmerait
  qu'aucun seuil de distance fixe ne sépare les feuilles, ce qui viserait notre seuil de
  40 µm. ⚠ **Je n'ai pas retrouvé cette citation à la source** avec les motifs essayés, donc
  elle n'est **pas** reprise dans l'article et reste à vérifier. Une antériorité qu'on ne peut
  pas citer ne se cite pas.
- **Le contrôle P1 bis** du rapport « budget » : le budget exigerait ×15,9 de cellules là où
  ×3,8 est observé. Si l'hypothèse tient, le budget fait plus que grandir la surface — et ça,
  `windcheck` ne le dit pas. À faire tourner sur nos propres grilles.

---

**Verdict global, à ajouter aux 14 de `66`** : 17 résultats audités, **6 déjà connus,
11 partiellement**, aucun intact et aucun sans valeur. Le motif tient sur les trois nouveaux
comme sur les quatorze anciens : **le domaine publie les mécanismes et les questions ; ce qui
résiste est la mesure, sa répétition, et son incertitude.**

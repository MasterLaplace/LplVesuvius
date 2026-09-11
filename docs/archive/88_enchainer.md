# 88 — La composition, et la provenance devient un fait observé

> ⭐⭐⭐ **`lplv` nomme 190 greffons et n'en composait aucun. `lplv enchainer <chaîne>` les
> enchaîne, s'arrête à la première panne, et OBSERVE quel verbe a écrit quel fichier — donc la
> provenance devient un fait mesuré, sans une seule déclaration à maintenir.**

Mesuré sur la première chaîne réelle : **6/6 étages en 2,71 s**, et **6 artefacts attribués au
verbe exact qui les a écrits** — trois `.json` et trois `.png`.

## 1. Pourquoi la composition résout la provenance mieux que la déclaration

[`87`](87_la_forme_du_depot.md) mesure que `artefacts_orphelins` déclare « 0 orphelin » avec
**46 % de son verdict reposant sur une tige de ≤12 caractères** — `juge_scroll4.json` est déclaré
produit parce que le mot `juge` apparaît quelque part dans `src/`.

Le remède évident était de faire **déclarer** à chaque module ce qu'il produit. La mesure a montré
le prix :

| les 486 artefacts | |
|---|---:|
| nom entier présent dans un module → un littéral suffirait | **172 (35 %)** |
| ⚠ exigeraient un **motif écrit à la main** | **314 (65 %)** |
| ⚠⚠ nommés par **plusieurs** modules (un lit, un écrit) | **105** |

⭐⭐⭐ **Une chaîne qui tourne fait mieux qu'une déclaration : elle OBSERVE.** Inventaire des
racines surveillées avant et après chaque étage, puis différence. Aucun motif, aucune troncature,
rien à tenir à jour — et les 105 ambiguïtés disparaissent, puisque seul l'étage qui a écrit est
crédité.

## 2. Le dessin, et ses quatre décisions

**`subprocess` et non `os.execvp`**, et la différence est délibérée : `lplv <verbe>` utilise
`execvp` pour que le code de sortie, les signaux et le terminal soient ceux du verbe. Une chaîne ne
peut pas — un processus remplacé ne revient jamais, donc un seul étage tournerait. Le prix est un
maillon qui pourrait avaler un code de retour, d'où le code de sortie de chaque étage
**enregistré** plutôt que consulté au vol.

⚠⚠⚠ **La chaîne entière est validée AVANT que le premier étage ne tourne.** Une coquille à la
cinquième ligne ne doit pas coûter les quatre étages du dessus. C'est le seul endroit où un lanceur
peut être poli.

⚠⚠ **« Créé » et « modifié » sont deux listes, pas une** : un étage qui régénère un artefact
existant fait autre chose qu'un étage qui en produit un neuf.

⚠ **La portée de l'observation voyage avec le résultat.** `data/` en est absent délibérément —
98 275 fichiers, 168 Gio, son inventaire coûterait plus que les étages. Donc un étage est rapporté
« rien écrit **parmi les racines observées** », jamais « rien écrit ».

## 3. ⚠⚠ Ce qui n'est PAS fait, et c'est une décision

Ni parallélisme, ni cache, ni reprise, ni réessai. `concevoir-avant-coder` §2 : une couche se
construit quand un **compteur** montre ce que la couche du dessous laisse passer. Le lanceur compte
donc les étages, leur durée et leurs artefacts — et les couches viendront de ces chiffres, ou ne
viendront pas. Construites d'avance, on obtient cinq couches dont trois ne servent jamais et qu'on
ne peut plus retirer.

⭐ Et **le lanceur est lui-même un greffon** : il vit dans `src/depot/`, donc `lplv` le découvre
comme les 190 autres. L'architecture reste cohérente avec elle-même, et un contrôle l'asserte.

## 4. Les deux premières chaînes, et pourquoi elles existent

| chaîne | ce qu'elle rejoue |
|---|---|
| `docs/chaines/les_spires_publiees.chaine` | les six étages de [`84`](84_une_surface_combien_de_spires.md), [`85`](85_le_sens_du_rang.md) et [`86`](86_la_demi_feuille_par_objet.md), **dont deux téléchargements** |
| `docs/chaines/les_gardes_de_larbre.chaine` | les quatre gardes qui parcourent tout l'arbre |

⚠ Les deux ont été lancées **à la main dans un terminal** le 2026-09-08 — six modules dans le bon
ordre, plus un `until` de surveillance réécrit à chaque fois, et un `pkill -f` mal fermé qui a tué
le shell qui les attendait. **Une commande tapée dans un terminal est perdue au prochain shell** ;
c'est exactement ce que ces deux fichiers réparent, et l'ordre des étages y porte sa raison.

## 5. ⚠⚠ Deux fautes à moi, trouvées par mes propres sondes

**Un faux signal.** Le run à sec annonçait **6 étages muets** — or rien n'avait tourné, donc « n'a
rien écrit » signalait l'absence d'un effet que le run à sec avait lui-même empêché. Un rapport qui
fait ça est pire qu'un rapport muet.

⚠⚠⚠ **Et un contrôle qui ne testait pas ce qu'il prétendait.** Ma sonde « valider au fil de l'eau
au lieu d'en amont » **passait les trente contrôles** : je vérifiais que l'exception nomme le verbe
fautif, jamais que **rien n'avait tourné**. La forme falsifiable est celle-ci — une chaîne dont le
premier étage écrit et le second verbe est inconnu doit laisser le disque **intact**. Réécrit
ainsi, la sonde échoue comme elle doit.

## 6. Ce que ça débloque, et ce qui reste

⭐⭐ **La provenance observée peut remplacer la troncature.** `artefacts_orphelins` pourrait lire
les enregistrements de chaîne et n'avoir à deviner que pour ce qu'aucune chaîne n'a jamais produit
— le décompte deviendrait alors visible et ne pourrait que rétrécir. C'est la tranche suivante, et
elle touche une garde, donc elle est à part.

⚠ Reste hors périmètre : les **21** artefacts produits par un `.sh` de `campagnes/`, et les **588**
`.json` versionnés hors de `docs/mesures/`.

## Reproduire

```
uv run python src/depot/enchainer.py --verifier
uv run python src/depot/enchainer.py docs/chaines/les_spires_publiees.chaine --sec
uv run python src/depot/enchainer.py docs/chaines/les_spires_publiees.chaine \
    --json docs/mesures/enchainer_les_spires_publiees.json
lplv enchainer docs/chaines/les_gardes_de_larbre.chaine
```

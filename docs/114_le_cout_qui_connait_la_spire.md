# 114 — Le coût qui connaît la spire, et le faux champ qui en obtient autant

> ⛔⛔ **La réouverture était légitime, et la réponse est NON.** Brancher l'indice
> d'enroulement dans le coût du tracker fait tomber la fragmentation de
> **99.12** à **96.14** morceaux
> par mur — mais le **champ TOURNÉ**, faux par construction, obtient
> **96.64**, soit
> **83 %** de la descente. Ce qui
> travaille est l'existence d'une pénalité, pas l'identité qu'elle porte.
>
> ⛔ **La part SPÉCIFIQUE vaut 0.50 morceau** sur les
> **98.1** à supprimer pour tracer une feuille d'un bout à l'autre —
> **0.5 % du chemin**.
>
> ⭐ **Et la condition de mort est passée, ce qui rend le non informatif.** Mesuré secteur par
> secteur sur **2342** pas, un indice de spire publié vaut
> **1.006** feuille : le champ distingue bien à la résolution de la
> feuille. L'instrument est bon, et il ne sauve pas le tracker.
>
> ⚠⚠ **Trois défauts à moi, tous attrapés par une sonde et aucun par relecture** : un témoin
> qui était un **no-op par construction**, une métrique de tête **dégénérée**, et un verdict
> qui a imprimé OUI pendant que le faux champ prenait 83 % du gain.

![le coût qui connaît la spire](images/114_le_cout_qui_connait_la_spire.png)

## 1. Pourquoi ce fichier rouvre une cause éliminée

`fusions` a posé trois hypothèses sur la fragmentation de son tracker et **les trois ont été
réfutées** — affectation globale : pire ; pistes en sursis : innocentes ; détecteur : 92 % des
murs retrouvés à moins de deux voxels. La cause réelle qu'il a mesurée est ailleurs :

> *« 125 murs sur 126 sont appariés à chaque colonne, donc la couverture est quasi parfaite et
> c'est l'**IDENTITÉ** des pistes qui churne. Les « fusions » comptées comme des morts de piste
> étaient des **changements d'étiquette**. »*

⚠ **Conséquence à retenir avant tout le reste** : les **12 249 « fusions »** de
`docs/mesures/fusions_0172.json` ne sont pas des événements de matière. C'est la sortie du
tracker d'avant le correctif de pente, sur une coupe qui compte **158 feuilles**. Ce chiffre ne
doit plus être cité comme un fait sur le rouleau.

**Ce qui a changé depuis, et c'est la condition de réouverture de [`55`](55_les_murs_et_leurs_causes.md).**
Le coût du tracker n'apparie que sur **une** quantité :

```python
predicted = tracks[t]["radius"] + tracks[t]["slope"] * (1 + tracks[t]["missed"])
cost = np.abs(predicted[:, None] - found[None, :])
```

Aucun indice de spire. Et son propre commentaire nomme le mode de panne qu'il ne peut
qu'**interdire** par une tolérance : *« un coût fini laisserait l'optimum global **sauter une
spire** pour gagner ailleurs »*.

L'instrument qui donnerait cette seconde coordonnée —
[`le_champ_denroulement`](../src/excision/le_champ_denroulement.py), indice d'enroulement
continu validé à spire exclue — a été construit **le 4 septembre**, soit trois semaines **après**
la dernière mesure du tracker. `55` exige une mesure neuve pour rouvrir une cause éliminée ;
c'en est une.

## 2. ⭐ La condition de mort, et elle est passée

Si un indice de spire publié valait **deux** feuilles, le champ ne serait qu'une étiquette de
bande grossière et ne pourrait pas départager deux pistes voisines — c'est-à-dire exactement ce
qu'on lui demande. La tranche se serait arrêtée là.

| | voxels | µm |
|---|---:|---:|
| écart inter-feuilles (`76`, PHerc0172) | 18,6 | 147,4 |
| pas d'indice médian, mesuré | 18.7 | 148 |

**1.006 feuille par pas d'indice**, sur **2342** pas.

⚠⚠ **Mesuré SECTEUR PAR SECTEUR, et la première sonde ne l'était pas.** Chaque patch publié
couvre un secteur angulaire différent, donc comparer deux spires sur l'ensemble des angles
compare des angles différents : une médiane tous angles confondus rendait **six pas négatifs sur
quarante-trois** — impossible pour une spirale, et sans rapport avec le champ. Secteur par
secteur il en reste **78 sur 2342**, soit
3.3 %.

⚠ **Exiger zéro pas négatif serait exiger que le rouleau soit rond.** Un pas négatif dit qu'à
cet angle la spire suivante est à un rayon *plus petit* — ce qu'une section écrasée fait
réellement là où elle se replie. Ma batterie l'exigeait et échouait ; c'est l'assertion qui
avait tort.

## 3. ⚠⚠ Le champ est reconstruit dans le repère de la polaire

Le champ publié travaille avec un centre ajusté par tranche de hauteur ; la polaire est dépliée
autour de l'ombilic de `data/axes/`. Les deux diffèrent, et **un décalage de centre déplace le
rayon d'un mur autant qu'il déplace son angle** — c'est-à-dire exactement la quantité que le
tracker apparie. Emprunter la table telle quelle rendrait des indices parfaitement valides pris
ailleurs dans le rouleau, ce qui ne lève rien et ne ressemble pas à une erreur.

Les rayons sont donc recalculés depuis les nuages de points avec le centre **de la polaire**.

⚠ Et deux seuils de ma première version étaient bien plus stricts que l'instrument réutilisé :
**100 points par cellule** contre `POINTS_MINIMUM = 10`, et une demi-tranche de **50 voxels**
contre les **258 voxels** (12 380 ÷ 24 ÷ 2) que `TRANCHES_Z = 24` découpe sur l'étendue des nuages.
Résultat : **11 secteurs sur 72** répondaient — ce qui ne se lit pas comme un paramètre trop
serré mais comme un champ qui ne couvre pas le rouleau. Alignés : **72/72**.

## 4. ⛔⛔ Le résultat

Bande `r ∈ [1563, 3000]` voxels — **47.9 %** du rayon —
**18850** colonnes angulaires, **72** murs par colonne.

| variante | morceaux par mur | gain |
|---|---:|---:|
| témoin (tracker livré) | 99.12 | — |
| **champ d'enroulement** | 96.14 | **−2.99** |
| champ constant | 99.12 | −0.00 |
| **champ TOURNÉ (faux)** | 96.64 | **−2.49** |

Le champ **constant** ne fait rien du tout, et c'est correct : il rend le même indice partout,
donc un écart nul partout. Il vaut d'exister — il prouve que le peu qui bouge vient de la
**variation** du champ et non d'un terme de plus dans le coût.

Le champ **tourné** prend **83 %** de la
descente. Part spécifique : **0.50** morceau sur
**98.1**.

⚠ Et `traversantes` vaut **0** pour toutes les variantes : aucune piste
ne traverse même 90 % du balayage. Une feuille reste coupée en ~99
morceaux.

## 5. ⚠⚠⚠ Trois défauts à moi, et aucun trouvé en relisant

1. **Mon témoin « décalé d'une spire » était un no-op par construction.** Le coût ne lit que
   `|indice de la piste − indice du mur|` : ajouter 1 aux deux le laisse inchangé. Il rendait
   **exactement** le même nombre que le vrai champ — 6,09 contre 6,09 — ce qui se lit *« décaler
   ne nuit pas »* alors que **rien n'avait été décalé**. Remplacé par une **rotation** de
   secteurs, qui donne un champ ayant toutes les statistiques du vrai et aucune de ses
   correspondances.
2. **Ma métrique de tête était dégénérée.** `traversantes` valait zéro pour les quatre
   variantes : une quantité qui ne peut pas prendre la valeur signalant le succès. Remplacée par
   les **morceaux par mur**, publiée avec `traversantes` à côté.
3. **Mon premier verdict a imprimé OUI.** Il testait `gain_tourné < gain_champ` — une inégalité
   stricte entre flottants que le bruit satisfait presque toujours — pendant que le faux champ
   prenait 83 % du gain. Le critère est refait et **dérivé** : *si un champ délibérément faux
   obtient plus que la part spécifique du vrai, alors ce qui travaille est l'existence d'une
   pénalité.*

⚠ Plus deux seuils de témoin **choisis** au lieu d'être dérivés : « zéro pas radial négatif »
(§2) et « 90 % des colonnes sondées diffèrent ». Le second est réancré sur la borne de la
contrainte elle-même — le coût interdit au-delà de **0.5** spire, donc un faux
champ n'est utilisable comme faux que s'il désaccorde de plus que ça. Mesuré : **écart médian
13,44 spire**.

⚠ Et un troisième piège de figure, de la même famille que `⭐`/`★` : **`⛔` n'est pas dans la
police déployée**. La garde `prose_tracable` l'a attrapé avant publication ; les huit autres
figures qui portent ce caractère ne le **dessinent** pas, elles le commentent, et leurs
batteries restent vertes.

## 6. ⚠ Ce que cette tranche ne dit pas

1. **La moitié intérieure n'est pas couverte.** Les spires publiées de PHerc0172 occupent
   `r ∈ [1536, 3293]` voxels à cette hauteur ; la polaire porte `0..3000`. Le **cœur** — là où
   `fusions` note que le comptage rendait *« une carte de la faiblesse du détecteur »* — reste
   hors de portée.
2. **Un seul objet, une seule hauteur** : PHerc0172, z = 6967.
3. **Rien sur la 3D.** Une coupe polaire est un plan ; les 775 heures sont dépensées sur des
   **surfaces**. Ce fichier mesure si l'identité tient dans le plan — pas si elle porte.
4. **Un seul jeu de réglages** (`poids = 4.0`, `ecart_max = 0.5`). Un
   balayage pourrait déplacer les chiffres ; il ne peut pas déplacer le fait que le faux champ
   suit le vrai, qui est ce que la tranche établit.

## 7. Ce que ça laisse ouvert

Dans une coupe polaire, l'identité **ne se récupère pas** en ajoutant une coordonnée
d'enroulement à une affectation colonne par colonne. La question retourne donc là où elle avait
sa place : **en 3D**, où un « bout » n'est pas la fin d'une piste mais la **bordure d'une
nappe**, et où la conservation de matière s'écrit comme une conservation de flot à chaque
jonction plutôt que comme un appariement de points.

## Reproduire

```bash
uv run python src/excision/le_cout_qui_connait_la_spire.py --verifier
uv run python src/excision/le_cout_qui_connait_la_spire.py \
    --json docs/mesures/le_cout_qui_connait_la_spire.json
uv run python src/figures/figure_le_cout_qui_connait_la_spire.py --verifier
```

⚠ La course complète tient en **29 s** et ne lit **rien à distance** : la polaire
(`data/out/polaire_0172.npy`, 3000 × 18 850) et les nuages de spires sont en cache.

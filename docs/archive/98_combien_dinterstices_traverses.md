# 98 — Combien d'interstices entre une cellule et sa voisine ? Le critère que la matière tranche

> ⭐⭐⭐ **Le premier critère dont le seuil ne vient ni d'un maillage ni d'un réglage.** `97` a
> mesuré que deux tracés humains indépendants de la même matière divergent de plus d'une
> demi-feuille partout : **aucun signal calibré contre un maillage humain ne peut donc l'être**.
> Il fallait un critère que la **matière** tranche, et il s'énonce en une phrase — entre une
> cellule et le point situé un pas de feuille plus loin, le profil doit valoir *brillant – sombre
> – brillant* : exactement **un** interstice.
>
> ⚠⚠ Signe correct (**−0,411** avec la rupture de continuité) mais **faible** : au bord l'accord
> vaut **0,353** contre une barre de **0,3311**. Là où la réponse compte le plus, la matière est
> presque muette.

![combien d'interstices traversés](../images/98_combien_dinterstices_traverses.png)

## 1. Pourquoi il fallait sortir des maillages

Quatre tranches ont fermé la question du signal de confiance. Le **pli** (`94`) et la **pose sur
la matière** (`95`) sont anti-prédictifs ; la **fermeture d'un tour** (`96`) a le bon signe mais
aucun étalon ; et `97` a mesuré pourquoi — deux tracés humains **indépendants** de la même matière
divergent de **plus d'une demi-feuille partout**, et de plus d'une feuille entière sur un tiers
des points.

> **Aucun signal mesuré contre un maillage humain ne peut être calibré, parce que le maillage
> humain n'a pas de valeur unique.**

## 2. ⚠⚠⚠ La question de l'auteur, et pourquoi la réponse n'est pas « adapter le seuil »

*« Il faut être adaptatif par rapport au rouleau testé, non ? »* — oui, et la mesure rend la
question plus forte qu'elle ne l'annonçait. Dans **une seule bande du bord**, l'étendue du profil
d'intensité varie d'un facteur **146** (p10 = 0, p90 = 146 niveaux), et d'un facteur **2,4** au
milieu. Un seuil absolu de « sombre » est donc sans espoir, et une constante **par rouleau**
serait déjà un paramètre ajusté.

⭐ Mais la bonne réponse n'est pas d'adapter le seuil : c'est de **choisir une quantité qui n'en a
pas besoin**. Une **corrélation normalisée** à un gabarit est invariante en amplitude **et** en
décalage. Il n'y a donc rien à adapter — ni au rouleau, ni à la bande, ni au profil.

⚠ Vérifié plutôt que supposé : multiplier signal **et** bruit par 0,05 puis par 50 laisse le score
**identique au bit près**. Et le modèle nul est indépendant de σ (médianes 0,148 · 0,150 · 0,150
pour σ = 2, 10, 40) — si le nul dépendait du bruit, le filtre aurait un paramètre caché.

## 3. ⭐⭐⭐ Le seuil vient d'un modèle nul fabriqué

Un accord qu'un **bruit blanc** atteint déjà ne dit rien. Le p99 du nul est donc la barre, et il
est calculable **sans regarder le rouleau** : **0,331**.

⭐ C'est la seule façon d'obtenir un seuil que ni un maillage humain ni un réglage n'ont fixé — et
`97` a montré qu'un maillage humain ne peut pas le fixer.

## 4. ⭐⭐ L'instrument, et ce qu'il vaut sur des profils connus

| cas injecté | bon nombre d'interstices | bon côté | accord médian |
|---|---:|---:|---:|
| k = 1, 2 ou 3, σ = 2 | **1,000** | **1,000** | 0,998 |
| idem, σ = 10 | **1,000** | **1,000** | 0,945 |
| idem, σ = 40 (= l'amplitude) | **1,000** | **1,000** | 0,58 |
| bruit pur | — | — | **0,15** |

⚠ « Zéro interstice » n'est **pas** exprimable en gabarit : un segment qui reste sur la même
feuille est brillant de bout en bout, donc plat, donc de norme nulle après centrage. C'est le cas
**sans accord**, déjà couvert par le nul — le confondre avec un gabarit aurait fabriqué une
réponse là où la matière n'en donne pas.

## 5. ⭐⭐⭐ Le résultat

| tiers | matière répond | accord | 1 interstice | 2 ou + | part sur la feuille | continuité |
|---|---:|---:|---:|---:|---:|---:|
| cœur (9 bandes) | 0,740 | 0,457 | **0,557** | 0,443 | 0,487 | ×1,7 |
| milieu (9) | 0,690 | 0,429 | 0,536 | 0,464 | 0,474 | ×5,9 |
| bord (10) | **0,540** | **0,353** | **0,518** | 0,482 | 0,506 | ×31,0 |

Corrélations : **−0,354** avec le rayon, **−0,411** avec la rupture de continuité.

⭐ **La part de transferts que la matière confirme baisse là où la continuité casse.** Le signe est
donc correct — c'est le second signal après `96` à l'avoir, et le premier dont le seuil soit
matériel.

⚠⚠ **Et il est faible.** Au bord, l'accord médian vaut **0,353** pour une barre de **0,3311**, et la
matière ne répond que **54 %** du temps. Là où le transfert casse, elle est presque muette — ce
qui est cohérent avec `94` : au bord, le maillage humain a **enjambé** ce qu'il ne pouvait pas
suivre, donc il n'y a pas toujours de matière à interroger.

## 6. ⭐⭐ Un second verdict que la même lecture donne gratuitement

Le gabarit existe en deux polarités : *brillant–sombre–brillant* si la cellule part **sur** une
feuille, *sombre–brillant–sombre* si elle part **dans** un interstice.

Mesuré : la cellule part sur la feuille **48,7 % au cœur, 47,4 au milieu, 50,6 au bord** — soit
environ **une fois sur deux**.

⚠⚠⚠ **Et ce nombre a deux lectures opposées**, qu'il fallait séparer avant de publier : soit le
maillage est réellement dans un interstice une fois sur deux, soit les deux gabarits sont à
égalité et le choix est un **tirage**. Seule la **marge** entre les deux polarités les distingue.

Mesuré : marge médiane **0,376** au cœur, **0,392** au milieu, **0,356** au bord — comparable à
l'accord lui-même (0,457) — et **81 %** des profils lus ont une marge franche. Sur fixture, la marge vaut ±0,95 au bon signe et **0,06** sur du bruit pur.

> ⭐ **L'instrument tranche donc bien, et ce qu'il tranche est que la moitié des cellules du
> maillage humain partent d'un interstice et non d'une feuille.**

## 7. ⛔⛔ Le compteur de minima, réfuté et gardé

Le premier instrument comptait les **minima proéminents** du profil. Il n'a **aucun point de
fonctionnement** :

| proéminence | faux positifs (bruit pur) | détection (un interstice réel) |
|---:|---:|---:|
| ×3 | 0,988 | 0,265 |
| ×4 | 0,769 | 0,285 |
| ×6 | 0,087 | 0,060 |

Lisser le profil fait monter la détection à **0,95** sans changer les faux positifs (0,6 à 1,0), et
la raison est structurelle :

> ⭐⭐⭐ **Une proéminence exprimée en unités du bruit propre au profil est invariante d'échelle,
> donc lisser abaisse le bruit ET le seuil ensemble.** La discrimination ne peut pas venir de la
> profondeur — elle vient de la **forme**.

⚠ Et son estimateur de bruit était lui-même faux : une différence **première** lit aussi la
**pente** du signal (6,9 niveaux pour une amplitude de 40), donc elle confondait signal et grain.
Corrigé en différence **seconde**, insensible à une pente (0,3 niveau pour la même amplitude).

## 8. ⚠⚠⚠ Trois défauts payés dans cette tranche

**Les gabarits étaient de signe inversé.** `−cos(2π(k+1)t)` commence et finit **sombre**, alors
qu'un segment qui part du centre d'une feuille doit commencer **brillant**. Trouvé en lisant les
comptes : 40 % des profils réels s'appariaient à un gabarit dont la lecture correcte est « la
cellule est dans un interstice », et je publiais ce compte sous le nom « zéro interstice ». **Deux
états différents sous une seule étiquette.**

**Mon test de platitude ne pouvait pas voir le cas dégénéré.** Un profil **exactement constant** a
une étendue nulle *et* un bruit nul, donc `0 < 4×0` est faux : il ressortait « non muet » et son
compte valait zéro, ce qui se lit comme « même feuille » au lieu de « on ne sait pas ». Une mesure
satisfaite par l'absence de ce qu'elle mesure.

**Et deux contrôles à moi mal formulés**, corrigés plutôt que contournés : j'affirmais que le score
ne dépend pas de l'**amplitude** à bruit fixe — c'est faux, à amplitude 3 pour un bruit de 1 le
rapport signal/bruit vaut 3 et le score baisse légitimement ; l'invariance porte sur l'**échelle**.
Et j'exigeais une marge de polarité supérieure à **1,0**, un nombre pris au hasard que la fixture
rendait à 0,952 — remplacé par un rapport au **nul**, comme le reste du fichier.

## 9. ⛔⛔⛔ Ce que `104` a réfuté ici, et ce qui l'a remplacé

Le compteur ci-dessus mesure **deux** choses qu'on lisait comme une seule : *la matière a-t-elle
répondu* et *combien d'interstices le segment franchit*. La première tient. **La seconde est
réfutée par [`104`](104_un_pas_confirme_nest_pas_une_feuille.md)**, et la cause est dans la famille
elle-même : `{1, 2, 3}` ne peut pas exprimer « moins d'une feuille », donc le compte ne vaut jamais
moins de un. Un segment ne franchissant que **0,82** feuille rend « 1 interstice » avec un score de
**0,781** — au-dessus de la barre de **0,3311** — donc il ressort **confirmé**.

⭐⭐ **`feuilles_franchies` le remplace pour la quantité**, sur une famille **continue** : elle rend
la fraction, donc elle peut valoir moins de un, et elle reproduit `cos θ` à **0,0022** près sur
quatre obliquités fabriquées. ⚠ Chaque famille porte la barre de **sa** forme — **0,4018** pour la
continue contre **0,3475** pour celle à trois gabarits, mesuré sur le même bruit pur.

⚠⚠ **Deux gardes, deux pannes, et aucune ne couvre l'autre.** *Sous* la fenêtre le score ne garde
rien (0,20 feuille ressort à 0,350 avec un score de **0,996**) et seule la **butée** le dit ; *loin
au-delà* l'argmax est arbitraire, n'est **pas** en butée, et c'est le **score** qui écarte.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/combien_dinterstices_traverses.py --verifier
uv run python src/nappe/combien_dinterstices_traverses.py \
    --json docs/mesures/combien_dinterstices_traverses.json
uv run python src/figures/figure_combien_dinterstices_traverses.py --verifier
```

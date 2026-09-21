# `212` — Jusqu'où une nappe tient-elle ? Les deux budgets, et celui qui lie

*C'est s'accorder qui lie, pas traverser — et la chaîne optimisait le mauvais budget depuis `204`.*

![Le budget de la nappe](../images/212_le_budget_de_la_nappe.png)

## 0. Pourquoi cette tranche

`151` a monté le pipeline complet à partir de cent cinquante documents, et son maillon ouvert était
la MARCHE : une pince qui avance dans le volume, qui rendait **zéro transfert sur trente-six** sur la
matière calibrée sur le rouleau.

⭐⭐⭐⭐ **Les tranches `198` à `211` ont construit tout autre chose.** Il n'y a plus de pince : il y a
un **champ de pas** sur le treillis des chunks, qu'on intègre en une surface. Cette voie a maintenant
son arithmétique complète — `204` la dispersion du pas, `207` la marche, `208` la décomposition,
`210` la moyenne, `211` le désaccord — et **personne ne l'avait écrite en un seul endroit**.

⚠⚠⚠ **Cette tranche ne tire aucun échantillon.** Elle relit des mesures publiées et en tire des
conséquences arithmétiques, donc elle **ne déclare aucune épreuve** et ne consomme aucune part de la
garantie. Ce qui la rend falsifiable est ailleurs, et c'est le **triangle** (§4).

## 1. ⭐⭐⭐⭐ L'équation de conception

`207` a posé la convention de la chaîne : une marche de $n$ coutures dont le pas a une dispersion
$\sigma$ s'éloigne de son départ d'un écart attendu

$$\mathbb{E}\bigl[\,\lvert \Delta(n) \rvert\,\bigr] \;\simeq\; \sigma\sqrt{n}$$

Elle quitte le feuillet quand cet écart atteint le demi-feuillet $\delta = \Delta/2$. Poser l'égalité
et résoudre en $n$ donne **la longueur tenable** :

$$\boxed{\;n_{\max} \;=\; \left(\frac{\delta}{\sigma}\right)^{2}\;}$$

⭐ **Aucune constante n'entre, et aucun seuil n'est choisi.** Le demi-feuillet de **36 voxels** n'est
pas un réglage : c'est la distance à laquelle la surface saute au feuillet voisin. L'équation est
l'inverse exacte d'une convention déjà publiée, pas une nouveauté théorique — ce qui est neuf est
qu'elle rende **un seul nombre par budget**, directement comparable à la largeur d'une rangée.

⚠⚠ **Une longueur tenable est une ÉCHELLE, pas une promesse.** À $n_{\max}$, l'écart *attendu* vaut
le demi-feuillet, donc environ la moitié des courses de cette longueur en sont déjà sorties. Une
excursion reste une seule réalisation, très variable — `207` l'a payé.

## 2. ⭐⭐⭐⭐ Il y a DEUX budgets, et ils ne se déduisent pas l'un de l'autre

C'est `R4-L16`. `208` sépare le pas d'une rangée en une part que les voisines **partagent** et une
part **propre** à chacune :

$$\sigma_i^{2} \;=\; \sigma_p^{2} \;+\; \sigma_{b,i}^{2}$$

Les deux opérations que le pipeline sait faire ne touchent pas la même moitié :

| opération | ce qu'il reste | ce qu'elle sert |
|---|---|---|
| **moyenner** $k$ rangées | $\sigma_k=\sqrt{\sigma_p^{2}+\dfrac{\sigma_b^{2}}{k}}$ | **traverser** |
| **différencier** deux rangées | $\sigma_\Delta(i,j)=\sqrt{\sigma_{b,i}^{2}+\sigma_{b,j}^{2}}$ | **s'accorder** |

⭐⭐⭐⭐ **La dérive partagée disparaît entièrement d'une différence, et la moyenne ne l'entame
jamais.** Améliorer l'un n'améliore donc pas l'autre, et le pipeline est lié par le **plus petit des
deux**. `151` ne pouvait pas poser cette question : il n'avait qu'une marche.

## 3. Les deux budgets, chiffrés sur le rouleau

| budget | $\sigma$ par couture | $n_{\max}$ |
|---|---:|---:|
| **traverser** — la moyenne de **3 rangées** (`210`) | **1,9245 voxel** | **349,92 coutures** |
| traverser — le plancher de la matière (`204`) | **2,233 voxels** | **259,91 coutures** |
| traverser — une rangée seule (`204`) | **2,4587 voxels** | **214,38 coutures** |
| **s'accorder** — la paire **198**–**197** (`211`) | **2,7138 voxels** | **175,97 coutures** |
| s'accorder — la paire **198**–**199** | **2,9794 voxels** | **146 coutures** |
| **s'accorder** — la paire **197**–**199**, la pire | **3,4004 voxels** | **112,08 coutures** |

✗ **C'est S'ACCORDER qui lie** : **112,08 coutures** contre **349,92** en traversant, soit un rapport
de **0,3203**. Le budget liant coûte **237,84 coutures** de nappe.

⚠⚠⚠ **Conséquence directe pour le pipeline : améliorer la traversée n'achète RIEN.** Toute la chaîne
depuis `204` — seize rangées moyennées, le treillis, la fermeture verticale de `208`, la moyenne de
`210` — a poussé le budget qui **ne lie pas**. C'est le résultat le plus actionnable de cette tranche
et il ne se voyait pas sans mettre les deux échelles côte à côte.

⚠ **La pire paire est celle qui compte**, pas celle de l'épreuve : il suffit d'une couture pour
perdre le feuillet.

## 4. ⭐⭐⭐⭐ Le triangle — et c'est lui qui rend la tranche falsifiable

Le modèle dit qu'une rangée porte un bruit qui lui est propre, et que le désaccord de deux rangées
est la racine de la somme de leurs carrés. **Trois rangées donnent trois équations pour trois
inconnues**, donc le système est exactement déterminé :

$$\sigma_{b,i}^{2} \;=\; \frac{\sigma_\Delta^{2}(i,j)+\sigma_\Delta^{2}(i,k)-\sigma_\Delta^{2}(j,k)}{2}$$

⚠⚠⚠ **Et rien ne garantit que sa solution soit faite de variances POSITIVES.** Il suffirait que le
plus grand des trois désaccords dépasse la racine de la somme des carrés des deux autres pour qu'une
variance sorte négative, et le modèle serait réfuté. C'est une **inégalité sur la matière**, pas une
identité algébrique — exactement la forme que `208` s'était donnée pour se réfuter lui-même.

| rangée | variance propre | bruit propre |
|---|---:|---:|
| **198** | **2,3394 voxels carrés** | **1,5295 voxel** |
| **197** | **5,0253 voxels carrés** | **2,2417 voxels** |
| **199** | **6,5374 voxels carrés** | **2,5568 voxels** |

★ **Les trois sont positives : le modèle TIENT sur les trois rangées mesurées.**

## 5. ⚠⚠ Mais le triangle ne recoupe pas `208`

| rangée | selon `208` | selon le triangle | rapport |
|---|---:|---:|---:|
| **198** | **1,9387 voxel** | **1,5295 voxel** | **0,7889** |
| **197** | **1,899 voxel** | **2,2417 voxels** | **1,1805** |

Le plus grand écart vaut **0,4092 voxel**.

⚠⚠⚠ **Les deux estimateurs ne lisent pas la même chose, et c'est pour cela que l'écart est publié
plutôt que tu.** `208` décompose UNE paire en une dérive partagée et deux bruits propres : il doit
supposer quelque chose pour tirer trois quantités de deux variances et d'une covariance. Le triangle
n'utilise QUE des différences, donc il est **aveugle à la dérive partagée** et n'a rien à supposer.
Les deux devraient s'accorder si le modèle tenait exactement ; l'écart mesuré dit de combien il ne
tient qu'approximativement. Affirmer un accord qu'on n'a pas vérifié serait `R5-L24`.

## 6. Ce qu'une rangée entière demande

Une rangée de **285 colonnes** porte **284 coutures** — ce sont les **intervalles** entre chunks
voisins qui se comptent, pas les chunks.

| | part couverte | verdict |
|---|---:|---|
| en traversant | **1,2321** | ★ une rangée entière **traverse** |
| en s'accordant | **0,3946** | ✗ une rangée entière **ne s'accorde pas** |

Il manque **171,92 coutures** pour qu'une rangée s'accorde d'un bout à l'autre.

⚠ **Et le plancher de la matière n'y suffirait pas non plus** : même un lecteur PARFAIT, qui ne
porterait que la dérive, ne tiendrait que **259,91 coutures** sur **284**. Seule la moyenne de trois
rangées passe la rangée entière en traversée.

## 7. ⭐⭐⭐⭐ La hauteur est gratuite — et voici sous quelle condition

Le résultat est contre-intuitif et il sort du **modèle**, pas d'une mesure. Le désaccord entre la
première et la dernière rangée d'une bande est la différence de leurs deux marches propres :

$$d_{1,r}(n) \;=\; W_1(n)-W_r(n) \qquad\Longrightarrow\qquad \mathrm{Var}\bigl[d_{1,r}(n)\bigr] \;=\; \bigl(\sigma_{b,1}^{2}+\sigma_{b,r}^{2}\bigr)\,n$$

⭐ **Les rangées du milieu n'y entrent pas.** Le désaccord d'une nappe de trois cent quatre-vingt-seize
rangées vaut donc celui d'une paire, et la hauteur ne coûte rien : la nappe tient sur
**112,08 coutures**, qu'elle porte deux rangées ou quatre cents.

⚠⚠⚠ **Et c'est exactement là que le modèle doit être mis à l'épreuve, parce que la conclusion est
trop belle.** Rien n'a mesuré le désaccord de deux rangées **éloignées** : les trois paires de `211`
sont voisines ou à deux rangées d'écart. Si le bruit propre croît avec la distance entre rangées — ce
qu'une matière réelle fait volontiers — la hauteur cesse d'être gratuite, et **le modèle ne le
verrait pas**. Tout ce que le triangle prouve est qu'il tient sur les trois rangées mesurées.

## 8. Les sondes, et les vingt bris

Le module rend **45** contrôles, la figure **47**. Vingt bris ont été posés et **les vingt ont viré
au rouge** après réparation. Quatre y ont d'abord échappé :

⚠⚠ **Une garde entièrement couverte par une autre** : n'exiger que deux paires au lieu de trois
restait vert, parce que le cas à deux paires était déjà refusé par un garde en aval. Le trou réel
était une **quatrième** paire — les paires sont rangées par ensemble non ordonné, donc « 20-10 »
écrase « 10-20 » sans bruit et le triangle se calculerait sur la dernière écrite.

⚠⚠ **Le `.get()` du verdict n'était exercé par rien**, tous les appels passant des dictionnaires qui
portent la clef.

⚠⚠ **Deux sondes MOURAIENT au lieu de rougir** : lever la borne sur la dispersion fait **diviser par
zéro**, donc la batterie mourait avant son verdict et le bris passait pour une panne de sonde.

⚠⚠⚠ **Et une garde de figure ne pouvait pas échouer** : l'échelle verticale du panneau valait
$1{,}55\,\delta$, donc la bande du demi-feuillet retombait **toujours au même pixel** quelle que soit
la constante publiée. Elle suit désormais les courbes tracées. La figure a aussi livré, en la
REGARDANT, six courbes qu'aucune légende ne rattachait à un budget.

## 9. Ce que cette tranche ne dit pas

⚠ Elle porte sur **3 rangées** d'**un** segment, et ses budgets sont ceux de ce segment. ⚠⚠ Elle ne
mesure rien de neuf : elle est une conséquence arithmétique de mesures publiées, et si l'une d'elles
bouge, tous ses nombres bougent. ⚠⚠⚠ Et elle suppose que l'écart attendu d'une marche vaut $\sigma
\sqrt{n}$ — c'est la convention de `207`, donc elle vaut pour des pas **indépendants**, ce que
`R4-F264` a établi pour la dérive et `R4-F335` pour le désaccord, mais jamais au-delà des longueurs
mesurées.

## 10. La porte

`R4-P59` **s'ouvre**, et elle passe AVANT `R4-P58` : le bruit propre d'une rangée croît-il avec la
distance à sa voisine ? Toute la gratuité de la hauteur en dépend, et la mesure est la moins chère de
la chaîne — c'est le pipeline de `211` sur des rangées plus écartées.

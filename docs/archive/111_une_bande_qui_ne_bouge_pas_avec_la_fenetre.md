# 111 — Une bande qui ne bouge pas avec la fenêtre : le plancher devient physique

> ⭐⭐⭐⭐ **Le mode qui « ne compte rien » compte.** Sous l'ancienne bande il tombe d'une falaise —
> **1.008** feuille par pas à deux pas puis **0.12** à six, dérive **-0.888**. Sur **les mêmes
> échantillons**, sous la bande bornée : **1.019** puis **0.951**, dérive **-0.068**. Il
> franchissait une feuille par pas depuis le début, et c'est l'instrument qui la perdait.
>
> ⭐⭐⭐ **Et la bimodalité de `107` s'efface presque entièrement** : l'écart entre les deux modes
> au plus long passe de **+0.965** feuille par pas à **+0.134**.
>
> ⚠⚠⚠ **Le prix est nommé avant d'être mesuré** : une bande étroite ne peut plus dire « pas de
> périodicité » **par son compte**. C'est le **score** qui l'écarte — **0.282** au plus sur une
> dérive seule contre **0.984** au moins sur une périodicité pure — et le mode bas franchit sa
> propre barre sur **76.9 %** à **88.5 %** de ses marches.
>
> ⚠⚠⚠ **Et la dette rétroactive est lourde** : `99` à `110` ont tous été mesurés avec la bande
> non bornée.

![une bande qui ne bouge pas avec la fenêtre](../images/111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png)

## 1. Le défaut : un plancher relatif à la fenêtre

L'estimateur de `98` cherche sa fréquence entre `F_MIN = 0,35` et `k + 4` **périodes par
fenêtre**. Le plancher est donc **relatif** :

| longueur | plus grande longueur d'onde admise |
|---|---:|
| 2 pas (~460 µm) | **1314 µm** |
| 6 pas (~1380 µm) | **3943 µm** |

Aucune de ces deux valeurs n'est un espacement de feuille. `110` a mesuré la conséquence : une
composante de basse fréquence devient **exprimable** dès que la fenêtre est assez longue, et si
elle est plus forte que la périodicité, **elle gagne l'argmax**.

## 2. ⭐⭐⭐ Le remède est une bande, pas un estimateur

Une feuille a un espacement, et la campagne en a déjà fixé la plage : les candidats du balayage de
`105` vont de **86.5** à **346.0** µm. En fréquence, $f = L / \lambda$ — donc la bande suit la
longueur de la fenêtre et **le plancher reste physique**.

| longueur | f min | f max | λ admise |
|---|---:|---:|---|
| 417 µm | **1.2** | **4.82** | 86,5 à 346 µm |
| 1250 µm | **3.61** | **14.45** | 86,5 à 346 µm |

> ⭐ **Aucune ligne de `98` n'est réécrite.** C'est `98` qu'on appelle, avec une bande calculée :
> une seconde implémentation du même ajustement serait deux réponses à « combien de feuilles »,
> libres de diverger.

⚠ Les bornes **ne sont pas un réglage de cette tranche** : ce sont les candidats du balayage. Si
un jour la plage bouge, les deux bougent ensemble.

## 3. ⚠⚠⚠ Le prix de la bande étroite, nommé avant d'être mesuré

Une bande étroite **ne peut plus dire « pas de périodicité » par son compte**. Sur une dérive
seule, sans aucune feuille, elle rend quand même un nombre.

**periodicite pure**

| bande | 2 pas | 3 pas | 4 pas | 5 pas | 6 pas |
|---|---:|---:|---:|---:|---:|
| ancien, compte | **1.0** | **1.002** | **0.999** | **1.001** | **0.999** |
| ancien, score | **0.985** | **0.987** | **0.985** | **0.986** | **0.984** |
| **borné**, compte | **1.0** | **1.001** | **0.998** | **1.001** | **1.0** |
| **borné**, score | **0.985** | **0.987** | **0.985** | **0.986** | **0.984** |

**periodicite plus derive x1,5**

| bande | 2 pas | 3 pas | 4 pas | 5 pas | 6 pas |
|---|---:|---:|---:|---:|---:|
| ancien, compte | **0.963** | **0.15** | **0.13** | **0.126** | **0.125** |
| ancien, score | **0.849** | **0.76** | **0.832** | **0.836** | **0.822** |
| **borné**, compte | **0.962** | **0.973** | **0.986** | **0.996** | **1.001** |
| **borné**, score | **0.849** | **0.66** | **0.558** | **0.548** | **0.57** |

**periodicite plus derive x2,0**

| bande | 2 pas | 3 pas | 4 pas | 5 pas | 6 pas |
|---|---:|---:|---:|---:|---:|
| ancien, compte | **0.95** | **0.147** | **0.13** | **0.126** | **0.125** |
| ancien, score | **0.78** | **0.839** | **0.893** | **0.897** | **0.882** |
| **borné**, compte | **0.95** | **0.968** | **0.982** | **0.993** | **1.001** |
| **borné**, score | **0.78** | **0.566** | **0.46** | **0.446** | **0.473** |

**derive SEULE, aucune feuille**

| bande | 2 pas | 3 pas | 4 pas | 5 pas | 6 pas |
|---|---:|---:|---:|---:|---:|
| ancien, compte | **0.175** | **0.127** | **0.124** | **0.125** | **0.126** |
| ancien, score | **0.919** | **0.976** | **0.984** | **0.985** | **0.984** |
| **borné**, compte | **0.842** | **0.735** | **0.685** | **0.665** | **2.19** |
| **borné**, score | **0.282** | **0.171** | **0.119** | **0.046** | **0.019** |

**bruit pur**

| bande | 2 pas | 3 pas | 4 pas | 5 pas | 6 pas |
|---|---:|---:|---:|---:|---:|
| ancien, compte | **0.98** | **0.472** | **1.519** | **0.793** | **0.104** |
| ancien, score | **0.165** | **0.15** | **0.146** | **0.149** | **0.107** |
| **borné**, compte | **0.98** | **1.051** | **1.518** | **0.793** | **1.631** |
| **borné**, score | **0.165** | **0.115** | **0.146** | **0.149** | **0.08** |


> ⚠⚠⚠ **Sur une dérive seule, la bande bornée rend 0.84 feuille par pas** — un nombre parfaitement
> plausible. Ce qui l'écarte est le **score**, tombé à **0.28** puis **0.02**.

⭐ Et le contrôle est **à double sens** : la bande bornée **garde** le compte sous une dérive
(**True**) là où l'ancienne le **perd** (**True**), et sur une périodicité pure les deux
s'accordent.

## 4. ⚠⚠ La bande bornée a donc besoin de SA barre, et elle change avec la longueur

| longueur | f min | f max | p99 du score sur bruit pur |
|---:|---:|---:|---:|
| 417 µm | **1.204** | **4.817** | **0.2874** |
| 625 µm | **1.806** | **7.226** | **0.2333** |
| 833 µm | **2.409** | **9.634** | **0.2156** |
| 1042 µm | **3.011** | **12.043** | **0.1938** |
| 1250 µm | **3.613** | **14.451** | **0.1725** |

⚠⚠⚠ **Elle BAISSE, et j'avais annoncé l'inverse.** Deux effets s'opposent : la bande **s'élargit**
avec la fenêtre, ce qui devrait rendre l'accord fortuit plus facile ; mais le nombre
d'**échantillons** grandit aussi, et la corrélation d'un gabarit avec du bruit blanc décroît en
$1/\sqrt{n}$.

> ⭐ **C'est le second qui gagne** (pente **-0.1149**). La bande bornée devient **plus**
> discriminante quand la marche s'allonge, pas moins — l'inverse de ce que j'avais écrit dans la
> docstring avant de mesurer.

⚠ Et elle diffère de la barre de la famille de `98` (**0.2874** contre **0.4156**) : *chaque
famille porte la barre de sa propre forme*, et ici **chaque longueur** porte la sienne.

## 5. ⭐⭐⭐ Le résultat : la falaise était celle de l'instrument

Les deux bandes, sur **les mêmes échantillons**, mode par mode :

| mode | bande | 2 pas | 3 | 4 | 5 | 6 | dérive |
|---|---|---:|---:|---:|---:|---:|---:|
| **qui compte** | ancien | **1.012** | **1.128** | **0.82** | **0.889** | **1.085** | **+0.073** |
| | **borné** | **1.031** | 1.128 | **0.861** | **0.943** | 1.085 | **+0.054** |
| **qui ne compte rien** | ancien | **1.008** | **0.241** | **0.186** | **0.152** | **0.12** | **-0.888** |
| | **borné** | **1.019** | **0.996** | **0.933** | **0.937** | **0.951** | **-0.068** |

> ⭐⭐⭐ **La falaise passe de -0.888 à -0.068.** Le mode qui « ne compte rien » franchit **0.951**
> feuille par pas à six pas.

Et la bimodalité de `107` s'efface :

| | écart entre les modes au plus long |
|---|---:|
| ancienne bande | **+0.965** feuille par pas |
| **bande bornée** | **+0.134** |

⭐ Et sur l'ensemble des 48 marches, la dérive du taux passe de
**-0.809** feuille par pas avec l'ancienne bande à
**-0.032** avec la bornée.

## 6. ⭐⭐ Et le compte du mode bas est lu AU-DESSUS de sa barre

C'est la condition sans laquelle « il compte 0,95 » ne voudrait rien dire.

| longueur | score médian du mode bas | barre | part au-dessus |
|---:|---:|---:|---:|
| 2 pas | **0.556** | 0.2874 | **0.769** |
| 3 pas | **0.419** | 0.2333 | **0.885** |
| 4 pas | **0.39** | 0.2156 | **0.769** |
| 5 pas | **0.32** | 0.1938 | **0.769** |
| 6 pas | **0.277** | 0.1725 | **0.769** |

Et le mode haut, pour comparaison :

| longueur | score médian du mode haut | part au-dessus de sa barre |
|---:|---:|---:|
| 2 pas | **0.585** | **1.0** |
| 3 pas | **0.47** | **0.909** |
| 4 pas | **0.427** | **1.0** |
| 5 pas | **0.42** | **0.909** |
| 6 pas | **0.384** | **1.0** |

⚠ **Le mode bas reste plus bas EN SCORE** (0.277 contre **0.384** à six pas) : la périodicité y
est moins nette. Mais plus en **compte** — les deux franchissent une feuille par
pas.

> ⭐ Le bon partage n'est donc pas *une population qui compte et une qui ne compte rien*, mais
> *une matière dont la périodicité est plus ou moins nette, traversée au même rythme partout*.

## 7. ⚠⚠⚠ La dette rétroactive, et elle fait partie du résultat

`99` à `110` ont **tous** été mesurés avec la bande non bornée. Ce que cette tranche déplace :

| tranche | ce qui tombe | ce qui tient |
|---|---|---|
| `107` | ses **deux populations** — l'écart tombe de +0.965 à +0.134 | sa portée (1,0 pas confirmés), son risque par pas, son coût |
| `108` | son **interprétation** : il séparait une partition largement instrumentale | son **fait** : le score du PAS prédit bien ce qu'il prédisait |
| `110` | rien | tout — il avait **nommé** ce mécanisme et montré que l'observation ne le distinguait pas |

⭐⭐ **Et ce que `108` a trouvé change de sens sans devenir faux.** Le score du **pas** est calculé
par le balayage, dont les candidats **sont** la plage physique. C'était donc déjà une mesure
**bornée**, et ce qu'elle prédisait est : *quand l'estimateur NON borné va perdre le signal*.
C'est le mécanisme de `111`, trouvé par l'autre bout.

⚠⚠ **En revanche sa conséquence opérationnelle tombe** : « après trois pas, un automate sait s'il
faut insister » ne sert plus à rien une fois la bande bornée, puisque ce qu'il saurait est quand
l'ancien instrument échoue.

## 8. ⚠ Ce que cette tranche ne dit pas

- **Que le marcheur porte plus loin.** La portée de `107` est **inchangée** : c'est le critère de
  `98` par pas, un autre instrument, et cette tranche ne le touche pas.
- **Que six pas valent cent vingt.** La courbe s'arrête où le plafond de `107` s'arrête.
- **Ce que la quantité mesurée signifie.** `106` reste debout : la périodicité que ce pas suit
  n'est pas l'espacement d'un empilement localement parallèle.
- **Qu'il n'y a aucune feuille nulle part.** Une bande bornée ne peut jamais répondre « aucune
  feuille ici » autrement que par son **score**. C'est un instrument plus juste, pas un instrument
  qui sait tout dire.

## 9. ⭐ Ce que la tranche laisse comme acquis d'outillage

**Les profils bruts sont gardés.** `107` a gardé ses étapes sans son départ ; `110` ses préfixes
sans ses échantillons — d'où les **1158,5 s** de réseau repayées ici pour relire **les mêmes**
voxels. Le profil fait 439 nombres par marche : le garder coûte quelques centaines de kilooctets
et rend toute relecture future **gratuite**.

⚠ Et le partage lecture / agrégation de `107`, que `110` avait payé vingt minutes pour apprendre,
est en place dès le premier jet : `--reagreger` refait le verdict sans rien relire.

## Reproduire

```bash
uv run python src/nappe/une_bande_qui_ne_bouge_pas_avec_la_fenetre.py --verifier
uv run python src/nappe/une_bande_qui_ne_bouge_pas_avec_la_fenetre.py \
    --json docs/mesures/une_bande_qui_ne_bouge_pas_avec_la_fenetre.json
uv run python src/nappe/une_bande_qui_ne_bouge_pas_avec_la_fenetre.py --reagreger \
    --json docs/mesures/une_bande_qui_ne_bouge_pas_avec_la_fenetre.json
uv run python src/figures/figure_une_bande_qui_ne_bouge_pas_avec_la_fenetre.py \
    --sortie docs/images/111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png
```

⚠ La mesure lit le volume distant (**56** lectures, **1158.5** s) ; `--reagreger` ne lit rien.

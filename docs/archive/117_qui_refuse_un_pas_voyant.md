# 117 — Deux tiers des refus viennent de la fenêtre, pas de la matière

> ⭐⭐⭐⭐ **LE TAUX DE 0,7618 NE SE LIT PAS COMME « UN PAS SUR QUATRE ÉCHOUE SUR LA MATIÈRE ».**
> Sur les **91 pas voyants refusés**, **62 n'ont rien contre eux sinon `en_butee`** — l'optimum de
> longueur est tombé sur une extrémité de la fenêtre de candidats. **69 % des refus touchent la
> fenêtre.** C'est l'instrument qui ne sait pas répondre, pas la matière qui dit non.
>
> ⭐⭐⭐⭐ **LA MATIÈRE SEULE N'EN REFUSE QUE 28 SUR 382**, donc le taux vaudrait **au plus
> 0,9122**. ⚠⚠ Borne supérieure et jamais une mesure : un pas en butée aurait pu échouer aussi sur
> la matière avec une fenêtre plus large.
>
> ⭐⭐⭐ **ET LES 63 PAS EN BUTÉE SONT EXACTEMENT AUX DEUX BOUTS**, aucun entre : **43** au bout
> court (86,5 µm) et **20** au bout long (346,0 µm), pour une fenêtre de **0,5 à 2,0 fois** le pas
> nominal de **173,0 µm**.
>
> ⭐⭐⭐ **ET LA PROFONDEUR NE DÉGRADE RIEN.** Chez les voyants, le taux va de **0,74 à 0,80**
> (p **0,3493**) du premier tiers au dernier. Le même test sur tous les pas retrouve **exactement**
> ce que `113` a publié — 0,56 → 0,50, p 0,3253 — ce qui est le contrôle du lecteur.
>
> ⭐ **Zéro lecture distante** : tout se calcule sur les 560 étapes que `113` a gardées.

![Ce qui refuse un pas voyant](../images/117_qui_refuse_un_pas_voyant.png)

## 1. Pourquoi ce fichier

`115` a mesuré que là où le volume répond, le marcheur tient **0,7618** de ses pas, à tout rayon.
Restent 91 pas voyants non confirmés sur 382, et c'est exactement là que l'humain corrige. La
question du graal n'est donc pas *combien* mais **quoi** : le prédicat de `102` est une conjonction
de trois termes, donc chaque refus a une cause nommable.

```
confirme = (interstices == 1) et (accord > barre_interstice) et (non en_butee)
```

## 2. ⚠⚠ La garde sans laquelle la décomposition porte sur autre chose

Le prédicat est **reconstruit** depuis les trois champs et la barre que la course déclare, puis
confronté au `confirme` stocké : **560 pas, 0 désaccord**. Si un seul pas était confirmé alors
qu'un terme est faux, ou refusé alors que les trois tiennent, la conjonction ne serait pas celle
qu'on croit et compter « qui refuse » n'aurait aucun sens.

⚠ Le test porte sur **tous** les pas, aveugles compris : un prédicat qui ne vaudrait que sur les
voyants serait un prédicat différent, et c'est précisément ce qu'on veut exclure. La batterie
refuse de mesurer une course dont le prédicat ne se reconstruit pas.

⚠ **Et ce n'est pas la tautologie que `115` a écartée.** `115` refusait de **corréler** les termes
du prédicat à son résultat ; ici on demande, pour un refus déjà constaté, **lequel** des termes
était faux. C'est une description exhaustive, pas un lien.

## 3. ⭐⭐⭐⭐ Qui refuse

| terme faux | pas |
|---|---:|
| `butee` seule | **62** |
| `accord` seul | 17 |
| `interstices` seul | 8 |
| `interstices` + `accord` | 3 |
| `interstices` + `butee` | 1 |
| **total des refus voyants** | **91** |

⚠ Les combinaisons sont rendues **entières** et pas seulement les marginales : « 63 pas en butée »
et « 20 pas dont l'accord manque » se recouvrent, donc les additionner donnerait plus de refus
qu'il n'y a de pas refusés.

⚠ `interstices + butee` est compté avec la matière et non avec la fenêtre : ce pas-là porte **aussi**
un refus de la matière, donc élargir la fenêtre ne le récupérerait pas.

## 4. ⭐⭐⭐ La butée est une limite d'instrument, et son fichier le dit

`en_butee` vient de `touche_un_bord`, dont la docstring écrit elle-même : *« un optimum au bord
n'est pas une mesure, c'est une butée. La matière y dit "au moins ceci" ou "au plus ceci", et le
publier comme une longueur ferait passer une limite de FENÊTRE pour une limite de matière — le
péché nº 1 de ce dépôt. »*

| | |
|---|---:|
| fenêtre | **0,5 à 2,0** × **173,0 µm** |
| candidats | 31 |
| pas en butée | **63** |
| **au bout court (86,5 µm)** | **43** |
| **au bout long (346,0 µm)** | **20** |
| entre les deux | **0** |

⚠ Les bornes sont **lues dans les pas eux-mêmes** puis comparées au pas nominal que la course
déclare, jamais écrites en constantes : une seconde définition de la fenêtre du marcheur serait
libre de ne plus lui correspondre. Le contrôle « aucun pas en butée n'est au milieu » est dans la
batterie, parce qu'un drapeau qui se lèverait ailleurs qu'aux bouts ne voudrait pas dire ce qu'il
dit.

## 5. ⭐⭐⭐ Ce que la matière seule refuse

| | |
|---|---:|
| pas voyants | 382 |
| confirmés | 291 |
| refusés par la fenêtre seule | **63** |
| **refusés par la matière** | **28** |
| **taux au plus, si la fenêtre ne bornait pas** | **0,9122** |

⚠⚠ **Borne supérieure, et le nom le dit.** Un pas en butée aurait pu échouer aussi sur la matière
si la fenêtre avait été plus large : on ne le saura qu'en refaisant la course. Écrire « le marcheur
confirmerait 91 % » serait promettre ce qu'une re-course seule peut rendre.

⚠⚠ **Et les deux bouts ne veulent pas dire la même chose.** Au bout long, la matière demande un pas
de deux feuilles : le marcheur voulait en sauter une. Au bout court, elle demande moins d'une
demi-feuille, c'est-à-dire un pas qui ne traverse probablement rien. Élargir la fenêtre par le bas
et par le haut ne se justifie donc pas du même argument, et rien ici ne tranche lequel des deux est
un vrai pas que la fenêtre interdit — porte `R4-P24`.

## 6. ⭐⭐⭐ La profondeur ne dégrade rien

| population | premier tiers | dernier tiers | p |
|---|---:|---:|---:|
| tous les pas (ce que `113` a publié) | 0,56 | 0,50 | 0,3253 |
| **voyants seuls** | **0,74** | **0,80** | **0,3493** |

Le test est **importé** de `113` et non réécrit — deux implémentations d'une même probabilité sont
deux occasions de ne pas s'accorder, et le partage en tiers y est déjà déclaré avant de voir les
chiffres.

⭐ La première ligne est le **contrôle positif** : le lecteur retrouve exactement le résultat publié,
donc il lit bien les mêmes pas. Sans lui, « plat chez les voyants » pourrait venir d'un lecteur qui
lit autre chose.

⚠ Les deux taux montent parce qu'on retire des pas qui ne confirment jamais ; le tardif monte le
plus parce que les pas aveugles sont **en queue de marche** (`116`). Le profil de `113` mesurait donc
la profondeur **et** la cécité à la fois — le même défaut que `115` a trouvé sur le rayon, un axe
plus loin.

⚠ p 0,3493 : le taux **ne baisse pas**, et il n'est pas établi qu'il monte. Lire « le marcheur
s'améliore » serait lire un écart non significatif comme un effet.

## 7. Ce que ça change pour le graal

- Là où le volume répond et où l'instrument ne borne pas, la matière refuse **28 pas sur 382**.
  L'humain qu'il faut remplacer n'a donc pas un quart des pas à corriger, il en a **au plus** un
  sur onze — et rien n'indique que ce soit une correction de trajectoire plutôt qu'un refus juste.
- ⭐ La marche ne se dégrade pas en avançant : sur vingt pas, soit environ 4,6 mm, le taux des
  voyants ne baisse pas. Il n'y a donc **pas d'accumulation d'erreur** à corriger sur cette
  distance, ce qui est précisément ce que la correction humaine de spire à spire est censée faire.
- ⚠ Ce qui reste à faire est une **re-course**, pas une relecture : élargir la fenêtre de candidats
  et voir lesquels des 63 pas en butée deviennent des pas mesurés. C'est `R4-P24`, et c'est le seul
  moyen de transformer la borne supérieure en mesure.

## 8. Les registres

Faits : `R4-F42` (deux tiers des refus sont la fenêtre), `R4-F43` (la matière seule en refuse 28,
taux au plus 0,9122), `R4-F44` (la profondeur ne dégrade rien chez les voyants). Porte `R4-P24`
(quel bout de la fenêtre cache un vrai pas). ⚠ Et la note de `R4-F32` est corrigée : son taux plat
avec la profondeur était mesuré sur un échantillon qui contenait les pas aveugles ; la conclusion
survit et se renforce.

## Reproduire

```bash
uv run python src/nappe/qui_refuse_un_pas_voyant.py --verifier           # 35 contrôles
uv run python src/nappe/qui_refuse_un_pas_voyant.py \
    --json docs/mesures/qui_refuse_un_pas_voyant.json                    # une seconde
uv run python src/figures/figure_qui_refuse_un_pas_voyant.py --verifier  # 16 contrôles
uv run python src/figures/figure_qui_refuse_un_pas_voyant.py
```

⚠ **Aucune lecture distante** : tout se calcule sur `docs/mesures/jusquou_va_t_il_si_on_le_laisse.json`.
La définition d'un pas aveugle est **importée** de `ce_qui_porte_le_taux.py` et le test de
profondeur de `jusquou_va_t_il_si_on_le_laisse.py` : rien de ce qui a déjà été écrit n'est réécrit.

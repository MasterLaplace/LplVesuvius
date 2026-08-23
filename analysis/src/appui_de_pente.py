#!/usr/bin/env python3
"""α est une PENTE : elle a deux appuis, et un appui qui ne mesure rien n'en est pas un.

⚠⚠ **Le défaut que ce fichier corrige.** [`49`](../../docs/49_alpha_ne_separe_pas_deux_pannes.md)
a appris à refuser une série dont *aucune* fenêtre ne mesure rien. Mais `test_convergence`
agrège les amplitudes par un **maximum** — « si une seule fenêtre a du relief, la mesure
n'est pas vide » — et cette règle, juste pour la question *« y a-t-il quelque chose ici ? »*,
est fausse pour la question *« quelle est la pente ? »*. Une pente entre une mesure et une
non-mesure n'est pas une pente.

Mesuré le 2026-08-23 : les **trois** candidats `ps256` de
[`48`](../../docs/48_ou_monter_lexperience.md), publiés avec α = +1,01 · +1,17 · +1,01,
ont tous leur fenêtre étroite sous le seuil de détection. Deux d'entre eux ont *les deux*
écarts posés exactement sur la demi-fenêtre.

⭐⭐ **Et le remède n'est pas un refus de plus, c'est un SIGNE.** Un écart posé sur le bord de
la fenêtre n'est pas une absence de donnée : c'est une **borne**. Le pic est *au moins* à
cette distance, peut-être plus loin. Selon l'appui touché, α mesuré est donc un majorant ou
un minorant de α vrai — et cela suffit à dire quels verdicts survivent :

| appui au bord | α mesuré est | condamnation (α ≥ 0,7) | convergence (α < 0,7) |
|---|---|---|---|
| aucun | exact | tient | tient |
| **étroit** | un **majorant** | ⚠ ne tient pas | ⭐ tient |
| **large** | un **minorant** | ⭐ tient | ⚠ ne tient pas |
| les deux | rien | ⚠ ne tient pas | ⚠ ne tient pas |

⚠ Un appui **plat** hors du bord (amplitude sous le seuil, écart pas sur la demi-fenêtre) ne
donne aucun signe : l'écart rapporté est l'argmax d'un bruit, il n'est ni majorant ni
minorant. Il vaut « rien », et le dire est plus honnête que de lui prêter une direction.

Reproduire :

    python3 analysis/src/appui_de_pente.py --racine . --json docs/appui_de_pente.json
    python3 analysis/src/appui_de_pente.py --verifier
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_profils_plats import lire_profil, juger, serie_de          # noqa: E402

# ⚠ Le seuil du verdict vient de `test_convergence`, jamais recopie : deux seuils pour une
# meme grandeur finiraient par se contredire.
try:
    from test_convergence import ALPHA_TRAVERS
except ImportError:                                          # pragma: no cover
    ALPHA_TRAVERS = 0.7

# Les quatre etats d'un appui. « au_bord » l'emporte sur « plat » quand les deux sont vrais :
# le bord porte un SIGNE, le plat n'en porte aucun, et garder le plus informatif des deux
# est ce qui evite de jeter une borne utilisable.
APPUI_MESURE, APPUI_BORD, APPUI_PLAT, APPUI_INCONNU = "mesure", "au_bord", "plat", "inconnu"

BORNE_EXACTE, BORNE_MAJORANT, BORNE_MINORANT, BORNE_AUCUNE = (
    "exacte", "majorant", "minorant", "aucune")


def appui(x: dict) -> str:
    """L'état d'un profil vu comme APPUI d'une pente.

    ⚠ Ce n'est pas le même jugement que `audit_profils_plats.juger`, et c'est voulu : celui-là
    répond « ce profil mesure-t-il quelque chose », celui-ci « peut-on poser une pente
    dessus ». Un profil dont une fenêtre sur deux a du relief mesure bien quelque chose, et
    son écart médian peut malgré tout être le bord du regard.
    """
    if x.get("au_plafond"):
        return APPUI_BORD
    etat = juger(x)["etat"]
    if etat == "inconnu":
        return APPUI_INCONNU
    return APPUI_PLAT if etat == "plat" else APPUI_MESURE


def borne(etroit: str, large: str) -> str:
    """Dans quel sens α mesuré s'écarte-t-il de α vrai ?

    ⚠⚠ La direction se déduit de la formule et non d'une intuition. α = log(e₁/e₀)/log(n₁/n₀)
    avec n₁ > n₀, donc le dénominateur est positif. Un écart posé au bord est **sous-estimé**
    (le pic est au moins là) :

    - appui étroit au bord ⇒ e₀ sous-estimé ⇒ e₁/e₀ **sur**-estimé ⇒ α **majorant** ;
    - appui large au bord ⇒ e₁ sous-estimé ⇒ e₁/e₀ **sous**-estimé ⇒ α **minorant**.
    """
    if etroit in (APPUI_PLAT, APPUI_INCONNU) or large in (APPUI_PLAT, APPUI_INCONNU):
        return BORNE_AUCUNE
    bas, haut = etroit == APPUI_BORD, large == APPUI_BORD
    if bas and haut:
        return BORNE_AUCUNE
    if bas:
        return BORNE_MAJORANT
    if haut:
        return BORNE_MINORANT
    return BORNE_EXACTE


def survit(alpha: float | None, b: str, seuil: float = ALPHA_TRAVERS) -> bool:
    """Le verdict rendu à partir de cet α tient-il malgré la borne ?

    ⚠ « Tient » veut dire : aucune valeur admissible de α vrai ne change le côté du seuil.
    Un majorant place α vrai **en dessous** du mesuré, donc il préserve ce qui est déjà en
    dessous et pas ce qui est au-dessus.
    """
    if alpha is None or b == BORNE_AUCUNE:
        return False
    if b == BORNE_EXACTE:
        return True
    condamne = alpha >= seuil
    return (b == BORNE_MINORANT) if condamne else (b == BORNE_MAJORANT)


def alpha_de(pts: list[tuple[float, float]]) -> float | None:
    """La même formule que `test_convergence`, sur les deux extrêmes de la série."""
    if len(pts) < 2:
        return None
    (n0, e0), (n1, e1) = min(pts), max(pts)
    if n0 <= 0 or e0 <= 0 or n1 <= n0:
        return None
    return math.log(e1 / e0) / math.log(n1 / n0)


def juger_serie(xs: list[dict]) -> dict | None:
    """Une série de profils, jugée par ses deux appuis.

    ⚠ Les appuis sont les **extrêmes en profondeur**, pas le premier et le dernier fichier
    lus : un tri par nom mettrait `profil_161c` avant `profil_41c`.
    """
    xs = [x for x in xs if x.get("couche_tracee") and x.get("ecart_um")]
    if len(xs) < 2:
        return None
    s = sorted(xs, key=lambda y: y["couche_tracee"])
    e, g = s[0], s[-1]
    if e["couche_tracee"] == g["couche_tracee"]:
        return None
    a_e, a_g = appui(e), appui(g)
    b = borne(a_e, a_g)
    a = alpha_de([(y["couche_tracee"] * 2 + 1, y["ecart_um"]) for y in s])
    return {"alpha": a, "appui_etroit": a_e, "appui_large": a_g, "borne": b,
            "verdict": (None if a is None else
                        ("suit la fenêtre" if a >= ALPHA_TRAVERS else "converge")),
            "tient": survit(a, b),
            "couches": [e["couche_tracee"] * 2 + 1, g["couche_tracee"] * 2 + 1],
            "ecarts_um": [e["ecart_um"], g["ecart_um"]],
            "plafonds_um": [e.get("plafond_um"), g.get("plafond_um")]}


def balayer(racine: Path) -> dict[str, list[dict]]:
    """Les profils de l'arbre, groupés par série (le dossier qui les contient)."""
    par: dict[str, list[dict]] = {}
    for p in sorted(racine.rglob("profil*.json")):
        x = lire_profil(p)
        if x:
            # ⚠ La cle vient de `serie_de` et non du dossier parent : deux
            # conventions de rangement coexistent, et grouper par parent
            # decoupait les campagnes du profileur en series d un seul profil.
            par.setdefault(serie_de(p), []).append(x)
    return par


def identites(juges: dict[str, dict]) -> list[dict]:
    """Les α que le couple de fenêtres rend PAR IDENTITÉ, et combien de séries les portent.

    ⚠⚠ **Le contrôle le plus dur du fichier, et il ne coûte rien.** Quand les deux appuis
    sont au bord, α vaut log(demi-fenêtre₁/demi-fenêtre₀) / log(n₁/n₀) — c'est-à-dire une
    propriété du **couple de fenêtres** et de rien d'autre. Deux séries tracées à des
    kilovoxels l'une de l'autre, dans deux prédictions différentes, avec des tirages
    différents, rendent alors **exactement le même nombre**.

    ⭐ Une valeur répétée à la quatrième décimale sur des dizaines de runs indépendants
    n'est pas une mesure robuste : c'est une mesure absente. Ce regroupement le rend
    visible, là où chaque run pris isolément affiche un « α = +1,01 » parfaitement
    plausible.
    """
    grp: dict[tuple[int, int, float], list[str]] = {}
    for k, j in juges.items():
        if j["appui_etroit"] != APPUI_BORD or j["appui_large"] != APPUI_BORD:
            continue
        if j["alpha"] is None:
            continue
        cle = (j["couches"][0], j["couches"][1], round(j["alpha"], 4))
        grp.setdefault(cle, []).append(k)
    out = []
    for (n0, n1, a), ks in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        # ⚠ L'identite est RECALCULEE depuis les demi-fenetres, jamais recopiee depuis α :
        # la recopier ferait un controle qui se compare a lui-meme.
        d0, d1 = (n0 - 1) / 2.0, (n1 - 1) / 2.0
        attendu = (math.log(d1 / d0) / math.log(n1 / n0)) if d0 > 0 and n1 > n0 else None
        out.append({"couches": [n0, n1], "alpha": a, "series": len(ks),
                    "identite_du_couple": attendu,
                    "colle_a_l_identite": (attendu is not None
                                           and abs(a - attendu) < 5e-4),
                    "exemples": sorted(ks)[:3]})
    return out


def resumer(par: dict[str, list[dict]]) -> dict:
    """Le compte par borne, et la liste de ce qui ne tient plus."""
    juges = {}
    for k, xs in sorted(par.items()):
        j = juger_serie(xs)
        if j:
            juges[k] = j
    par_borne: dict[str, int] = {}
    for j in juges.values():
        par_borne[j["borne"]] = par_borne.get(j["borne"], 0) + 1
    tombent = sorted(k for k, j in juges.items() if not j["tient"])
    tiennent_par_borne = sorted(
        k for k, j in juges.items()
        if j["tient"] and j["borne"] in (BORNE_MAJORANT, BORNE_MINORANT))
    convergents = [k for k, j in juges.items() if j["verdict"] == "converge"]
    conv_tombent = sorted(k for k in convergents if not juges[k]["tient"])
    ident = identites(juges)
    return {"series_jugees": len(juges), "par_borne": par_borne,
            "identites_du_couple_de_fenetres": ident,
            "series_sur_une_identite": sum(x["series"] for x in ident
                                           if x["colle_a_l_identite"]),
            "series_qui_tombent": tombent,
            "series_sauvees_par_le_signe": tiennent_par_borne,
            "convergents": len(convergents),
            "convergents_qui_tombent": conv_tombent,
            "seuil_alpha": ALPHA_TRAVERS, "detail": juges}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'etat d'un appui -------------------------------------------------------------
    v("un écart posé sur la demi-fenêtre est AU BORD",
      appui({"au_plafond": True, "amplitude": 0.9, "seuil": 0.02}) == APPUI_BORD)
    v("une amplitude sous le seuil, hors du bord, est PLATE",
      appui({"au_plafond": False, "amplitude": 0.01, "seuil": 0.02}) == APPUI_PLAT)
    v("une amplitude franche, hors du bord, MESURE",
      appui({"au_plafond": False, "amplitude": 0.09, "seuil": 0.02}) == APPUI_MESURE)
    # ⚠ Le bord l'emporte sur le plat : il porte un signe, le plat n'en porte aucun.
    v("plat ET au bord reste AU BORD — le bord est le plus informatif des deux",
      appui({"au_plafond": True, "amplitude": 0.0, "seuil": 0.02}) == APPUI_BORD)
    v("une amplitude absente est INCONNUE, pas plate",
      appui({"au_plafond": False, "amplitude": None, "seuil": 0.02}) == APPUI_INCONNU)

    # --- le signe de la borne ----------------------------------------------------------
    v("deux appuis francs donnent un α exact",
      borne(APPUI_MESURE, APPUI_MESURE) == BORNE_EXACTE)
    v("appui étroit au bord ⇒ α est un MAJORANT",
      borne(APPUI_BORD, APPUI_MESURE) == BORNE_MAJORANT)
    v("appui large au bord ⇒ α est un MINORANT",
      borne(APPUI_MESURE, APPUI_BORD) == BORNE_MINORANT)
    v("les deux au bord ⇒ aucune information",
      borne(APPUI_BORD, APPUI_BORD) == BORNE_AUCUNE)
    v("un appui plat ne donne AUCUN signe, même avec l'autre franc",
      borne(APPUI_PLAT, APPUI_MESURE) == BORNE_AUCUNE)
    v("... y compris du côté large", borne(APPUI_MESURE, APPUI_PLAT) == BORNE_AUCUNE)
    v("un appui inconnu ne donne aucun signe non plus",
      borne(APPUI_INCONNU, APPUI_MESURE) == BORNE_AUCUNE)

    # --- quel verdict survit -----------------------------------------------------------
    v("une convergence sur un majorant TIENT", survit(0.25, BORNE_MAJORANT))
    v("une condamnation sur un majorant NE TIENT PAS", not survit(1.05, BORNE_MAJORANT))
    v("une condamnation sur un minorant TIENT", survit(1.05, BORNE_MINORANT))
    v("une convergence sur un minorant NE TIENT PAS", not survit(0.25, BORNE_MINORANT))
    v("sans borne, rien ne tient", not survit(0.25, BORNE_AUCUNE))
    v("un α absent ne fait tenir aucun verdict", not survit(None, BORNE_EXACTE))
    # ⚠ Le bord exact du seuil : α == ALPHA_TRAVERS est une CONDAMNATION (le verdict
    # « suit la fenetre » se rend a partir de `alpha >= ALPHA_TRAVERS`). Un majorant ne la
    # sauve donc pas. Sans ce controle, un decalage d'un cote du seuil passerait inapercu.
    v("pile au seuil, c'est une condamnation, qu'un majorant ne sauve pas",
      not survit(ALPHA_TRAVERS, BORNE_MAJORANT))
    v("pile au seuil, un minorant la sauve", survit(ALPHA_TRAVERS, BORNE_MINORANT))

    # --- la serie ----------------------------------------------------------------------
    def prof(ct, ecart, plafond, ampl=0.09):
        return {"couche_tracee": ct, "ecart_um": ecart, "plafond_um": plafond,
                "au_plafond": ecart >= plafond * (1 - 1e-9), "amplitude": ampl,
                "seuil": 0.02, "seuil_est_un_repli": False}

    # ⚠ Les profils sont donnes dans le DESORDRE : un tri par nom de fichier mettrait
    # « 161 » avant « 41 », et les deux appuis seraient echanges — donc le signe aussi.
    s = juger_serie([prof(80, 172.8, 192.0), prof(20, 48.0, 48.0)])
    v("les appuis sont les extrêmes en PROFONDEUR, pas l'ordre de lecture",
      s["couches"] == [41, 161], str(s["couches"]))
    v("... et l'étroit posé au bord rend un majorant", s["borne"] == BORNE_MAJORANT)
    v("une série d'un seul profil ne se juge pas", juger_serie([prof(20, 48.0, 48.0)]) is None)
    # ⚠ Deux profils a la MEME profondeur ne font pas une pente : le denominateur
    # log(n1/n0) vaudrait zero. Refuse plutot que division par zero.
    v("deux profils à la même profondeur ne font pas une pente",
      juger_serie([prof(20, 48.0, 48.0), prof(20, 40.0, 48.0)]) is None)

    # --- le cas reel qui a impose ce fichier -------------------------------------------
    # `ps256_c0` : 41c ecart 48,00 sur une demi-fenetre de 48,00 ; 161c ecart 192,00 sur
    # une demi-fenetre de 192,00. Les DEUX appuis sont le bord, donc α = +1,01 est le
    # rapport des fenetres et ne porte rien.
    c0 = juger_serie([prof(20, 48.0, 48.0, 0.0175), prof(80, 192.0, 192.0, 0.0462)])
    v("le cas ps256_c0 rend un α ≈ 1", abs(c0["alpha"] - 1.0) < 0.05, f"{c0['alpha']:.4f}")
    v("... et il ne porte AUCUNE information", c0["borne"] == BORNE_AUCUNE)
    v("... donc sa condamnation ne tient pas", not c0["tient"])
    # Une spire qui converge, appui etroit au bord : le verdict TIENT.
    sp = juger_serie([prof(15, 129.6, 129.6), prof(40, 172.8, 345.6)])
    v("une spire convergente sur appui étroit au bord tient",
      sp["verdict"] == "converge" and sp["tient"],
      f"{sp['verdict']} borne={sp['borne']}")

    # --- le resume ---------------------------------------------------------------------
    r = resumer({"a": [prof(20, 48.0, 48.0, 0.0175), prof(80, 192.0, 192.0, 0.0462)],
                 "b": [prof(15, 129.6, 129.6), prof(40, 172.8, 345.6)],
                 "c": [prof(15, 100.0, 129.6), prof(40, 110.0, 345.6)]})
    v("le résumé compte les trois séries", r["series_jugees"] == 3)
    v("... en nommant celle qui tombe", r["series_qui_tombent"] == ["a"],
      str(r["series_qui_tombent"]))
    v("... et celle que le SIGNE sauve", r["series_sauvees_par_le_signe"] == ["b"],
      str(r["series_sauvees_par_le_signe"]))
    v("aucune série convergente ne tombe ici", r["convergents_qui_tombent"] == [])

    # --- l'identite du couple de fenetres ----------------------------------------------
    juges = {
        "a": {"alpha": 1.0135, "appui_etroit": APPUI_BORD, "appui_large": APPUI_BORD,
              "couches": [41, 161]},
        "b": {"alpha": 1.0135, "appui_etroit": APPUI_BORD, "appui_large": APPUI_BORD,
              "couches": [41, 161]},
        "c": {"alpha": 0.30, "appui_etroit": APPUI_BORD, "appui_large": APPUI_MESURE,
              "couches": [31, 81]}}
    ident = identites(juges)
    v("les séries aux deux appuis au bord sont regroupées", len(ident) == 1, str(ident))
    v("... et elles sont bien deux", ident[0]["series"] == 2)
    # ⚠⚠ Le controle qui compte : le nombre observe DOIT etre l'identite du couple, et
    # l'identite est recalculee depuis les demi-fenetres. Sans ce recalcul, on verifierait
    # seulement que deux runs s'accordent -- ce qui est vrai de toute mesure reproductible.
    v("... et leur α est l'identité du couple de fenêtres",
      ident[0]["colle_a_l_identite"],
      f"{ident[0]['alpha']} contre {ident[0]['identite_du_couple']}")
    v("une série dont un seul appui est au bord n'entre pas dans le compte",
      all("c" not in x["exemples"] for x in ident))
    # ⚠ Un α qui ne colle PAS a l'identite doit etre signale comme tel et non exclu : deux
    # appuis au bord avec un autre nombre voudrait dire que les demi-fenetres ne sont pas
    # celles qu'on croit, ce qui est une information et non un cas a jeter.
    autre = identites({"z": {"alpha": 0.5, "appui_etroit": APPUI_BORD,
                             "appui_large": APPUI_BORD, "couches": [41, 161]}})
    v("un α au bord qui ne colle pas à l'identité est listé, non exclu",
      len(autre) == 1 and not autre[0]["colle_a_l_identite"])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--racine", type=Path, default=Path("."))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    par = balayer(a.racine)
    if not par:
        print(f"aucun profil sous {a.racine}", file=sys.stderr)
        return 1
    r = resumer(par)

    print(f"\n  {r['series_jugees']} série(s) jugeables, seuil α = {r['seuil_alpha']}")
    for b, libelle in ((BORNE_EXACTE, "les deux appuis mesurent — α exact"),
                       (BORNE_MAJORANT, "appui étroit au bord — α est un MAJORANT"),
                       (BORNE_MINORANT, "appui large au bord — α est un MINORANT"),
                       (BORNE_AUCUNE, "⚠⚠ aucun signe — α ne porte rien")):
        print(f"    {r['par_borne'].get(b, 0):4d}  {libelle}")

    print(f"\n  ⭐ {len(r['series_sauvees_par_le_signe'])} série(s) reposent sur un appui au "
          f"bord et leur verdict TIENT QUAND MÊME — le signe de la borne le dit")
    print(f"  ⚠⚠ {len(r['series_qui_tombent'])} série(s) rendent un verdict que leurs appuis "
          f"ne portent pas")
    for k in r["series_qui_tombent"][:12]:
        j = r["detail"][k]
        print(f"      {k:44s} α {j['alpha']:+.4f}  « {j['verdict']} »  "
              f"appuis {j['appui_etroit']}/{j['appui_large']}")
    if len(r["series_qui_tombent"]) > 12:
        print(f"      … et {len(r['series_qui_tombent']) - 12} autre(s)")

    if r["identites_du_couple_de_fenetres"]:
        print(f"\n  ⚠⚠ {r['series_sur_une_identite']} série(s) rendent un α qui est "
              f"l'IDENTITÉ de leur couple de fenêtres — le même nombre, à la quatrième")
        print("      décimale, quels que soient la graine, la prédiction et le tirage :")
        for x in r["identites_du_couple_de_fenetres"]:
            marque = "  = log(d₁/d₀)/log(n₁/n₀)" if x["colle_a_l_identite"] else ""
            print(f"      {x['series']:3d} série(s)  {x['couches'][0]}c→{x['couches'][1]}c  "
                  f"α = {x['alpha']:+.4f}{marque}")

    # ⭐⭐ LA MOITIE RASSURANTE, MESUREE ET NON SUPPOSEE — et cette fois avec sa RAISON.
    # Un appui etroit au bord rend α majorant, donc il preserve exactement ce qui est SOUS
    # le seuil : une convergence. C'est pourquoi les verdicts positifs survivent, et ce
    # n'est plus une constatation mais une consequence du signe.
    print(f"\n  ⭐⭐ {r['convergents']} série(s) convergent, dont "
          f"{len(r['convergents_qui_tombent'])} tombent — un appui étroit au bord rend α "
          f"MAJORANT,")
    print("      donc il préserve précisément ce qui est sous le seuil. Les verdicts")
    print("      positifs ne survivent pas par chance : le signe de la borne les protège.")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

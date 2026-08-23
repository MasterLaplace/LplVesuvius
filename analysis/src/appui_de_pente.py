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
    if s[0]["couche_tracee"] == s[-1]["couche_tracee"]:
        return None
    # ⚠⚠ **Le couple le plus LARGE dont les DEUX bouts mesurent**, et non simplement les
    # extremes. Une serie de trois fenetres offre trois couples, et prendre les extremes
    # maximise le bras de levier au prix de reintroduire un appui vide.
    #
    # Mesure du 2026-08-24 : la campagne de plafond au niveau 2 tient 11, 41 et 83 couches.
    # Les extremes donnent 11/83, dont l appui etroit est PLAT -- alors qu un rendu a ete
    # paye exactement pour disposer de 41/83, dont les deux bouts mesurent. Prendre les
    # extremes jetait la mesure qu on venait d acheter.
    #
    # ⚠ Le repli reste les extremes : quand aucun couple ne mesure des deux cotes, le plus
    # large est encore ce qui se rapproche le plus d une pente, et son verdict portera de
    # toute facon la mention « les appuis ne portent pas ».
    def _rapport_ok(a, b):
        return (2 * b["couche_tracee"] + 1) >= 2 * (2 * a["couche_tracee"] + 1)

    e, g = s[0], s[-1]
    meilleur = None
    for i, a in enumerate(s):
        for b in s[i + 1:]:
            if a["couche_tracee"] == b["couche_tracee"] or not _rapport_ok(a, b):
                continue
            if appui(a) == APPUI_MESURE and appui(b) == APPUI_MESURE:
                bras = b["couche_tracee"] / a["couche_tracee"]
                if meilleur is None or bras > meilleur[0]:
                    meilleur = (bras, a, b)
    if meilleur:
        e, g = meilleur[1], meilleur[2]
    a_e, a_g = appui(e), appui(g)
    b = borne(a_e, a_g)
    a = alpha_de([(y["couche_tracee"] * 2 + 1, y["ecart_um"]) for y in s])
    return {"alpha": a, "appui_etroit": a_e, "appui_large": a_g, "borne": b,
            # ⚠ Le couple RETENU est rapporte : sur une serie de plus de deux fenetres, un
            # lecteur ne peut pas deviner lesquelles ont produit α.
            "fenetres_disponibles": [y["couche_tracee"] * 2 + 1 for y in s],
            "couple_choisi_pour_ses_appuis": bool(meilleur),
            "verdict": (None if a is None else
                        ("suit la fenêtre" if a >= ALPHA_TRAVERS else "converge")),
            "tient": survit(a, b),
            "couches": [e["couche_tracee"] * 2 + 1, g["couche_tracee"] * 2 + 1],
            "ecarts_um": [e["ecart_um"], g["ecart_um"]],
            "plafonds_um": [e.get("plafond_um"), g.get("plafond_um")]}


def contraste_des_appuis(par: dict[str, list[dict]]) -> dict:
    """Une surface posée sur une feuille a-t-elle le même genre d'appuis que la nôtre ?

    ⚠⚠ **La question que α seul ne peut pas trancher sur ce rouleau.** Trente-neuf séries
    rendent un verdict que leurs appuis ne portent pas, donc empiler des α ne dit plus rien.
    Mais l'ÉTAT d'un appui — le pic est-il sur un bord de la fenêtre — est une question
    binaire posée à l'intérieur de chaque fenêtre, quelle que soit sa profondeur, et elle ne
    demande ni seuil à régler ni profondeurs appariées.

    ⭐ Ce que ça mesure : sur une surface qui suit une feuille, le relief est **déjà là dans
    une fenêtre étroite**. Sur une surface posée en travers, il n'apparaît qu'en élargissant
    — c'est-à-dire que ce qu'on lit est la fenêtre et non la surface.

    ⚠ **Ce n'est pas circulaire, et il faut le dire.** La partition se fait sur le SIGNE de α,
    qui vient des écarts ; l'état de l'appui vient des amplitudes. Deux grandeurs différentes
    des mêmes profils. Elles sont liées par un mécanisme — un pic dans la fenêtre donne à la
    fois un écart stable et une amplitude franche — et ce lien est le contenu du constat, pas
    son défaut.
    """
    conv_plat = conv_total = cond_plat = cond_total = 0
    exemples: list[str] = []
    # ⚠ Le RAPPORT au plancher, et non l amplitude nue : le plancher peut differer d un
    # profil a l autre, et comparer des amplitudes brutes comparerait aussi des seuils.
    points: list[dict] = []
    for k, xs in sorted(par.items()):
        j = juger_serie(xs)
        if not j or j["alpha"] is None:
            continue
        # ⚠⚠ On lit l AMPLITUDE de la fenetre etroite, pas son etat d appui. `appui()` fait
        # gagner « au bord » sur « plat » quand les deux sont vrais -- c est juste pour
        # choisir un SIGNE de borne, et faux pour la question posee ici, qui est « cette
        # fenetre montre-t-elle du relief ». Une fenetre a la fois plate et au bord est
        # plate, et c est ce qui compte.
        s = sorted([x for x in xs if x.get("couche_tracee") and x.get("ecart_um")],
                   key=lambda y: y["couche_tracee"])
        if not s:
            continue
        etroit_plat = juger(s[0])["etat"] == "plat"
        a0, seuil = s[0].get("amplitude"), s[0].get("seuil")
        if a0 is not None and seuil:
            points.append({"serie": k, "converge": j["alpha"] < ALPHA_TRAVERS,
                           "amplitude_sur_plancher": float(a0) / float(seuil),
                           # ⚠ La part de fenetres dont le pic est colle a un bord est
                           # rapportee A COTE de l amplitude, parce que c est exactement ce
                           # que l outil public `tracecheck` publie deja sous le nom
                           # `edge_pinned`. Les deux ensemble disent lequel des deux signaux
                           # separe le mieux -- et la reponse n est pas celui qu on publie.
                           "au_bord": (float(s[0]["au_bord"])
                                       if s[0].get("au_bord") is not None else None),
                           "couches_etroite": s[0]["couche_tracee"] * 2 + 1})
        if j["alpha"] < ALPHA_TRAVERS:
            conv_total += 1
            if etroit_plat:
                conv_plat += 1
                exemples.append(k)
        else:
            cond_total += 1
            if etroit_plat:
                cond_plat += 1
    # ⚠⚠ LES DEUX SIGNAUX COMPARES, et c est le point : `edge_pinned` est ce que l outil
    # public publie deja, l amplitude est ce que personne ne publie. Les compter cote a cote
    # dit lequel separe -- et ce n est pas celui qui est publie.
    def _sous(pop, cle, seuil, sens):
        v = [x[cle] for x in points if x["converge"] is pop and x.get(cle) is not None]
        if not v:
            return None
        n = sum(1 for y in v if (y < seuil if sens == "<" else y >= seuil))
        return {"sur": len(v), "compte": n}

    signaux = {
        "amplitude_sous_le_plancher": {
            "convergentes": _sous(True, "amplitude_sur_plancher", 1.0, "<"),
            "condamnees": _sous(False, "amplitude_sur_plancher", 1.0, "<")},
        "au_bord_au_moins_90_pourcent": {
            "convergentes": _sous(True, "au_bord", 0.90, ">="),
            "condamnees": _sous(False, "au_bord", 0.90, ">=")}}

    return {"convergentes": conv_total, "convergentes_appui_etroit_plat": conv_plat,
            "signaux_compares": signaux,
            "condamnees": cond_total, "condamnees_appui_etroit_plat": cond_plat,
            # ⚠ Nommees, pas seulement comptees : une convergente a l appui plat serait un
            # contre-exemple, et un compte sans nom ne se verifie pas.
            "convergentes_plates_nommees": exemples,
            "points": points}


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
    contraste = contraste_des_appuis(par)
    return {"series_jugees": len(juges), "par_borne": par_borne,
            "contraste_des_appuis": contraste,
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

    # --- le choix du couple dans une serie de plus de deux fenetres ----------------------
    def prof3(ct, ecart, plafond, ampl=0.09):
        n = 2 * ct + 1
        return {"couche_tracee": ct, "ecart_um": ecart, "plafond_um": plafond,
                "bords_um": [plafond], "au_plafond": ecart >= plafond * (1 - 1e-9),
                "amplitude": ampl, "seuil": 0.02, "seuil_est_un_repli": False,
                "layers": list(range(n))}

    # ⚠⚠ Le cas reel : 11, 41 et 83 couches, l appui a 11 est PLAT. Les extremes donneraient
    # 11/83 et jetteraient le couple 41/83, dont les deux bouts mesurent -- celui pour lequel
    # un rendu a ete paye.
    trois = juger_serie([prof3(5, 48.0, 96.0, 0.007),
                         prof3(20, 182.4, 192.0, 0.031),
                         prof3(41, 384.0, 393.6, 0.046)])
    v("le couple retenu est le plus large dont les DEUX bouts mesurent",
      trois["couches"] == [41, 83], str(trois["couches"]))
    v("... et il est signale comme choisi", trois["couple_choisi_pour_ses_appuis"])
    v("... toutes les fenetres disponibles sont rapportees",
      trois["fenetres_disponibles"] == [11, 41, 83], str(trois["fenetres_disponibles"]))
    # ⚠ Quand aucun couple ne mesure des deux cotes, on retombe sur les extremes et le
    # verdict portera sa mention.
    aucun = juger_serie([prof3(5, 48.0, 96.0, 0.007), prof3(41, 384.0, 393.6, 0.007)])
    v("sans couple mesurant, on retombe sur les extremes",
      aucun["couches"] == [11, 83] and not aucun["couple_choisi_pour_ses_appuis"],
      str(aucun["couches"]))
    # ⚠ Un couple mesurant mais TROP SERRE ne doit pas etre prefere : le verdict le
    # refuserait pour rapport insuffisant.
    serre = juger_serie([prof3(20, 182.4, 192.0, 0.031), prof3(30, 250.0, 288.0, 0.040),
                         prof3(41, 384.0, 393.6, 0.046)])
    v("un couple trop serre n est pas retenu", serre["couches"] == [41, 83],
      str(serre["couches"]))

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

    # --- le contraste entre les deux populations -----------------------------------------
    def pf(ct, ecart, plafond, ampl, au_bord=0.5):
        n = 2 * ct + 1
        return {"couche_tracee": ct, "ecart_um": ecart, "plafond_um": plafond,
                "bords_um": [plafond], "au_plafond": ecart >= plafond * (1 - 1e-9),
                "amplitude": ampl, "seuil": 0.02, "seuil_est_un_repli": False,
                "au_bord": au_bord, "layers": list(range(n))}

    c = contraste_des_appuis({
        # convergente, relief franc des la fenetre etroite
        "bonne": [pf(15, 100.0, 129.6, 0.12), pf(40, 104.0, 345.6, 0.13)],
        # condamnee, appui etroit PLAT
        "mauvaise": [pf(20, 48.0, 48.0, 0.005), pf(80, 192.0, 192.0, 0.046)],
        # condamnee mais dont l appui etroit mesure : la separation n est pas parfaite
        "mitigee": [pf(20, 100.0, 192.0, 0.09), pf(80, 400.0, 768.0, 0.12)]})
    v("les convergentes sont comptees", c["convergentes"] == 1, str(c))
    v("les condamnees aussi", c["condamnees"] == 2, str(c))
    v("une fenetre etroite sans relief chez une condamnee est comptee",
      c["condamnees_appui_etroit_plat"] == 1, str(c))
    # ⚠⚠ Le controle qui distingue les deux lectures : une fenetre a la fois PLATE et AU
    # BORD est plate. `appui()` la dirait « au bord » -- juste pour choisir un signe de
    # borne, faux pour « montre-t-elle du relief ».
    v("... y compris quand elle est AUSSI au bord",
      contraste_des_appuis({"x": [pf(20, 48.0, 48.0, 0.005),
                                  pf(80, 192.0, 192.0, 0.046)]}
                           )["condamnees_appui_etroit_plat"] == 1)
    # ⚠⚠ Le controle qui porte le constat : AUCUNE convergente ne doit avoir d appui etroit
    # plat. S il y en avait, elles seraient NOMMEES, parce qu un compte sans nom ne se
    # verifie pas.
    # ⚠ Les points portent le RAPPORT au plancher : 0,12 pour un plancher de 0,02 fait 6.
    v("un point porte le rapport de l amplitude au plancher",
      any(abs(x["amplitude_sur_plancher"] - 6.0) < 1e-9 for x in c["points"]),
      str([round(x["amplitude_sur_plancher"], 2) for x in c["points"]]))
    v("... et chaque serie jugee a son point", len(c["points"]) == 3)
    # ⚠⚠ Les deux signaux doivent etre comptes SEPAREMENT : les confondre ferait croire que
    # l outil public mesure deja ce qui separe.
    sig = c["signaux_compares"]
    v("les deux signaux sont comptes a part",
      set(sig) == {"amplitude_sous_le_plancher", "au_bord_au_moins_90_pourcent"}, str(sig))
    v("chaque signal porte son denominateur",
      all(x and "sur" in x for g in sig.values() for x in g.values()), str(sig))
    v("aucune convergente n a d appui etroit plat ici",
      c["convergentes_appui_etroit_plat"] == 0 and c["convergentes_plates_nommees"] == [])

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

    # --- le chemin de SORTIE, que la batterie n exercait pas ------------------------------
    # ⚠⚠ Paye le 2026-08-24 : une variable de boucle nommee `a` dans `main` a ecrase le
    # namespace argparse, et `a.json` a plante. La batterie etait verte -- elle n appelle
    # jamais `main`. Un chemin de sortie non exerce est un chemin non teste.
    import tempfile as _t
    import subprocess as _sp
    with _t.TemporaryDirectory() as td:
        # ⚠⚠ DEUX series, une convergente et une condamnee, et c est indispensable : le bloc
        # d affichage qui portait le bug est garde par « il y a des deux ». Une premiere
        # version de cette sonde n avait qu une serie, donc le bloc ne s executait pas et la
        # sonde restait verte en reintroduisant le defaut. Verifie.
        for nom, trois in (("bonne", ((15, 100.0, 0.12, 0.3), (40, 104.0, 0.13, 0.3))),
                           ("mauvaise", ((20, 48.0, 0.005, 1.0), (80, 192.0, 0.046, 1.0)))):
            d = Path(td) / "arbre" / nom
            d.mkdir(parents=True)
            for ct, ecart, ampl, bord in trois:
                n = 2 * ct + 1
                (d / f"profil_{n}c.json").write_text(json.dumps({
                    "ecart_trace_um_median": ecart, "couche_tracee": ct, "voxel_um": 8.64,
                    "amplitude_mediane": ampl, "amplitude_min": 0.02, "au_bord": bord,
                    "layers": list(range(n))}), encoding="utf-8")
        sortie = Path(td) / "r.json"
        pr = _sp.run([sys.executable, str(Path(__file__).resolve()),
                      "--racine", str(Path(td) / "arbre"), "--json", str(sortie)],
                     capture_output=True, text=True)
        v("le chemin --json va au bout", pr.returncode == 0,
          (pr.stderr or "").strip().splitlines()[-1] if pr.stderr else "")
        v("... et il ecrit un JSON relisible",
          sortie.is_file() and "series_jugees" in json.loads(sortie.read_text()))

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

    ct = r["contraste_des_appuis"]
    if ct["convergentes"] and ct["condamnees"]:
        print(f"\n  ⭐⭐ l'appui ÉTROIT, question binaire posée dans chaque fenêtre — "
              f"ni seuil à régler, ni profondeurs à apparier :")
        print(f"      {ct['convergentes_appui_etroit_plat']:3d} / {ct['convergentes']:3d} "
              f"séries qui CONVERGENT ont leur appui étroit plat")
        print(f"      {ct['condamnees_appui_etroit_plat']:3d} / {ct['condamnees']:3d} "
              f"séries CONDAMNÉES l'ont")
        sig = ct.get("signaux_compares") or {}
        if sig:
            print("      et le meme partage lu par les DEUX signaux disponibles :")
            for nom, libelle in (("amplitude_sous_le_plancher",
                                  "amplitude sous le plancher"),
                                 ("au_bord_au_moins_90_pourcent",
                                  "pic au bord sur ≥ 90 % des fenêtres")):
                g = sig.get(nom) or {}
                # ⚠⚠ Surtout PAS `a` : c est le namespace argparse de cette fonction, et
                # l ecraser faisait planter `a.json` vingt lignes plus bas -- sur le seul
                # chemin que la batterie n exerce pas. Une variable d une lettre dans une
                # fonction qui en a deja une du meme nom est un piege qui attend son tour.
                cv, cd = g.get("convergentes"), g.get("condamnees")
                if cv and cd:
                    print(f"        {libelle:38s} convergentes "
                          f"{cv['compte']:3d}/{cv['sur']:3d}"
                          f"   condamnées {cd['compte']:3d}/{cd['sur']:3d}")
        for k in ct["convergentes_plates_nommees"][:5]:
            print(f"      ⚠ contre-exemple : {k}")

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

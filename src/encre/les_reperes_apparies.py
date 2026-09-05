#!/usr/bin/env python3
"""Les repères intérieurs s'apparient-ils à l'autre aplatissement ? — et le témoin qui décide.

⚠⚠ POURQUOI CE FICHIER EXISTE. `75` C1 a établi que le masque des étiquettes porte **348**
trous intérieurs, dont **314** assez ronds pour contraindre les deux composantes — et que
l'autre aplatissement ne publie **aucun masque de surface**, seulement le **support de la carte
d'encre**, c'est-à-dire là où le détecteur a rendu quelque chose.

⭐⭐⭐ **Reste la question qui décide, et elle se mesure** : les trous du masque se retrouvent-ils
dans ce support ? Là où il n'y a **pas de matière**, un détecteur ne peut rien rendre — donc si
le support porte les mêmes trous, il est un masque de fait, et les repères ont un vis-à-vis.
S'il ne les porte pas, ses trous sont une propriété du **détecteur** et il faut demander un
masque publié.

⚠⚠ **Le témoin est obligatoire et il est de MÊME COMPTE.** Sur une empreinte trouée, n'importe
quel semis de points tombe parfois près d'un trou : la distance d'appariement ne veut rien dire
sans la distance qu'un semis **au hasard** obtient sur la même empreinte, avec le même nombre
de points. C'est le même contrôle que la carte d'encre mélangée de `75`.

⚠ Les centres sont transportés par l'affine **déjà validée** (`le_recalage_des_etiquettes`,
Dice 0,975, AUC 0,756 contre 0,500 au mélange) et non par un recalage refait ici : ce fichier
teste si des repères existent, pas si l'affine est bonne.

Usage :
    uv run python src/encre/les_reperes_apparies.py --verifier
    uv run python src/encre/les_reperes_apparies.py \\
        --json docs/mesures/les_reperes_apparies.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from les_reperes_interieurs import _image, trous, utilisables  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
RECALAGE = RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json"


def transformer(centre: list[float], t: dict) -> tuple[float, float]:
    """Un point du masque dans le repère de la carte publiée, par l'affine diagonale.

    ⚠ Diagonale parce que les deux aplatissements sont des rectangles quasi alignés du même
    objet : `deux_aplatissements` mesure 3,2 % d'écart d'aspect, ce qu'une échelle par axe
    décrit exactement.
    """
    return (centre[0] * t["echelle_lignes"] + t["decalage_lignes"],
            centre[1] * t["echelle_colonnes"] + t["decalage_colonnes"])


def apparier(sources: np.ndarray, cibles: np.ndarray) -> np.ndarray:
    """La distance de chaque source à la cible la plus proche.

    ⚠ Rendue **par source** et non agrégée : une médiane cache qu'un repère sur deux peut être
    parfait et l'autre absurde, ce qui n'est pas la même situation qu'un appariement moyen.
    """
    if sources.size == 0 or cibles.size == 0:
        return np.zeros(0)
    d = np.hypot(sources[:, None, 0] - cibles[None, :, 0],
                 sources[:, None, 1] - cibles[None, :, 1])
    return d.min(axis=1)


def semis_temoin(empreinte: np.ndarray, combien: int, graine: int = 42) -> np.ndarray:
    """Autant de points, tirés au hasard DANS l'empreinte.

    ⚠⚠ Dans l'empreinte et non dans le rectangle : un semis qui tomberait hors du fragment
    serait loin de tout trou par construction, et le témoin serait artificiellement mauvais —
    donc l'appariement vrai paraîtrait bon sans rien prouver.
    """
    ii, jj = np.nonzero(empreinte > 0)
    if ii.size == 0:
        return np.zeros((0, 2))
    rng = np.random.default_rng(graine)
    k = rng.choice(ii.size, size=min(combien, ii.size), replace=False)
    return np.stack([ii[k].astype(float), jj[k].astype(float)], axis=1)


def mesurer(carte: np.ndarray, masque: np.ndarray, transformation: dict,
            aire_min_cible: int = 4, graine: int = 42) -> dict:
    """Les repères du masque contre les trous du support publié, avec leur témoin."""
    support = (carte > 0).astype(np.uint8) * 255
    cibles_t = utilisables(trous(support, aire_minimale=aire_min_cible))
    cibles = np.array([t["centre"] for t in cibles_t], dtype=float)

    sources_t = utilisables(trous(masque))
    # ⚠ Seuls les repères dont l'AIRE survit à l'échelle de la carte ont une chance d'y être :
    # un trou de 64 px du masque fait moins d'un pixel une fois transporté.
    facteur = transformation["echelle_lignes"] * transformation["echelle_colonnes"]
    gardes = [t for t in sources_t if t["aire"] * facteur >= aire_min_cible]
    sources = np.array([transformer(t["centre"], transformation) for t in gardes], dtype=float)

    d = apparier(sources, cibles)
    t_pts = semis_temoin(support, len(gardes), graine)
    dt = apparier(t_pts, cibles)
    # ⚠⚠ Les PAIRES sont rendues, pas seulement leur distance : l'écart source→cible EST le
    # champ résiduel que C1 cherche, et une médiane ne se dessine pas. Rendre l'agrégat seul
    # obligerait une figure à refaire l'appariement, donc à pouvoir en faire un autre.
    paires = []
    if sources.size and cibles.size:
        for k in range(len(sources)):
            dk = np.hypot(sources[k, 0] - cibles[:, 0], sources[k, 1] - cibles[:, 1])
            c = int(dk.argmin())
            paires.append({"source": [round(float(sources[k, 0]), 2),
                                      round(float(sources[k, 1]), 2)],
                           "cible": [round(float(cibles[c, 0]), 2),
                                     round(float(cibles[c, 1]), 2)],
                           "distance": round(float(dk[c]), 2),
                           "aire": gardes[k]["aire"]})
    return {"paires": paires,
            "trous_du_masque": len(sources_t),
            "reperes_transportables": len(gardes),
            "trous_du_support": len(cibles_t),
            "distance_mediane": round(float(np.median(d)), 2) if d.size else None,
            "distance_p10": round(float(np.percentile(d, 10)), 2) if d.size else None,
            "distance_temoin_mediane": round(float(np.median(dt)), 2) if dt.size else None,
            "bat_le_temoin": bool(d.size and dt.size and np.median(d) < np.median(dt)),
            "forme_carte": list(carte.shape)}


def charger_transformation(chemin: Path = RECALAGE) -> dict | None:
    """L'affine déjà validée, LUE plutôt que refaite."""
    if not chemin.is_file():
        return None
    return json.loads(chemin.read_text()).get("transformation")


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    t = {"echelle_lignes": 0.5, "echelle_colonnes": 0.25,
         "decalage_lignes": 10.0, "decalage_colonnes": -5.0}
    v("l'affine diagonale transporte un point", transformer([100.0, 200.0], t) == (60.0, 45.0))

    a = np.array([[0.0, 0.0], [10.0, 10.0]])
    b = np.array([[0.0, 3.0], [10.0, 10.0]])
    d = apparier(a, b)
    v("l'appariement rend une distance PAR source", d.shape == (2,), str(d))
    v("... et c'est la plus proche", abs(d[0] - 3.0) < 1e-9 and d[1] == 0.0)
    v("des cibles vides ne rendent aucune distance", apparier(a, np.zeros((0, 2))).size == 0)

    # ⚠⚠ Le témoin tire DANS l'empreinte : hors d'elle il serait loin de tout par construction,
    # donc l'appariement vrai paraîtrait bon sans rien prouver.
    emp = np.zeros((100, 100), dtype=np.uint8)
    emp[40:60, 40:60] = 255
    pts = semis_temoin(emp, 50)
    v("le témoin tire dans l'empreinte, jamais dehors",
      pts.size and bool(((pts[:, 0] >= 40) & (pts[:, 0] < 60)).all()), str(pts[:2]))
    v("... et autant de points qu'on lui en demande", len(semis_temoin(emp, 17)) == 17)
    v("... bornés par ce que l'empreinte contient", len(semis_temoin(emp, 10 ** 6)) == 400)

    # --- une correspondance fabriquée, et son absence ---
    def masque_avec(trous_ij, cote=400, rayon=12):
        m = np.zeros((cote, cote), dtype=np.uint8)
        m[20:cote - 20, 20:cote - 20] = 255
        yy, xx = np.mgrid[0:cote, 0:cote]
        for i, j in trous_ij:
            m[(yy - i) ** 2 + (xx - j) ** 2 <= rayon ** 2] = 0
        return m

    ident = {"echelle_lignes": 1.0, "echelle_colonnes": 1.0,
             "decalage_lignes": 0.0, "decalage_colonnes": 0.0}
    positions = [(100, 100), (100, 300), (300, 100), (300, 300), (200, 200)]
    m1 = masque_avec(positions)
    r = mesurer(m1.astype(float), m1, ident, aire_min_cible=16)
    # ⭐⭐ LE CAS OÙ LA CORRESPONDANCE EXISTE : les mêmes trous des deux côtés doivent
    # s'apparier à zéro et battre franchement le témoin.
    v("des trous identiques s'apparient à zéro et battent le témoin",
      r["distance_mediane"] is not None and r["distance_mediane"] < 1.0 and r["bat_le_temoin"],
      str(r))
    # ⚠⚠ ET LE CAS OÙ ELLE N'EXISTE PAS. Ma première version mettait les trous dans les coins
    # et ils battaient quand même le témoin : sur une empreinte dont les cibles sont sur une
    # grille, un coin reste systématiquement plus proche qu'un point tiré n'importe où. Le
    # négatif juste est un DÉPLACEMENT d'une demi-maille — la panne réelle qu'on veut exclure,
    # un recalage faux d'un demi-pas — et non « des trous quelque part d'autre ».
    m2 = masque_avec([(i + 100, j) for i, j in positions])
    r2 = mesurer(m2.astype(float), m1, ident, aire_min_cible=16)
    v("... alors qu'un décalage d'une demi-maille ne le bat pas",
      not r2["bat_le_temoin"],
      f"{r2['distance_mediane']} contre {r2['distance_temoin_mediane']}")
    # ⚠ Un support SANS trou ne rend aucune distance : c'est un refus, pas un appariement nul.
    plein = np.full((400, 400), 255, dtype=np.uint8)
    r3 = mesurer(plein.astype(float), m1, ident, aire_min_cible=16)
    v("un support sans trou ne rend aucune distance",
      r3["trous_du_support"] == 0 and r3["distance_mediane"] is None, str(r3))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--recette", default="new_canon")
    p.add_argument("--graine", type=int, default=42)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    sys.path[:0] = [str(q) for q in (RACINE / "src").iterdir() if q.is_dir()]
    from le_recalage_des_etiquettes import carte_publiee_reduite  # noqa: PLC0415

    t = charger_transformation()
    if t is None:
        raise SystemExit(f"affine absente : {RECALAGE}")
    masque = _image("500P2_mask.png")
    if masque is None:
        raise SystemExit("masque absent")
    duo = carte_publiee_reduite(a.recette)
    if duo is None:
        raise SystemExit("carte publiée injoignable")
    carte, nom = duo
    r = {"carte": nom, "recette": a.recette, **mesurer(carte, masque, t, graine=a.graine)}
    print(f"carte {nom}\n  {r['forme_carte'][0]}×{r['forme_carte'][1]}")
    print(f"  trous du masque, utilisables            {r['trous_du_masque']:>6}")
    print(f"  dont transportables à cette échelle     {r['reperes_transportables']:>6}")
    print(f"  trous du SUPPORT de la carte publiée    {r['trous_du_support']:>6}")
    print(f"  distance d'appariement, médiane         {r['distance_mediane']}")
    print(f"  ... au 1er décile                       {r['distance_p10']}")
    print(f"  témoin, même compte au hasard           {r['distance_temoin_mediane']}")
    print(f"\n  les repères s'apparient mieux que le hasard : "
          f"{'OUI' if r['bat_le_temoin'] else 'NON'}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

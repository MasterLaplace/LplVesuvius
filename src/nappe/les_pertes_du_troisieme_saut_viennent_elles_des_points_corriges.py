"""Les justes que la chaîne repartie perd au troisième saut de la bande sont-ils les points que la correction a déplacés ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE RANGEMENT. Ce qui était vu avant d'écrire : tout ce que `248` et `257` à `285` publient.
Repartie du deuxième saut corrigé de la bande, recalé sur son rayon, la chaîne rend au troisième saut 7 ratés justes pour 15
justes ratés (`285`), et 96 points notés y diffèrent du témoin. La correction n'a déplacé que 69 points au deuxième saut.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Deux chemins mènent d'un point déplacé au deuxième saut à un saut suivant qui
change. Le point lui-même part d'ailleurs. Ou ses voisins changent : la chaîne recalcule les normales par différences entre
mailles voisines, et son vote vise la médiane d'un carré de trois mailles, tour après tour. Le remède n'est pas le même : dans le
premier cas, c'est la correction qu'il faut revoir ; dans le second, c'est la façon dont la chaîne repart d'une surface
corrigée.

## Le rangement, déclaré avant la mesure

Les deux reprises sont celles de `285`, refaites à l'identique. Au troisième saut, chaque point noté où elles diffèrent est
rangé par sa distance, en mailles (la plus grande des deux différences d'indices), au plus proche point que la correction a
déplacé au deuxième saut : 0 (le point lui-même), 1, 2 ou 3, 4 et plus.

⚠ Le contrôle rend la mesure décidable : le rangement refait les comptes de `285` au troisième saut, ratés rendus justes et justes
rendus ratés.

## Les issues, exclusives

- plus de la moitié des justes que la reprise rend ratés au troisième saut sont des points que la correction a déplacés : la
  perte vient des points corrigés eux-mêmes ;
- non : elle vient de points que la correction n'a pas touchés.

⚠ Rapporté à côté : les ratés rendus justes rangés de même ; au quatrième saut, le même rangement ; pour les points déplacés,
leur état au deuxième saut recalé contre leur état au troisième.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une autre façon de repartir ; une correction du troisième saut.

Usage :
    uv run python src/nappe/les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges.py --verifier
    uv run python src/nappe/les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges.py \\
        --json docs/mesures/les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

from la_procedure_sans_juge_tient_elle_sur_la_bande import la_bande  # noqa: E402
from recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste import les_deux_reprises  # noqa: E402
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import les_justes  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_285_A_PUBLIE = LES_MESURES / "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json"
LES_CLASSES = (("le_point_lui_meme", 0, 0), ("a_une_maille", 1, 1), ("a_deux_ou_trois_mailles", 2, 3),
               ("a_quatre_mailles_ou_plus", 4, np.inf))


def la_distance_en_mailles(gi: np.ndarray, gj: np.ndarray, quels: np.ndarray) -> np.ndarray:
    """Pour chaque point, la plus grande des deux différences d'indices au plus proche point choisi ; inf sans point choisi."""
    d = np.full(len(gi), np.inf)
    for y, x in zip(gi[quels], gj[quels]):
        d = np.minimum(d, np.maximum(np.abs(gi - y), np.abs(gj - x)))
    return d


def le_rangement(tau_t: np.ndarray, tau_r: np.ndarray, verite: np.ndarray, distance: np.ndarray) -> dict:
    """Les points notés où la reprise diffère du témoin, rangés par leur distance au plus proche point déplacé."""
    note = np.isfinite(verite)
    bt, br = les_justes(tau_t, verite), les_justes(tau_r, verite)
    with np.errstate(invalid="ignore"):
        differe = note & ~(np.abs(tau_r - tau_t) < 1e-9)
    rj, jr = note & ~bt & br, note & bt & ~br
    out = {"les_points_notes": int(note.sum()), "ou_les_deux_chaines_different": int(differe.sum()),
           "les_rates_rendus_justes": int(rj.sum()), "les_justes_rendus_rates": int(jr.sum()), "les_classes": {}}
    for nom, a, b in LES_CLASSES:
        c = (distance >= a) & (distance <= b)
        out["les_classes"][nom] = {"ou_les_deux_chaines_different": int((differe & c).sum()),
                                   "les_rates_rendus_justes": int((rj & c).sum()),
                                   "les_justes_rendus_rates": int((jr & c).sum())}
    return out


def letat_des_points_deplaces(tau2: np.ndarray, v2: np.ndarray, tau3: np.ndarray, v3: np.ndarray,
                              deplace: np.ndarray) -> dict:
    """Pour les points déplacés notés aux deux sauts : juste ou raté au deuxième saut recalé, puis au troisième."""
    m = deplace & np.isfinite(v2) & np.isfinite(v3)
    j2, j3 = les_justes(tau2, v2), les_justes(tau3, v3)
    return {"les_points": int(m.sum()),
            "justes_puis_justes": int((m & j2 & j3).sum()), "justes_puis_rates": int((m & j2 & ~j3).sum()),
            "rates_puis_justes": int((m & ~j2 & j3).sum()), "rates_puis_rates": int((m & ~j2 & ~j3).sum())}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : le rangement ne refait pas les comptes de 285 au troisième saut"}
    t = r["le_troisieme_saut"]
    if 2 * t["les_classes"]["le_point_lui_meme"]["les_justes_rendus_rates"] > t["les_justes_rendus_rates"]:
        return {"lissue": "la perte du troisième saut vient des points corrigés eux-mêmes"}
    return {"lissue": "la perte du troisième saut vient de points que la correction n'a pas touchés"}


def mesurer() -> dict:
    debut = time.monotonic()
    b = la_bande()
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b, "le_verdict": le_verdict({})}
    r = les_deux_reprises(b)
    v, deplace = b["verite"], r["deplace"]
    distance = la_distance_en_mailles(b["gi"], b["gj"], deplace)
    publie = json.loads(CE_QUE_285_A_PUBLIE.read_text())["les_sauts"]
    out = {"les_points_deplaces": int(deplace.sum()),
           "le_troisieme_saut": le_rangement(r["tt"][0], r["tr"][0], v[2], distance),
           "le_quatrieme_saut": le_rangement(r["tt"][1], r["tr"][1], v[3], distance),
           "les_points_deplaces_du_deuxieme_au_troisieme": letat_des_points_deplaces(r["tau2r"], v[1], r["tr"][0], v[2],
                                                                                    deplace),
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    comptes = lambda x: (x["les_rates_rendus_justes"], x["les_justes_rendus_rates"])  # noqa: E731
    out["les_comptes_de_285"] = {"au_troisieme": comptes(publie[0]), "au_quatrieme": comptes(publie[1])}
    out["decidable"] = (comptes(out["le_troisieme_saut"]) == tuple(out["les_comptes_de_285"]["au_troisieme"])
                        and comptes(out["le_quatrieme_saut"]) == tuple(out["les_comptes_de_285"]["au_quatrieme"])
                        and not out["la_lecture"]["combien_de_pannes"])
    out["le_verdict"] = le_verdict(out)
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    gi = np.array([0, 0, 1, 3, 5, 0])
    gj = np.array([0, 1, 1, 0, 9, 5])
    d = la_distance_en_mailles(gi, gj, np.array([True, False, False, False, False, False]))
    v("★★★★ la distance en mailles est la plus grande des deux différences d'indices au plus proche point déplacé",
      d.tolist() == [0, 1, 1, 3, 9, 5], str(d))
    v("★★ sans point déplacé, la distance est infinie", np.isinf(la_distance_en_mailles(gi, gj, np.zeros(6, bool))).all())

    vt = np.array([216.0, 216.0, 216.0, 216.0, np.nan, 216.0])
    tt = np.array([216.0, 150.0, 216.0, 216.0, 216.0, 216.0])
    tr = np.array([150.0, 216.0, 216.0, 150.0, 150.0, 216.0])
    r = le_rangement(tt, tr, vt, d)
    c = r["les_classes"]
    v("★★★★ un juste que la reprise rate est rangé à la distance de son point, et un point non noté ne compte pas",
      r["les_justes_rendus_rates"] == 2 and c["le_point_lui_meme"]["les_justes_rendus_rates"] == 1
      and c["a_deux_ou_trois_mailles"]["les_justes_rendus_rates"] == 1, str(r))
    v("★★★ un raté que la reprise rend juste est rangé de même",
      r["les_rates_rendus_justes"] == 1 and c["a_une_maille"]["les_rates_rendus_justes"] == 1)
    v("★★★ les classes couvrent toutes les distances une fois",
      sum(x["ou_les_deux_chaines_different"] for x in c.values()) == r["ou_les_deux_chaines_different"] == 3)

    e = letat_des_points_deplaces(np.array([72.0, 150.0]), np.array([72.0, 72.0]), np.array([216.0, 144.0]),
                                  np.array([144.0, 144.0]), np.array([True, True]))
    v("★★★ l'état d'un point déplacé se lit au deuxième saut recalé, puis au troisième",
      e == {"les_points": 2, "justes_puis_justes": 0, "justes_puis_rates": 1, "rates_puis_justes": 1, "rates_puis_rates": 0},
      str(e))

    t_ = lambda moi, tous: {"decidable": True, "le_troisieme_saut": {  # noqa: E731
        "les_justes_rendus_rates": tous, "les_classes": {"le_point_lui_meme": {"les_justes_rendus_rates": moi}}}}
    v("★★★★ les issues : des points corrigés si plus de la moitié en sont, sinon d'ailleurs, indécidable sans contrôle",
      "eux-mêmes" in le_verdict(t_(8, 15))["lissue"] and "pas touchés" in le_verdict(t_(7, 14))["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    texte = json.dumps(r, ensure_ascii=False, indent=1)
    print(texte)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())

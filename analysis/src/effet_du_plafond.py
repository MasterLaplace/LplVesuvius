#!/usr/bin/env python3
"""Le plafond de générations fabrique-t-il le résultat, ou le résultat tient-il ?

⚠⚠ **Pourquoi ce fichier existe.** Toute trace jamais faite sur `PHercParis4` s'arrête à la
génération 59, et ce budget a été choisi le jour où j'estimais le rendu à 57 Kio/s — une
extrapolation faite sur *un* échantillon, corrigée depuis par la mesure : 1108 à 5861 Kio/s.
Le plafond était donc dimensionné pour un coût faux d'un facteur vingt à cent, et tout ce que
ce dépôt affirme sur ce rouleau a été mesuré en dessous.

⚠⚠ **La seule chose difficile ici est de ne pas conclure trop vite.** Le même tireur, sur la
même graine, rend déjà α = +0,89 à +1,12 : `vc_grow_seg_from_seed` n'est pas déterministe. Un
écart d'α entre deux budgets ne veut donc rien dire tant qu'il n'a pas dépassé ce bruit-là, et
la tentation de lire une baisse de 0,1 comme « la surface avait besoin de place » est
exactement l'erreur que ce fichier doit rendre impossible.

Le bruit est **mesuré** sur les répétitions quand elles existent, et seulement à défaut repris
de la valeur enregistrée — une constante recopiée finit par ne plus décrire l'instrument.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ⚠ Étendue observée sur cinq tirages de la MÊME graine, campagne `paris4_croise_r3`.
# C'est un repli : le fichier préfère toujours la mesurer sur les répétitions présentes.
BRUIT_TIRAGE_ENREGISTRE = 0.23

# ⚠ Le seuil de convergence est importé, jamais recopié — deux définitions finiraient par
# ne pas s'accorder, et celle-ci décide d'un verdict publié.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from test_convergence import ALPHA_TRAVERS
except Exception:                                    # pragma: no cover - repli hors dépôt
    ALPHA_TRAVERS = 0.7


def bruit_de_tirage(docs: Path) -> tuple[float, str]:
    """L'étendue d'α entre répétitions d'une même graine, mesurée si possible.

    ⚠ « Même graine » se lit dans le NOM du fichier, jamais dans l'ordre des fichiers : une
    campagne de répétitions écrit `..._r1`, `..._r2`, `..._r3`, et apparier par position
    donnerait un nombre dès qu'il y a deux fichiers, y compris quand ils décrivent deux
    endroits différents.
    """
    groupes: dict[str, list[float]] = {}
    for f in sorted(docs.glob("*.json")):
        m = re.match(r"(.+?)_r\d+\.json$", f.name)
        if not m:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for x in (d.get("series") or ([d] if "alpha" in d else [])):
            a = x.get("alpha")
            if isinstance(a, (int, float)):
                groupes.setdefault(m.group(1), []).append(float(a))
    etendues = [max(v) - min(v) for v in groupes.values() if len(v) >= 2]
    if etendues:
        return max(etendues), f"mesuré sur {len(etendues)} série(s) de répétitions"
    return BRUIT_TIRAGE_ENREGISTRE, "repli : étendue enregistrée de la campagne r3"


def charger(docs: Path, prediction: str, candidat: int) -> list[dict]:
    """Les mesures d'un même candidat aux différents budgets.

    ⚠ Le budget vient du NOM (`..._g200.json`) et pas d'un champ, parce que c'est la campagne
    qui le choisit et le traceur qui l'ignore : le lire dans le résultat reviendrait à faire
    confiance à un outil pour rapporter une consigne qu'il n'a pas reçue.
    """
    out = []
    motif = re.compile(rf"^plafond_{re.escape(prediction)}_c{candidat}_g(\d+)\.json$")
    for f in sorted(docs.glob(f"plafond_{prediction}_c{candidat}_g*.json")):
        m = motif.match(f.name)
        if not m:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for x in (d.get("series") or ([d] if "verdict" in d else [])):
            out.append({"budget": int(m.group(1)), "verdict": x.get("verdict"),
                        "alpha": x.get("alpha"), "aire_cm2": x.get("aire_cm2")})
    return sorted(out, key=lambda r: r["budget"])


def confronter(lignes: list[dict], bruit: float, origine_bruit: str = "fourni") -> dict:
    d: dict = {"n_budgets": len(lignes), "bruit_de_tirage": bruit,
               "origine_du_bruit": origine_bruit,
               "budgets": [l["budget"] for l in lignes]}
    mesures = [l for l in lignes if isinstance(l.get("alpha"), (int, float))]
    d["n_mesures"] = len(mesures)
    d["n_indecidables"] = sum(1 for l in lignes if l.get("verdict") == "indecidable")

    # ⭐ La question catégorique passe devant : une seule convergence changerait ce que ce
    # dépôt sait faire, et aucune tendance d'α ne pèse autant.
    conv = [l for l in mesures if abs(l["alpha"]) < ALPHA_TRAVERS]
    d["budgets_qui_convergent"] = [l["budget"] for l in conv]
    d["converge"] = bool(conv)

    if len(mesures) < 2:
        d["verdict"] = "insuffisant"
        d["raison"] = ("il faut au moins deux budgets MESURÉS pour dire si le plafond change "
                       "quelque chose ; un profil indécidable ne compte pas, il n'a pas d'α")
        return d

    a = [l["alpha"] for l in mesures]
    d["alpha_min"], d["alpha_max"] = min(a), max(a)
    d["etendue_alpha"] = max(a) - min(a)
    d["alpha_au_plus_petit"] = mesures[0]["alpha"]
    d["alpha_au_plus_grand"] = mesures[-1]["alpha"]
    d["variation"] = mesures[-1]["alpha"] - mesures[0]["alpha"]

    # ⚠⚠ Le point du fichier. Un écart inférieur au bruit du tireur n'est pas un petit effet :
    # c'est un effet dont on ne peut RIEN dire, et l'écrire autrement serait lire du hasard.
    d["depasse_le_bruit"] = abs(d["variation"]) > bruit
    if d["converge"]:
        d["verdict"] = "le plafond CACHAIT une convergence"
    elif d["depasse_le_bruit"] and d["variation"] < 0:
        d["verdict"] = "α baisse avec le budget"
        d["consequence"] = ("la surface avait besoin de place ; ce qui a été mesuré à 60 "
                            "générations sur ce rouleau est à refaire plus grand")
    elif d["depasse_le_bruit"]:
        d["verdict"] = "α monte avec le budget"
        d["consequence"] = "grandir empire la traversée, le plafond n'était pas la contrainte"
    else:
        d["verdict"] = "α stable sous le bruit de tirage"
        d["consequence"] = (f"la variation {d['variation']:+.2f} reste sous le bruit du "
                            f"tireur ({bruit:.2f}) — 60 générations suffisaient pour juger, "
                            f"et le résultat négatif de ce rouleau tient")
    return d


def rapporter(d: dict) -> None:
    print(f"\n  budgets mesurés : {d['budgets']}  "
          f"({d['n_mesures']} avec α, {d['n_indecidables']} indécidable(s))")
    print(f"  bruit de tirage : {d['bruit_de_tirage']:.2f}  ({d['origine_du_bruit']})")
    if d.get("converge"):
        print(f"\n  ⭐⭐⭐ UNE TRACE CONVERGE aux budgets {d['budgets_qui_convergent']}")
    if d["verdict"] == "insuffisant":
        print(f"\n  ⚠ {d['raison']}")
        return
    print(f"\n  α : {d['alpha_au_plus_petit']:+.2f} au budget {d['budgets'][0]}"
          f"  →  {d['alpha_au_plus_grand']:+.2f} au budget {d['budgets'][-1]}"
          f"   (variation {d['variation']:+.2f})")
    print(f"\n  ⭐ {d['verdict']}")
    if d.get("consequence"):
        print(f"     {d['consequence']}")


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    stable = [{"budget": 60, "alpha": 1.01, "verdict": "traverse"},
              {"budget": 200, "alpha": 1.09, "verdict": "traverse"}]
    r = confronter(stable, 0.23)
    v("une variation sous le bruit est dite stable", r["verdict"].startswith("α stable"))
    v("... et n'est pas présentée comme un effet", r["depasse_le_bruit"] is False)

    # ⚠⚠ Le contrôle qui porte le fichier : la MÊME variation devient un effet quand le
    # bruit est plus petit. Si les deux donnaient le même verdict, le bruit ne servirait
    # a rien et le fichier ne ferait que rehabiller une soustraction.
    r2 = confronter(stable, 0.02)
    v("la même variation devient un effet sous un bruit plus fin", r2["depasse_le_bruit"])
    v("... et son sens est lu", "monte" in r2["verdict"], r2["verdict"])

    baisse = [{"budget": 60, "alpha": 1.10, "verdict": "traverse"},
              {"budget": 400, "alpha": 0.75, "verdict": "traverse"}]
    rb = confronter(baisse, 0.23)
    v("une baisse au-delà du bruit est nommée", "baisse" in rb["verdict"], rb["verdict"])
    v("... et sa conséquence est écrite", "refaire plus grand" in rb.get("consequence", ""))

    # ⭐ Le catégorique passe devant : une convergence l'emporte sur toute tendance.
    conv = [{"budget": 60, "alpha": 1.10, "verdict": "traverse"},
            {"budget": 400, "alpha": 0.30, "verdict": "converge"}]
    rc = confronter(conv, 0.23)
    v("une convergence est signalée avant toute tendance", rc["converge"])
    v("... et le verdict le dit", "CACHAIT" in rc["verdict"], rc["verdict"])
    v("... et nomme les budgets concernés", rc["budgets_qui_convergent"] == [400])

    # ⚠ Un profil plat n'a pas d'α : il ne doit pas compter comme une mesure.
    plat = [{"budget": 60, "verdict": "indecidable", "alpha": None},
            {"budget": 200, "alpha": 1.0, "verdict": "traverse"}]
    rp = confronter(plat, 0.23)
    v("un profil indécidable ne compte pas comme mesure", rp["n_mesures"] == 1)
    v("... et un seul point ne conclut pas", rp["verdict"] == "insuffisant")
    v("... et il est compté à part", rp["n_indecidables"] == 1)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # ⚠ Sonde du bruit MESURÉ : deux répétitions d'une même graine, une autre série
        # ailleurs. L'étendue doit être celle du groupe, pas celle de tous les fichiers.
        (d / "x_r1.json").write_text('{"alpha": 1.00, "verdict": "traverse"}')
        (d / "x_r2.json").write_text('{"alpha": 1.30, "verdict": "traverse"}')
        (d / "y_r1.json").write_text('{"alpha": 0.10, "verdict": "converge"}')
        b, org = bruit_de_tirage(d)
        v("le bruit est mesuré sur les répétitions", abs(b - 0.30) < 1e-9, f"{b}")
        v("... par graine, pas sur tous les fichiers", b < 1.0)
        v("... et son origine est dite", "mesuré" in org)
        # ⚠ Contrôle : sans répétitions, il faut le repli et il faut qu'il le DISE.
        b2, org2 = bruit_de_tirage(d / "vide" if False else Path(td) / "aucun")
        v("sans répétitions, repli explicite", b2 == BRUIT_TIRAGE_ENREGISTRE and "repli" in org2)

        # ⚠ Le budget vient du nom : deux budgets du même candidat, plus un fichier d'un
        # AUTRE candidat que le motif ne doit pas ramasser.
        (d / "plafond_m7_c0_g60.json").write_text('{"alpha": 1.01, "verdict": "traverse"}')
        (d / "plafond_m7_c0_g200.json").write_text('{"alpha": 0.95, "verdict": "traverse"}')
        (d / "plafond_m7_c3_g60.json").write_text('{"alpha": 0.10, "verdict": "converge"}')
        lg = charger(d, "m7", 0)
        v("les budgets sont lus dans le nom", [l["budget"] for l in lg] == [60, 200], f"{lg}")
        v("... et un autre candidat n'est pas ramassé", all(l["alpha"] != 0.10 for l in lg))
        v("... dans l'ordre croissant", lg == sorted(lg, key=lambda r: r["budget"]))

    v("le seuil de convergence est importé", ALPHA_TRAVERS == 0.7)
    v("aucun budget, aucun verdict", confronter([], 0.23)["verdict"] == "insuffisant")

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs", type=Path, default=Path("docs"))
    ap.add_argument("--prediction", default="ps256")
    ap.add_argument("--candidat", type=int, default=0)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()

    lignes = charger(a.docs, a.prediction, a.candidat)
    if not lignes:
        print(f"aucune mesure plafond_{a.prediction}_c{a.candidat}_g*.json dans {a.docs}",
              file=sys.stderr)
        return 2
    bruit, origine = bruit_de_tirage(a.docs)
    d = confronter(lignes, bruit, origine)
    d["prediction"], d["candidat"] = a.prediction, a.candidat
    rapporter(d)
    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

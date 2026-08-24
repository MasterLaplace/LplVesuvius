#!/usr/bin/env python3
"""Ce que vaut le relief SUR UN CORPUS, lu par l'instrument qui l'a lu.

⚠⚠ **Ce fichier existe parce qu'un seuil a été transporté deux fois le même jour, et deux
fois à tort.** Le relief dépend de la profondeur de la fenêtre (exposant mesuré **+1,01**)
ET de son étendue dans le plan (exposant **−0,83**). Un nombre lu dans une géométrie ne veut
donc rien dire dans une autre, et une table de calibration qui ne déclare pas sa géométrie
ne calibre rien.

⭐ Le remède est celui que le README public conseille désormais à ses lecteurs : ne comparer
un candidat qu'à la distribution mesurée **là où on le lit**. Ce fichier produit cette
distribution à partir d'un balayage `tracecheck --all --csv`.

⚠ La géométrie est **lue dans le fichier** quand il la porte, et **déclarée à la main**
sinon — les balayages antérieurs au 2026-08-24 ne l'écrivaient pas. La sortie dit laquelle
des deux, parce qu'un nombre fourni de mémoire vaut moins qu'un nombre relu.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
import sys
from pathlib import Path


def lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("segment")]


def nombres(lignes: list[dict], colonne: str) -> list[float]:
    out = []
    for r in lignes:
        v = r.get(colonne)
        if v in (None, ""):
            continue
        try:
            out.append(float(v))
        except ValueError:
            continue
    return sorted(out)


def geometrie(lignes: list[dict], couches: int | None,
              fenetre_px: int | None) -> dict:
    """La géométrie de lecture, relue si le fichier la porte, déclarée sinon.

    ⚠⚠ **Un désaccord entre les lignes est un refus, pas une moyenne.** Deux balayages
    concaténés à des profondeurs différentes produiraient une distribution qui n'appartient
    à aucun instrument — exactement la faute que ce fichier existe pour rendre impossible.
    """
    lues = {"layers": {r["layers"] for r in lignes if r.get("layers")},
            "window_px": {r["window_px"] for r in lignes if r.get("window_px")}}
    out: dict = {"declaree": False}
    for cle, fourni in (("layers", couches), ("window_px", fenetre_px)):
        vues = {v for v in lues[cle] if v not in ("", "0")}
        if len(vues) > 1:
            raise ValueError(f"{cle} n'est pas unique dans ce fichier : {sorted(vues)} — "
                             f"deux instruments concaténés ne calibrent rien")
        if vues:
            out[cle] = int(next(iter(vues)))
        elif fourni is not None:
            out[cle] = int(fourni)
            out["declaree"] = True
        else:
            raise ValueError(f"{cle} absent du fichier : le déclarer avec --{cle}, "
                             f"sinon la distribution n'appartient à aucun instrument")
    return out


def par_geometrie(lignes: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Les lignes groupées par géométrie de lecture.

    ⚠⚠ **Un corpus publié n'est PAS homogène, mesuré et non supposé.** Sur les 81 segments
    de `Scroll1`, quatre-vingts sont lus sur 109 couches et **un** sur 6. Une distribution
    unique aurait mélangé une lecture sur six couches à quatre-vingts lectures sur cent neuf
    — et le relief dépend de la profondeur (exposant +1,01), donc ce mélange n'aurait décrit
    aucun instrument. C'est le refus de `geometrie` qui l'a trouvé, au premier usage réel.

    ⭐ Grouper vaut mieux que refuser OU que moyenner : chaque groupe est une calibration
    valide, et le groupe d'un seul segment se voit tout de suite comme tel.
    """
    out: dict[tuple[str, str], list[dict]] = {}
    for r in lignes:
        cle = (r.get("layers") or "?", r.get("window_px") or "?")
        out.setdefault(cle, []).append(r)
    return out


def distribution(valeurs: list[float]) -> dict | None:
    if not valeurs:
        return None
    n = len(valeurs)
    return {"n": n, "min": valeurs[0], "max": valeurs[-1],
            "mediane": st.median(valeurs),
            "q1": valeurs[n // 4], "q3": valeurs[(3 * n) // 4]}


def resumer(lignes: list[dict], geo: dict, plancher: float = 0.02) -> dict:
    rel = nombres(lignes, "relief")
    bord = nombres(lignes, "edge_pinned")
    out = {"segments": len(lignes), "geometrie": geo, "plancher": plancher,
           "relief": distribution(rel), "edge_pinned": distribution(bord)}
    if rel:
        # ⚠ Le rapport au plancher est ce que le README dit de lire, donc c est lui qu on
        # publie -- pas la valeur brute, qui n a de sens que dans cette geometrie.
        out["relief_sur_plancher"] = distribution([x / plancher for x in rel])
        out["sous_le_plancher"] = sum(1 for x in rel if x < plancher)
    if bord:
        # ⚠⚠ Le compte a 90 % est rapporte parce que c est le seuil auquel `edge_pinned` a
        # ete declare fautif ailleurs. S il ne l atteint JAMAIS sur ce corpus, les deux
        # signaux ne s y departagent pas -- et le dire vaut mieux que de reciter l autre
        # mesure.
        out["au_bord_90"] = sum(1 for x in bord if x >= 0.90)
    return out


def situer(candidat: dict, corpus: list[float], geo_candidat: dict,
           geo_corpus: dict) -> dict:
    """Où tombe un candidat dans la distribution d'un corpus.

    ⚠⚠ **REFUS si les deux géométries diffèrent**, et c'est tout l'intérêt. Le relief dépend
    de la profondeur lue (exposant +1,01) et de l'étendue dans le plan (exposant −0,83) :
    situer une lecture à 1024 px dans une distribution mesurée à 128 px placerait le
    candidat quatre fois trop bas, et le classement paraîtrait parfaitement sensé.

    ⭐ C'est exactement ce que le README public conseille à ses lecteurs — comparer un
    candidat à la distribution mesurée LÀ OÙ ON LE LIT — rendu exécutable plutôt que
    recommandé.
    """
    for cle in ("layers", "window_px"):
        if geo_candidat.get(cle) != geo_corpus.get(cle):
            raise ValueError(
                f"{cle} diffère : candidat {geo_candidat.get(cle)}, corpus "
                f"{geo_corpus.get(cle)} — situer l'un dans l'autre ne veut rien dire")
    v = float(candidat["relief"])
    tri = sorted(corpus)
    dessous = sum(1 for x in tri if x < v)
    return {"relief": v, "corpus_n": len(tri),
            "rang": dessous, "percentile": (100.0 * dessous / len(tri)) if tri else None,
            "mediane_corpus": st.median(tri) if tri else None,
            "rapport_a_la_mediane": (v / st.median(tri)) if tri and st.median(tri) else None,
            "sous_le_minimum": bool(tri and v < tri[0]),
            "geometrie": dict(geo_corpus)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    lignes = [{"segment": "a", "relief": "0.80", "edge_pinned": "0.05",
               "layers": "65", "window_px": "128"},
              {"segment": "b", "relief": "0.52", "edge_pinned": "0.15",
               "layers": "65", "window_px": "128"},
              {"segment": "c", "relief": "0.93", "edge_pinned": "0.00",
               "layers": "65", "window_px": "128"}]
    geo = geometrie(lignes, None, None)
    v("la geometrie est RELUE quand le fichier la porte",
      geo["layers"] == 65 and geo["window_px"] == 128 and not geo["declaree"], str(geo))

    sans = [{k: val for k, val in r.items() if k not in ("layers", "window_px")}
            for r in lignes]
    geo2 = geometrie(sans, 65, 128)
    v("... et DECLAREE quand il ne la porte pas", geo2["declaree"] and geo2["layers"] == 65)
    # ⚠⚠ Sans declaration ni colonne, on REFUSE : une distribution qui n appartient a aucun
    # instrument ne calibre rien.
    try:
        geometrie(sans, None, None)
        v("un fichier sans geometrie ni declaration est refuse", False)
    except ValueError:
        v("un fichier sans geometrie ni declaration est refuse", True)
    # ⚠⚠ Deux instruments concatenes : refus, jamais une moyenne.
    melange = lignes + [{"segment": "d", "relief": "0.10", "edge_pinned": "0.5",
                         "layers": "65", "window_px": "1024"}]
    try:
        geometrie(melange, None, None)
        v("deux geometries dans un meme fichier sont refusees", False)
    except ValueError as e:
        v("deux geometries dans un meme fichier sont refusees",
          "calibrent rien" in str(e))

    # ⚠⚠ Le groupage : mesure du 2026-08-24 sur `Scroll1`, 80 segments a 109 couches et UN
    # a 6. Une distribution unique aurait melange les deux.
    g = par_geometrie(melange)
    v("les geometries sont groupees et non fondues", len(g) == 2, str(list(g)))
    v("... et le groupe d un seul segment se voit",
      sorted(len(v) for v in g.values()) == [1, 3], str([len(v) for v in g.values()]))

    # --- situer un candidat --------------------------------------------------------------
    # ⚠ Les valeurs REELLES : notre trace lue a 128 px sur 109 couches contre le corpus
    # publie du meme rouleau, meme geometrie.
    g128 = {"layers": 109, "window_px": 128}
    sit = situer({"relief": 0.1978}, [0.04, 0.744, 0.975], g128, g128)
    v("le candidat est situe dans le corpus", sit["rang"] == 1, str(sit["rang"]))
    v("... et son rapport a la mediane est chiffre",
      abs(sit["rapport_a_la_mediane"] - 0.2659) < 0.001,
      f"{sit['rapport_a_la_mediane']:.4f}")
    v("... et il n est pas sous le minimum du corpus", not sit["sous_le_minimum"])
    v("un candidat sous le minimum est signale",
      situer({"relief": 0.01}, [0.04, 0.744], g128, g128)["sous_le_minimum"])
    # ⚠⚠ LE REFUS : situer une lecture a 1024 px dans une distribution a 128 px la placerait
    # quatre fois trop bas, et le classement paraitrait sense.
    try:
        situer({"relief": 0.0462}, [0.04, 0.744],
               {"layers": 109, "window_px": 1024}, g128)
        v("deux geometries differentes sont refusees", False)
    except ValueError as e:
        v("deux geometries differentes sont refusees", "ne veut rien dire" in str(e))
    try:
        situer({"relief": 0.2}, [0.04], {"layers": 41, "window_px": 128}, g128)
        v("... y compris quand seule la profondeur differe", False)
    except ValueError:
        v("... y compris quand seule la profondeur differe", True)

    r = resumer(lignes, geo)
    v("la distribution du relief est resumee",
      r["relief"]["n"] == 3 and abs(r["relief"]["mediane"] - 0.80) < 1e-9, str(r["relief"]))
    v("le rapport au plancher est publie, pas seulement la valeur brute",
      abs(r["relief_sur_plancher"]["mediane"] - 40.0) < 1e-9,
      str(r["relief_sur_plancher"]))
    v("aucun segment sous le plancher ici", r["sous_le_plancher"] == 0)
    # ⚠ Le compte a 90 % doit etre rapporte MEME quand il vaut zero : c est ce zero qui dit
    # que les deux signaux ne se departagent pas sur ce corpus.
    v("le compte a 90 % est rapporte meme nul", r["au_bord_90"] == 0)
    v("un corpus vide ne rend pas de distribution", distribution([]) is None)
    # ⚠ Le filtre : sur un fichier qui PORTE la colonne, `--layers` doit retenir le groupe
    # et non declarer une valeur qui contredirait les lignes.
    # ⚠ Le filtre : sur un fichier qui PORTE la colonne, retenir un groupe doit en ecarter
    # les autres, et le groupe retenu doit etre d une seule geometrie -- sinon `geometrie`
    # refuserait juste apres, ce qui est le comportement voulu mais pas le filtre teste.
    retenu = [r for r in melange if r.get("window_px") == "128"]
    v("le filtre retient le bon groupe", len(retenu) == 3 and len(melange) == 4,
      f"{len(retenu)} sur {len(melange)}")
    v("... et le groupe retenu est d une seule geometrie",
      geometrie(retenu, None, None)["window_px"] == 128)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path, nargs="?", help="sortie de `tracecheck --all --csv`")
    ap.add_argument("--layers", type=int, help="profondeur lue, si le fichier ne la porte pas")
    ap.add_argument("--window-px", type=int, help="étendue dans le plan, idem")
    ap.add_argument("--plancher", type=float, default=0.02)
    ap.add_argument("--situer", type=Path,
                    help="un profil de candidat à placer dans la distribution du corpus")
    ap.add_argument("--par-geometrie", action="store_true",
                    help="une calibration par géométrie plutôt qu'un refus")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.csv or not a.csv.is_file():
        ap.error("donner un CSV de balayage, ou --verifier")

    lignes = lire(a.csv)
    # ⚠⚠ `--layers` FILTRE quand le fichier porte la colonne, et DECLARE quand il ne la
    # porte pas. Les deux sens sont utiles et ils ne se confondent pas : filtrer un fichier
    # qui ne dit rien est impossible, declarer sur un fichier qui dit deux choses serait un
    # mensonge. Le compte ecarte est annonce, jamais silencieux.
    if a.layers is not None and any(r.get("layers") for r in lignes):
        avant = len(lignes)
        lignes = [r for r in lignes if r.get("layers") == str(a.layers)]
        if len(lignes) != avant:
            print(f"  ⚠ {avant - len(lignes)} segment(s) écarté(s) : lus à une autre "
                  f"profondeur", file=sys.stderr)
    if not lignes:
        print(f"aucune ligne dans {a.csv}", file=sys.stderr)
        return 2
    if a.situer:
        # ⚠ Le corpus doit etre d une seule geometrie pour qu on y situe quoi que ce soit :
        # `geometrie` refuse s il en porte deux, et c est le bon moment pour le decouvrir.
        try:
            geo_corpus = geometrie(lignes, a.layers, a.window_px)
        except ValueError as e:
            print(f"refus : {e}", file=sys.stderr)
            return 3
        d = json.loads(a.situer.read_text(encoding="utf-8"))
        d = d[0] if isinstance(d, list) and d else d
        # ⚠⚠ La geometrie du CANDIDAT est lue dans son propre profil, jamais supposee egale
        # a celle du corpus -- c est precisement ce qu on verifie.
        geo_cand = {"layers": len(d.get("layers") or []),
                    "window_px": int(d.get("size") or d.get("window_px") or 0)}
        if not geo_cand["window_px"] and a.window_px:
            geo_cand["window_px"] = int(a.window_px)
        cand = {"relief": float(d["amplitude_mediane"])}
        try:
            r = situer(cand, nombres(lignes, "relief"), geo_cand, geo_corpus)
        except ValueError as e:
            print(f"refus : {e}", file=sys.stderr)
            return 3
        print(f"\n  candidat lu à {geo_cand['window_px']} px × {geo_cand['layers']} "
              f"couches, comme le corpus")
        print(f"    relief {r['relief']:.4f}  ×{r['relief'] / a.plancher:.1f} le plancher")
        print(f"    rang {r['rang']} sur {r['corpus_n']} "
              f"({r['percentile']:.0f}ᵉ percentile)")
        print(f"    médiane du corpus {r['mediane_corpus']:.4f} — le candidat vaut "
              f"×{r['rapport_a_la_mediane']:.2f} de cette médiane")
        if r["sous_le_minimum"]:
            print("    ⚠⚠ SOUS le minimum du corpus")
        if a.json:
            a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
            print(f"\n  écrit : {a.json}")
        return 0

    if a.par_geometrie:
        groupes = par_geometrie(lignes)
        tout = {"corpus": len(lignes), "geometries": len(groupes), "groupes": []}
        print(f"\n  {len(lignes)} segments répartis en {len(groupes)} géométrie(s) de "
              f"lecture")
        for (couches, fenetre), sous in sorted(groupes.items(),
                                               key=lambda kv: -len(kv[1])):
            g = {"layers": int(couches), "window_px": int(fenetre), "declaree": False}
            rr = resumer(sous, g, a.plancher)
            tout["groupes"].append(rr)
            d = rr.get("relief")
            marque = "  ⚠ un seul segment" if len(sous) == 1 else ""
            print(f"    {fenetre} px × {couches} couches : {len(sous)} segment(s){marque}")
            if d:
                print(f"        relief min {d['min']:.3f}  médiane {d['mediane']:.3f}  "
                      f"max {d['max']:.3f}   sous le plancher : {rr['sous_le_plancher']}")
        print("\n  ⚠⚠ chaque groupe est une calibration ; les mélanger n'en serait pas une")
        if a.json:
            a.json.write_text(json.dumps(tout, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
            print(f"\n  écrit : {a.json}")
        return 0

    try:
        geo = geometrie(lignes, a.layers, a.window_px)
    except ValueError as e:
        print(f"refus : {e}", file=sys.stderr)
        return 3
    r = resumer(lignes, geo, a.plancher)

    src = "déclarée à la main" if geo["declaree"] else "relue dans le fichier"
    print(f"\n  {r['segments']} segments · fenêtre {geo['window_px']} px × "
          f"{geo['layers']} couches ({src})")
    for cle, nom in (("relief", "relief"), ("edge_pinned", "edge_pinned")):
        d = r.get(cle)
        if d:
            print(f"    {nom:12s} min {d['min']:.3f}  q1 {d['q1']:.3f}  "
                  f"médiane {d['mediane']:.3f}  q3 {d['q3']:.3f}  max {d['max']:.3f}")
    if r.get("relief_sur_plancher"):
        d = r["relief_sur_plancher"]
        print(f"    en multiples du plancher de {r['plancher']:g} : "
              f"×{d['min']:.1f} à ×{d['max']:.1f}, médiane ×{d['mediane']:.1f}")
        print(f"    segments sous le plancher : {r['sous_le_plancher']}")
    if r.get("au_bord_90") is not None:
        print(f"    segments à edge_pinned ≥ 90 % : {r['au_bord_90']}")
        if r["au_bord_90"] == 0:
            print("    ⚠ jamais atteint ici : sur ce corpus les deux signaux ne se "
                  "départagent pas")
    print("\n  ⚠⚠ cette distribution vaut pour CETTE géométrie et pour aucune autre")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

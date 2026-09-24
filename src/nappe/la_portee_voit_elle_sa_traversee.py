"""La portée de `239` voit-elle la traversée de `235` dont elle est tirée ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MESURE NE SOIT FAITE. Ce qui était vu avant d'écrire : le profil que `235`
publie — les cumuls aux coupes 163, 173 et 203 au-delà du demi-feuillet, ceux de 183 et 193 en deçà —, la portée que
`239` en tire, et les découpages que `239`, `240`, `241` et `243` publient.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. `244` pose la suite : enchaîner les boucles sans main. Une procédure doit alors
couper chaque boucle à un pas fixé d'avance, et ce pas est la résolution du certificat : une traversée du
demi-feuillet plus courte que lui passe entre deux coupes. `239` l'a fixé à la « plus longue traversée que `235`
publie », de la première à la dernière coupe où le cumul atteint le demi-feuillet : 40 rangées. Mais entre ces deux
coupes, le cumul de `235` repasse sous le demi-feuillet. La portée voit-elle la traversée dont elle est tirée ?

## Ce qui se mesure, sur le profil que `235` publie et rien d'autre

LES TRAVERSÉES D'UN SEUL TENANT : les suites de coupes consécutives où le cumul atteint le demi-feuillet. Chacune dure
au moins de sa première à sa dernière coupe, et au plus de la coupe qui la précède à celle qui la suit — les bouts de
l'aile en tenant lieu.

LE PLUS PETIT ÉCART QUI ÉVITE : parmi les suites de coupes de `235` qui vont d'un bout de l'aile à l'autre sans passer
par une coupe au-delà du demi-feuillet, le plus petit écart maximal entre deux coupes voisines. Une portée au moins
égale à cet écart permet de couper sans rien voir ; en deçà, toute suite de coupes de `235` qui la respecte voit une
traversée. LA PORTÉE QUI VOIT est l'écart qui évite, moins un.

⚠⚠ Tout est dit aux coupes de `235` : entre deux d'entre elles, le cumul n'est pas vu.

## Ce qui en suit, sans rien lire

Pour chaque découpage publié — le rectangle de `239`, les ailes de `240`, de `241` et de `243` —, son plus grand écart
entre deux coupes voisines, contre la portée qui voit : au plus, une traversée comme celles de `235` ne lui échappe pas ;
au-delà, elle peut lui échapper.

## Les issues, exclusives

- le profil de `235` n'a aucune traversée : il n'y a rien à voir ;
- une coupe au bout de l'aile est elle-même au-delà : aucune suite ne l'évite, et toute portée la voit ;
- la portée de `239` est plus petite que l'écart qui évite : oui, elle voit sa traversée ;
- elle ne l'est pas : non, une suite de coupes à sa portée évite toute traversée.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les boucles jugées à un écart trop grand restent dessous à la portée qui voit —
il faudrait lire leurs coupes de plus — ; ni une traversée ailleurs, plus brève que celles de `235`.

Usage :
    uv run python src/nappe/la_portee_voit_elle_sa_traversee.py --verifier
    uv run python src/nappe/la_portee_voit_elle_sa_traversee.py --json docs/mesures/la_portee_voit_elle_sa_traversee.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from letroite_reste_t_elle_sans_ecart import ce_que_235_a_publie  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
LES_DECOUPAGES_PUBLIES = {
    "239": MESURES / "le_rectangle_entre_ses_coupes.json",
    "240": MESURES / "les_ailes_tiennent_elles_sur_leur_profil.json",
    "241": MESURES / "au_dela_de_la_colonne_qui_derive.json",
    "243": MESURES / "une_aile_plus_etroite_tient_elle.json",
}

LA_QUESTION_DECLAREE = "la portée de `239` voit-elle la traversée de `235` dont elle est tirée ?"
LA_MESURE_DECLAREE = ("les traversées d'un seul tenant du profil de `235`, le plus petit écart maximal d'une suite de "
                      "ses coupes qui les évite toutes, et, contre lui, la portée de `239` et le plus grand écart de "
                      "chaque découpage publié")


def _lire(chemin: Path) -> dict:
    try:
        return json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent ou illisible : {e}"}


def les_decoupages_publies(chemins: dict | None = None) -> dict:
    """La portée de `239`, et chaque découpage publié : ses coupes, et son plus grand écart entre coupes voisines."""
    chemins = LES_DECOUPAGES_PUBLIES if chemins is None else chemins
    d239, d240, d241, d243 = (_lire(chemins[n]) for n in ("239", "240", "241", "243"))
    for nom, d in (("239", d239), ("240", d240), ("241", d241), ("243", d243)):
        if not d.get("decidable"):
            return {"decidable": False, "raison": f"`{nom}` : {d.get('raison') or 'indécidable'}"}
    if d239.get("la_portee") is None or not d239.get("les_coupes"):
        return {"decidable": False, "raison": "`239` ne publie pas sa portée ou ses coupes"}
    out = [{"la_tranche": "239", "la_boucle": "le rectangle", "les_coupes": [int(x) for x in d239["les_coupes"]]}]
    for c in sorted((d240.get("les_decoupages") or {})):
        out.append({"la_tranche": "240", "la_boucle": f"l'aile {c}",
                    "les_coupes": [int(x) for x in d240["les_decoupages"][c]["les_coupes"]]})
    for nom, d in (("241", d241), ("243", d243)):
        if (d.get("le_decoupage") or {}).get("les_coupes"):
            out.append({"la_tranche": nom, "la_boucle": "l'aile", "les_coupes": [int(x) for x in
                                                                                 d["le_decoupage"]["les_coupes"]]})
    for x in out:
        cs = x["les_coupes"]
        x["le_plus_grand_ecart"] = max(b - a for a, b in zip(cs[:-1], cs[1:]))
    return {"decidable": True, "la_portee_de_239": int(d239["la_portee"]), "les_decoupages": out}


# ─────────────────────────────── les traversées ───────────────────────────────

def au_dela(p: dict, demi: float) -> bool:
    return abs(float(p["le_cumul_en_voxels"])) >= float(demi)


def les_traversees(profil: list[dict], demi: float, debut: int) -> list[dict]:
    """Les suites de coupes consécutives au-delà du demi-feuillet ; chacune dure au moins de sa première à sa dernière
    coupe, et au plus de la coupe qui la précède — ou du début de l'aile — à celle qui la suit — ou la dernière."""
    out, cur = [], None
    for j, p in enumerate(profil):
        if au_dela(p, demi):
            if cur is None:
                cur = {"de": int(p["la_coupe"]), "avant": int(profil[j - 1]["la_coupe"]) if j else int(debut)}
            cur["a"] = int(p["la_coupe"])
            cur["jusqua"] = int(profil[j + 1]["la_coupe"]) if j + 1 < len(profil) else int(p["la_coupe"])
        elif cur is not None:
            out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    for t in out:
        t["au_moins"] = t["a"] - t["de"]
        t["au_plus"] = t["jusqua"] - t["avant"]
    return out


def lecart_qui_evite(profil: list[dict], demi: float, debut: int) -> int | None:
    """Le plus petit écart maximal d'une suite de coupes, du début de l'aile à sa dernière coupe, qui ne passe par aucune
    coupe au-delà du demi-feuillet : toutes les coupes permises la composent. Aucun si la dernière coupe est au-delà."""
    if not profil or au_dela(profil[-1], demi):
        return None
    permises = [int(debut)] + [int(p["la_coupe"]) for p in profil if not au_dela(p, demi)]
    return max(b - a for a, b in zip(permises[:-1], permises[1:]))


# ─────────────────────────────── le verdict ───────────────────────────────

def _ce_qui_reste(aucune: bool, inevitable: bool, voit: bool, portee, qui_voit) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if aucune:
        return "LE PROFIL DE `235` N'A AUCUNE TRAVERSÉE : IL N'Y A RIEN À VOIR"
    if inevitable:
        return "LA DERNIÈRE COUPE DE `235` EST AU-DELÀ DU DEMI-FEUILLET : TOUTE PORTÉE VOIT SA TRAVERSÉE"
    if voit:
        return f"À LA PORTÉE DE {portee}, TOUTE SUITE DE COUPES DE `235` VOIT UNE TRAVERSÉE"
    return (f"À LA PORTÉE DE {portee}, UNE SUITE DE COUPES DE `235` ÉVITE TOUTE TRAVERSÉE : IL FAUT {qui_voit} RANGÉES "
            f"AU PLUS POUR LA VOIR")


def le_verdict(traversees: list[dict], ecart: int | None, portee: int) -> dict:
    """Le verdict, depuis les traversées, l'écart qui les évite et la portée de `239`."""
    aucune = not traversees
    inevitable = (not aucune) and ecart is None
    qui_voit = None if (aucune or inevitable) else int(ecart) - 1
    voit = inevitable or ((not aucune) and int(portee) < int(ecart))
    return {"la_portee_de_239": int(portee), "lecart_qui_evite": ecart, "la_portee_qui_voit": qui_voit,
            "la_portee_voit": bool(voit),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(aucune, inevitable, voit and not inevitable, portee, qui_voit)}


def ce_quen_voit_chaque_decoupage(decoupages: list[dict], qui_voit) -> list[dict]:
    """Chaque découpage, et s'il voit une traversée comme celles de `235` : son plus grand écart au plus la portée qui
    voit."""
    return [{**x, "voit": (qui_voit is not None and int(x["le_plus_grand_ecart"]) <= int(qui_voit))} for x in decoupages]


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(par235: dict | None = None, pub: dict | None = None, demi: float | None = None) -> dict:
    """Tout, depuis les publications, sans rien lire."""
    par235 = ce_que_235_a_publie() if par235 is None else par235
    pub = les_decoupages_publies() if pub is None else pub
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("235", par235), ("les découpages", pub)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"{nom} : {par.get('raison')}"}
    demi = float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi)
    profil = par235.get("profil") or []
    if not profil:
        return {**base, "decidable": False, "raison": "`235` ne publie pas de profil"}
    debut = int(par235["aile"]["les_coins"][0])
    if int(profil[0]["la_coupe"]) <= debut or any(int(b["la_coupe"]) <= int(a["la_coupe"])
                                                 for a, b in zip(profil[:-1], profil[1:])):
        return {**base, "decidable": False, "raison": "le profil de `235` n'avance pas coupe après coupe"}
    tr = les_traversees(profil, demi, debut)
    ecart = lecart_qui_evite(profil, demi, debut)
    v = le_verdict(tr, ecart, pub["la_portee_de_239"])
    return {**base, "decidable": True, "le_demi_feuillet": demi, "le_debut_de_laile": debut, "le_profil_de_235": profil,
            "les_traversees": tr, "le_verdict": v,
            "les_decoupages": ce_quen_voit_chaque_decoupage(pub["les_decoupages"], v["la_portee_qui_voit"])}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    for t in r["les_traversees"]:
        print(f"traversée : coupes {t['de']} à {t['a']} · entre {t['avant']} et {t['jusqua']} · dure de "
              f"{t['au_moins']} à {t['au_plus']} rangées")
    for x in r["les_decoupages"]:
        print(f"{x['la_tranche']} {x['la_boucle']} : plus grand écart {x['le_plus_grand_ecart']} · voit {x['voit']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import itertools
    import tempfile
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom} {detail}")

    def _ok(f):
        try:
            return bool(f())
        except Exception:  # noqa: BLE001
            return False

    def _p(cs, cum):  # noqa: E306
        return [{"la_coupe": c, "le_cumul_en_voxels": x} for c, x in zip(cs, cum)]

    # les traversées, sur des profils fabriqués
    p1 = _p([10, 20, 30, 40, 50, 60, 70], [1, 37, 40, 30, -38, 5, 2])
    t1 = les_traversees(p1, 36.0, 0)
    v("★★★★ les traversées sont les suites de coupes consécutives au-delà du demi-feuillet, dans les deux signes",
      _ok(lambda: [(t["de"], t["a"]) for t in t1] == [(20, 30), (50, 50)]), str(t1))
    v("★★★★ chacune dure au moins de sa première à sa dernière coupe, au plus de la coupe d'avant à celle d'après",
      _ok(lambda: (t1[0]["avant"], t1[0]["jusqua"], t1[0]["au_moins"], t1[0]["au_plus"]) == (10, 40, 10, 30)
          and (t1[1]["avant"], t1[1]["jusqua"], t1[1]["au_moins"], t1[1]["au_plus"]) == (40, 60, 0, 20)), str(t1))
    t2 = les_traversees(_p([10, 20, 30], [40, 1, 38]), 36.0, 0)
    v("★★★ une traversée à la première coupe commence au début de l'aile ; à la dernière, elle finit sur elle",
      _ok(lambda: (t2[0]["avant"], t2[0]["au_plus"]) == (0, 20) and (t2[1]["jusqua"], t2[1]["au_plus"]) == (30, 10)),
      str(t2))
    v("★★★ exactement au demi-feuillet, c'est au-delà", _ok(lambda: les_traversees(_p([5], [-36.0]), 36.0, 0)[0]["de"] == 5))

    # l'écart qui évite
    v("★★★★ l'écart qui évite est le plus grand trou que laissent les coupes permises, bouts compris",
      _ok(lambda: lecart_qui_evite(p1, 36.0, 0) == 30 and lecart_qui_evite(_p([10, 20, 30, 40], [1, 37, 2, 3]), 36.0, 0)
          == 20 and lecart_qui_evite(_p([10, 20], [1, 2]), 36.0, 0) == 10
          and lecart_qui_evite(_p([30, 40], [1, 2]), 36.0, 0) == 30), str(lecart_qui_evite(p1, 36.0, 0)))
    v("★★★★ une dernière coupe au-delà ne s'évite pas", _ok(lambda: lecart_qui_evite(_p([10, 20], [1, 40]), 36.0, 0) is None))

    # le verdict
    va = le_verdict(t1, 30, 40)
    vb = le_verdict(t1, 30, 29)
    v("★★★★ une portée au moins égale à l'écart qui évite ne voit pas ; en deçà, elle voit ; la portée qui voit est "
      "l'écart moins un",
      _ok(lambda: not va["la_portee_voit"] and "ÉVITE" in va["ce_qui_reste_a_mesurer"] and va["la_portee_qui_voit"] == 29
          and "29 RANGÉES" in va["ce_qui_reste_a_mesurer"] and vb["la_portee_voit"]
          and "VOIT UNE TRAVERSÉE" in vb["ce_qui_reste_a_mesurer"] and not le_verdict(t1, 30, 30)["la_portee_voit"]))
    v0 = le_verdict([], 30, 40)
    vi = le_verdict(t2, None, 40)
    v("★★★ sans traversée, rien à voir ; une dernière coupe au-delà se voit à toute portée ; les quatre issues sont "
      "distinctes",
      _ok(lambda: not v0["la_portee_voit"] and "RIEN À VOIR" in v0["ce_qui_reste_a_mesurer"] and vi["la_portee_voit"]
          and "TOUTE PORTÉE" in vi["ce_qui_reste_a_mesurer"] and vi["la_portee_qui_voit"] is None
          and len({_ce_qui_reste(*t, 40, 29) for t in itertools.product((True, False), repeat=3)}) == 4))
    dc = ce_quen_voit_chaque_decoupage([{"le_plus_grand_ecart": 19}, {"le_plus_grand_ecart": 20}], 19)
    v("★★★★ un découpage voit une traversée si son plus grand écart est au plus la portée qui voit",
      _ok(lambda: [x["voit"] for x in dc] == [True, False]
          and not any(x["voit"] for x in ce_quen_voit_chaque_decoupage(dc, None))))

    # ce qui est publié
    q235 = ce_que_235_a_publie()
    pub = les_decoupages_publies()
    v("★★★★ ce que 235 publie se relit : un profil de coupe en coupe depuis la rangée 26, au-delà aux coupes 163, 173 "
      "et 203",
      _ok(lambda: q235["aile"]["les_coins"][0] == 26
          and [p["la_coupe"] for p in q235["profil"] if au_dela(p, 36.0)] == [163, 173, 203]))
    v("★★★★ les découpages publiés se relisent : la portée de 239 est 40, et chacun porte son plus grand écart",
      _ok(lambda: pub["la_portee_de_239"] == 40
          and [(x["la_tranche"], x["la_boucle"], x["le_plus_grand_ecart"]) for x in pub["les_decoupages"]]
          == [("239", "le rectangle", 37), ("240", "l'aile gauche", 10), ("240", "l'aile haut", 10),
              ("241", "l'aile", 29), ("243", "l'aile", 39)]), str(pub.get("les_decoupages") or pub.get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        ch = {k: Path(tmp) / f"{k}.json" for k in LES_DECOUPAGES_PUBLIES}
        for k, p_ in LES_DECOUPAGES_PUBLIES.items():
            ch[k].write_text(p_.read_text())
        ch["239"].write_text(json.dumps({**json.loads(LES_DECOUPAGES_PUBLIES["239"].read_text()), "la_portee": None}))
        v("★★★ sans la portée de 239, les découpages sont refusés",
          _ok(lambda: not les_decoupages_publies(ch)["decidable"]))

    # la mesure
    m = mesurer()
    v("★★★★ la mesure passe sur ce qui est publié, et son verdict est celui de ses parties",
      _ok(lambda: m["decidable"] and m["les_traversees"] == les_traversees(q235["profil"], 36.0, 26)
          and m["le_verdict"] == le_verdict(m["les_traversees"], lecart_qui_evite(q235["profil"], 36.0, 26), 40)
          and m["les_decoupages"] == ce_quen_voit_chaque_decoupage(pub["les_decoupages"],
                                                                    m["le_verdict"]["la_portee_qui_voit"])),
      str(m.get("raison")))
    v("★★★★ un profil qui n'avance pas est refusé ; sans profil aussi",
      "n'avance pas" in str(mesurer({**q235, "profil": list(reversed(q235["profil"]))}, pub).get("raison"))
      and "pas de profil" in str(mesurer({**q235, "profil": []}, pub).get("raison")))
    v("★★★ 235 ou les découpages refusés : la mesure est refusée, par leur raison",
      "235" in str(mesurer({"decidable": False, "raison": "x"}, pub).get("raison"))
      and "découpages" in str(mesurer(q235, {"decidable": False, "raison": "x"}).get("raison")))
    v("★★★★ la mesure est déterministe", _ok(lambda: json.dumps(mesurer(), sort_keys=True) == json.dumps(m, sort_keys=True)))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
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
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

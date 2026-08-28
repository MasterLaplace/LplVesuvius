#!/usr/bin/env python3
"""Les 45 échantillons du dépôt public, leur ÉNERGIE, et ce qu'on en a publié.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est une correction de ma propre méthode.
[`59`](../../docs/59_la_campagne_plutot_que_le_rouleau.md) avait déjà payé un angle mort :
`campagnes_de_scan.py` n'interrogeait **qu'un des deux layouts** du dépôt. Et j'ai refait la
même faute le 2026-08-29 dans `ou_la_verite_existe.py` — une liste de **cinq** rouleaux écrite
à la main, interrogée par force brute, appelée « inventaire ».

  ⭐⭐⭐ Le dépôt publie **`metadata.min.json`** : 45 échantillons, 67 scans, chacun avec son
     `energy_keV` et son `pixel_size_um`, et la liste de ce qui existe par segment. **Une
     requête.** Le catalogue n'était pas à construire, il était à lire.

⭐ Ce que ça rend possible, et c'est l'idée de l'auteur : comparer plusieurs rouleaux à
énergies **différentes et identiques** pour chercher une tendance, au lieu de raisonner sur
les deux seuls objets qu'on avait sous la main.

⚠⚠ ET LE PIÈGE QUE `59` A DÉJÀ PAYÉ, qui s'applique mot pour mot ici : **une carte d'encre
publiée suit l'ATTENTION portée à un rouleau, pas sa lisibilité.** Restreint aux rouleaux
qu'on avait vraiment tentés, le p de `59` est passé de 0,0081 à **0,50**. Le même contrôle est
donc obligatoire ici : la comparaison ne vaut qu'entre échantillons **segmentés**, parce qu'un
échantillon sans segment n'a jamais été essayé.

⚠ Ce que ce fichier N'ÉTABLIT PAS : que l'énergie cause la lisibilité. Une carte publiée n'est
pas une lecture réussie — c'est une sortie de modèle que quelqu'un a jugée digne d'être mise en
ligne. Le lien entre les deux n'est pas mesuré, et [`65`](../../docs/65_ce_que_sigma_ne_dit_pas.md)
vient justement de montrer que le substitut habituel (σ) ne prédit pas la qualité mesurée.

Usage :
    uv run python src/encre/corpus_par_energie.py --verifier
    uv run python src/encre/corpus_par_energie.py --json docs/mesures/corpus_par_energie.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from encre.fenetres_par_region import fisher_unilateral  # noqa: E402

INDEX = ("https://vesuvius-challenge-open-data.s3.amazonaws.com/metadata.min.json")

SEUIL_KEV = 100.0
"""La frontière entre « basse » et « haute » énergie, en keV.

⚠⚠ Elle est CHOISIE, et il faut le dire : le corpus se répartit en deux paquets nets — 53 à
88 keV d'un côté, 110 à 137 de l'autre — et **rien n'est scanné entre 88 et 110**. Le seuil
tombe donc dans un trou, ce qui est la seule position qui ne dépende pas de sa valeur exacte :
le déplacer de 90 à 109 ne change aucun classement. Le contrôle l'asserte, et il échouera le
jour où un scan atterrira dans l'intervalle — auquel cas le seuil devra être rediscuté plutôt
que subi.
"""


def telecharger(chemin: Path, timeout: float = 120.0) -> bool:
    """L'index du dépôt, ou faux — jamais une exception."""
    try:
        p = subprocess.run(["curl", "-s", "--max-time", str(int(timeout)), INDEX,
                            "-o", str(chemin)], check=False)
    except OSError:
        return False
    return p.returncode == 0 and chemin.exists() and chemin.stat().st_size > 1000


def lire_index(chemin: Path) -> dict:
    """Le JSON, qu'il soit gzippé ou non.

    ⚠ Le dépôt le sert **gzippé sans en-tête de contenu** : `json.load` échoue sur un
    `UnicodeDecodeError` en position 1, ce qui ne ressemble pas du tout à « c'est compressé ».
    Essayer les deux évite de rejeter un index parfaitement valide.
    """
    brut = chemin.read_bytes()
    if brut[:2] == b"\x1f\x8b":
        brut = gzip.decompress(brut)
    return json.loads(brut)


def resumer(index: dict) -> list[dict]:
    """Un échantillon par ligne : ses énergies, ses résolutions, ses segments, ses cartes."""
    out = []
    for nom, e in (index.get("samples") or {}).items():
        scans = e.get("scans") or {}
        energies = sorted({s.get("properties", {}).get("energy_keV")
                           for s in scans.values()
                           if s.get("properties", {}).get("energy_keV")})
        resolutions = sorted({s.get("properties", {}).get("pixel_size_um")
                              for s in scans.values()
                              if s.get("properties", {}).get("pixel_size_um")})
        segments = e.get("segments") or {}
        cartes = sum(1 for s in segments.values()
                     if any(a.get("type") == "ink-detection" for a in (s.get("data") or [])))
        out.append({
            "echantillon": nom,
            "genre": (e.get("sample") or {}).get("properties", {}).get("type"),
            "energies_keV": energies,
            "resolutions_um": resolutions,
            "segments": len(segments),
            "cartes_encre": cartes,
            # ⚠ « a une basse énergie DISPONIBLE », pas « a été rendu à basse énergie » : le
            # dépôt ne dit pas à quelle énergie une carte publiée a été produite. Confondre
            # les deux ferait croire à un lien qu'on n'a pas mesuré.
            "basse_disponible": any(v < SEUIL_KEV for v in energies),
            "haute_seulement": bool(energies) and all(v >= SEUIL_KEV for v in energies),
        })
    return sorted(out, key=lambda x: (-x["cartes_encre"], x["echantillon"]))


def table_des_tentes(lignes: list[dict], genre: str | None = None) -> dict:
    """Le 2×2 restreint aux échantillons SEGMENTÉS — donc réellement tentés.

    ⚠⚠⚠ LA RESTRICTION EST TOUT LE TEST. `59` a mesuré que sans elle, le corpus rend
    p = 0,0081, et qu'avec elle il rend **0,50** : les échantillons jamais tracés faisaient
    tout le résultat, parce qu'une carte publiée suit l'attention. Un échantillon sans segment
    n'a pas « échoué à rendre de l'encre », il n'a **jamais été essayé**.
    """
    tentes = [l for l in lignes if l["segments"] > 0
              and (genre is None or l["genre"] == genre)]
    a = sum(1 for l in tentes if l["basse_disponible"] and l["cartes_encre"] > 0)
    b = sum(1 for l in tentes if l["basse_disponible"] and l["cartes_encre"] == 0)
    c = sum(1 for l in tentes if l["haute_seulement"] and l["cartes_encre"] > 0)
    d = sum(1 for l in tentes if l["haute_seulement"] and l["cartes_encre"] == 0)
    p = fisher_unilateral(a, b, c, d) if (a + b) and (c + d) else None
    return {"genre": genre or "tous", "tentes": len(tentes),
            "basse_avec_encre": a, "basse_sans_encre": b,
            "haute_avec_encre": c, "haute_sans_encre": d,
            "table": [a, b, c, d], "p": p}


def trou_du_seuil(lignes: list[dict], bas: float = 88.0, haut: float = 110.0) -> list[float]:
    """Les énergies qui tombent DANS l'intervalle où le seuil est posé.

    ⚠ Si cette liste cesse d'être vide, `SEUIL_KEV` n'est plus un choix indifférent et le
    classement d'au moins un échantillon dépend de sa valeur exacte. C'est le genre de
    dépendance qu'un seuil doit déclarer plutôt que porter en silence.
    """
    return sorted({v for l in lignes for v in l["energies_keV"] if bas < v < haut})


def rapporter(lignes: list[dict]) -> None:
    """La sortie lisible, et le contrôle de `59` appliqué avant toute conclusion."""
    print(f"{'echantillon':17} {'genre':9} {'keV':>26} {'segs':>5} {'cartes':>7}")
    for l in lignes:
        if l["segments"] == 0 and l["cartes_encre"] == 0:
            continue
        e = ",".join(f"{v:g}" for v in l["energies_keV"]) or "—"
        print(f"{l['echantillon']:17} {str(l['genre']):9} {e:>26} "
              f"{l['segments']:5d} {l['cartes_encre']:7d}")

    trou = trou_du_seuil(lignes)
    print()
    print(f"  seuil basse/haute energie : {SEUIL_KEV:g} keV, "
          + (f"⚠ {len(trou)} scan(s) dans le trou {trou}" if trou
             else "aucun scan entre 88 et 110 keV — le seuil ne decide de rien"))

    for genre in (None, "scroll", "fragment"):
        t = table_des_tentes(lignes, genre)
        if not t["tentes"]:
            continue
        print()
        print(f"  == {t['genre']} SEGMENTES ({t['tentes']}) ==")
        print(f"     basse energie disponible : {t['basse_avec_encre']} avec carte, "
              f"{t['basse_sans_encre']} sans")
        print(f"     haute energie seulement  : {t['haute_avec_encre']} avec carte, "
              f"{t['haute_sans_encre']} sans")
        print(f"     Fisher unilateral {t['table']} : p = "
              + (f"{t['p']:.4f}" if t["p"] is not None else "—"))


def verifier() -> int:
    """L'instrument peut-il rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile

    faux = {"samples": {
        "A": {"sample": {"properties": {"type": "scroll"}},
              "scans": {"s1": {"properties": {"energy_keV": 54.0, "pixel_size_um": 7.91}}},
              "segments": {"g1": {"data": [{"type": "ink-detection"}]},
                           "g2": {"data": [{"type": "tifxyz"}]}}},
        "B": {"sample": {"properties": {"type": "scroll"}},
              "scans": {"s1": {"properties": {"energy_keV": 116.0, "pixel_size_um": 8.64}}},
              "segments": {"g1": {"data": [{"type": "tifxyz"}]}}},
        "C": {"sample": {"properties": {"type": "scroll"}},
              "scans": {"s1": {"properties": {"energy_keV": 113.0, "pixel_size_um": 9.36}}},
              "segments": {}},
    }}
    lignes = resumer(faux)
    par = {l["echantillon"]: l for l in lignes}
    v("les energies sont relevees", par["A"]["energies_keV"] == [54.0], str(par["A"]))
    v("les cartes d'encre sont comptees, pas les segments",
      par["A"]["cartes_encre"] == 1 and par["A"]["segments"] == 2, str(par["A"]))
    v("... et un segment sans carte ne compte pas", par["B"]["cartes_encre"] == 0)
    v("basse energie disponible est vrai sous le seuil", par["A"]["basse_disponible"])
    v("... et haute seulement est vrai au-dessus", par["B"]["haute_seulement"])
    v("... et les deux s'excluent ici",
      not (par["A"]["haute_seulement"] or par["B"]["basse_disponible"]))

    # ⚠⚠⚠ LA SONDE QUI PORTE LE FICHIER : `C` n'a AUCUN segment, donc il n'a jamais ete
    # tente. L'inclure est exactement la faute que `59` a payee -- les jamais-traces
    # faisaient tout le resultat.
    t = table_des_tentes(lignes)
    v("un echantillon sans segment est exclu du test", t["tentes"] == 2, str(t))
    v("... et la table est dans l'ordre declare", t["table"] == [1, 0, 0, 1], str(t["table"]))
    faux2 = json.loads(json.dumps(faux))
    faux2["samples"]["C"]["segments"] = {"g1": {"data": [{"type": "tifxyz"}]}}
    v("... alors qu'un segment le fait entrer",
      table_des_tentes(resumer(faux2))["tentes"] == 3)

    # -- le seuil : il doit tomber dans un trou, et le dire s'il n'y en a plus.
    v("aucun scan de la fixture ne tombe dans le trou", trou_du_seuil(lignes) == [])
    faux3 = json.loads(json.dumps(faux))
    faux3["samples"]["A"]["scans"]["s2"] = {"properties": {"energy_keV": 95.0}}
    v("... mais un scan a 95 keV y est signale", trou_du_seuil(resumer(faux3)) == [95.0],
      str(trou_du_seuil(resumer(faux3))))

    # -- le genre filtre bien.
    v("le filtre par genre restreint", table_des_tentes(lignes, "fragment")["tentes"] == 0)
    v("... et garde les rouleaux", table_des_tentes(lignes, "scroll")["tentes"] == 2)

    # -- lire_index : gzippe ou non, les deux.
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "clair.json").write_bytes(json.dumps(faux).encode())
        (r / "gz.json").write_bytes(gzip.compress(json.dumps(faux).encode()))
        v("un index en clair se lit", lire_index(r / "clair.json") == faux)
        # ⚠ Le depot le sert GZIPPE sans en-tete : `json.load` echoue sur un
        # UnicodeDecodeError en position 1, ce qui ne ressemble pas a « c'est compresse ».
        v("... et un index gzippe aussi", lire_index(r / "gz.json") == faux)

    v("le seuil est ecrit, pas devine", SEUIL_KEV == 100.0)

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--index", type=Path, default=RACINE / "data" / "metadata.min.json")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.index.is_file() and not telecharger(a.index):
        print(f"index indisponible : {INDEX}", file=sys.stderr)
        return 2
    lignes = resumer(lire_index(a.index))
    rapporter(lignes)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"index": INDEX, "seuil_keV": SEUIL_KEV, "echantillons": lignes,
             "trou_du_seuil": trou_du_seuil(lignes),
             "tests": [table_des_tentes(lignes, g) for g in (None, "scroll", "fragment")]},
            indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

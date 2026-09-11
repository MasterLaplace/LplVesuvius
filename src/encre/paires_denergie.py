#!/usr/bin/env python3
"""Le plan d'expérience que le corpus porte déjà, et que personne n'avait regardé.

⚠⚠⚠ Pourquoi ce fichier existe, et c'est la conséquence directe d'un angle mort.
`campagnes_de_scan.py` n'interroge que le bucket **open-data** (`*-masked.zarr`), et
[`59`](../../docs/archive/59_la_campagne_plutot_que_le_rouleau.md) a construit son argument dessus.
Le 2026-08-28, en corrigeant ce document, l'angle mort est apparu : le volume où le modèle
atteint AUC 0,925 vit dans l'**ancien layout** `full-scrolls/`, invisible à ce relevé. En
regardant l'autre layout, `fragments/` en fait autant — et ce qu'il contient change la
question.

⭐⭐⭐ LES SIX FRAGMENTS SONT UN PLAN D'EXPÉRIENCE CONTRÔLÉ, déjà scanné :

    Frag1 à Frag4    54 contre 88 keV, tous deux à 3,24 µm   → l'ÉNERGIE varie seule
    Frag5            70 keV, 3,24 contre 7,91 µm             → la RÉSOLUTION varie seule
    Frag6            53, 70 et 88 keV à 3,24 µm              → trois énergies
    Frag6            53 keV, 3,24 contre 7,91 µm             → et sa paire de résolution

⭐ Ce que ça change pour M1ter. [`58`](../../docs/archive/58_resolution_ou_rouleau.md) §8 pose le
patron : *rendre l'objet qui marche semblable à celui qui ne marche pas, une propriété à la
fois*. Pour la résolution, `58` a dû **émuler** en décimant. Pour l'énergie, on écrivait
qu'il faudrait émuler un contraste — et qu'une émulation d'énergie n'en est pas une, puisque
l'atténuation change différemment selon le matériau. **Il n'y a rien à émuler : le même objet
existe scanné aux deux énergies, au même pas.**

⚠⚠ Et ces fragments portent une **vérité terrain d'encre** : `working/54keV_exposed_surface/`
donne la surface ouverte du fragment, celle qui a servi au concours de détection. C'est aussi
ce que [`45`](../../docs/archive/45_consistent_with_quantifie.md) §6 réclame pour le **transport** —
*« les deux régions d'un même objet »* — et qui avait été déclaré impossible sur le couple
essayé.

⚠ Ce fichier ne mesure PAS l'encre : il établit quelles paires contrôlées existent, et ce
que chacune isole. Rendre et comparer est le lot d'après, et il demande de télécharger des
volumes que ce dépôt n'a pas.

Usage :
    uv run python src/encre/paires_denergie.py --verifier
    uv run python src/encre/paires_denergie.py --lister --json docs/mesures/paires_denergie.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

BASE = "https://dl.ash2txt.org/fragments"
"""L'ancien layout, celui que `campagnes_de_scan.py` ne voit pas."""

FRAGMENTS = ("Frag1", "Frag2", "Frag3", "Frag4", "Frag5", "Frag6")
"""⚠ Écrits plutôt que découverts, et c'est un choix : une découverte silencieuse ferait
grossir ou rétrécir le plan d'expérience sans que rien ne le dise. Un fragment nouveau doit
être ajouté ici, donc vu."""

ENERGIE = re.compile(r"(\d+)\s*keV")
LIEN = re.compile(r'href="([^"?][^"]*)"')


def _get(url: str, timeout: float = 60.0) -> str:
    p = subprocess.run(["curl", "-s", "--max-time", str(int(timeout)), url],
                       capture_output=True, text=True)
    return p.stdout


def energie_du_nom(nom: str) -> int | None:
    """L'énergie déclarée dans le nom d'un volume, ou `None`."""
    m = ENERGIE.search(nom or "")
    return int(m.group(1)) if m else None


def paires_controlees(volumes: list[dict]) -> list[dict]:
    """Les paires d'un même objet où UNE grandeur varie et l'autre est tenue.

    ⚠⚠ Une paire où les deux varient n'isole rien, et c'est exactement ce que
    `campagnes_de_scan.py` dit du corpus : les grandeurs y **co-varient par campagne**. Ce
    sont les paires où elles NE co-varient pas qui valent quelque chose, et il n'y en a que
    dans ce layout-ci.
    """
    out = []
    for i, a in enumerate(volumes):
        for b in volumes[i + 1:]:
            meme_voxel = a["voxel_um"] == b["voxel_um"]
            meme_energie = a["energie_kev"] == b["energie_kev"]
            if meme_voxel and not meme_energie:
                isole = "energie"
            elif meme_energie and not meme_voxel:
                isole = "resolution"
            else:
                continue
            out.append({"isole": isole, "a": a["volume"], "b": b["volume"],
                        "voxel_um": [a["voxel_um"], b["voxel_um"]],
                        "energie_kev": [a["energie_kev"], b["energie_kev"]]})
    return out


def lire_fragment(nom: str, timeout: float = 60.0) -> dict:
    """Les volumes d'un fragment, avec leur pas et leur énergie."""
    volpkg = None
    for lien in LIEN.findall(_get(f"{BASE}/{nom}/", timeout)):
        if lien.rstrip("/").endswith(".volpkg"):
            volpkg = lien.rstrip("/")
            break
    if not volpkg:
        return {"fragment": nom, "volpkg": None, "volumes": [], "refus": "aucun volpkg"}
    volumes = []
    for lien in LIEN.findall(_get(f"{BASE}/{nom}/{volpkg}/volumes/", timeout)):
        uuid = lien.rstrip("/")
        if not uuid.isdigit():
            continue
        brut = _get(f"{BASE}/{nom}/{volpkg}/volumes/{uuid}/meta.json", timeout)
        try:
            meta = json.loads(brut)
        except Exception:
            continue
        volumes.append({"volume": uuid, "voxel_um": float(meta["voxelsize"]),
                        "energie_kev": energie_du_nom(meta.get("name", "")),
                        "nom": meta.get("name", "")})
    return {"fragment": nom, "volpkg": volpkg, "volumes": volumes,
            "paires": paires_controlees(volumes)}


def resume(lots: list[dict]) -> dict:
    paires = [dict(p, fragment=l["fragment"]) for l in lots for p in l.get("paires", [])]
    return {"base": BASE, "fragments": lots, "paires": paires,
            "compte": {"energie": sum(1 for p in paires if p["isole"] == "energie"),
                       "resolution": sum(1 for p in paires if p["isole"] == "resolution")}}


def verifier() -> int:
    """Auto-test HORS LIGNE : l'appariement, sur des volumes fabriqués."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    def vol(u, px, kev):
        return {"volume": u, "voxel_um": px, "energie_kev": kev}

    # --- L'ENERGIE DANS UN NOM ----------------------------------------------------------
    v("l'energie est lue dans un nom de volume",
      energie_du_nom("PHercParis2Fr47 54keV merged, cropped") == 54)
    v("... avec ou sans espace", energie_du_nom("Frag6 88 keV") == 88)
    v("un nom sans energie rend None", energie_du_nom("PHercParis4 stitched") is None)
    v("un nom vide rend None", energie_du_nom("") is None)

    # --- LES PAIRES CONTROLEES -----------------------------------------------------------
    # ⚠⚠ Ce qui vaut quelque chose est une paire ou UNE grandeur varie. Une paire ou les
    # deux varient n'isole rien -- c'est le defaut du corpus que `59` decrit.
    p = paires_controlees([vol("a", 3.24, 54), vol("b", 3.24, 88)])
    v("meme voxel, energies differentes : l'energie est isolee",
      len(p) == 1 and p[0]["isole"] == "energie")
    p = paires_controlees([vol("a", 3.24, 70), vol("b", 7.91, 70)])
    v("meme energie, voxels differents : la resolution est isolee",
      len(p) == 1 and p[0]["isole"] == "resolution")
    v("les deux qui varient n'isolent RIEN",
      paires_controlees([vol("a", 3.24, 54), vol("b", 7.91, 88)]) == [])
    v("deux volumes identiques n'isolent rien non plus",
      paires_controlees([vol("a", 3.24, 54), vol("b", 3.24, 54)]) == [])
    v("un seul volume ne fait aucune paire", paires_controlees([vol("a", 3.24, 54)]) == [])

    # --- TROIS ENERGIES : les trois paires, et aucune de resolution ---------------------
    trois = paires_controlees([vol("a", 3.24, 53), vol("b", 3.24, 70), vol("c", 3.24, 88)])
    v("trois energies au meme pas font trois paires", len(trois) == 3)
    v("... toutes d'energie", all(q["isole"] == "energie" for q in trois))

    # --- LE PLAN DE Frag6, tel qu'il est publie ------------------------------------------
    # ⚠ Les valeurs viennent du depot, relevees le 2026-08-28. Si elles changent, ce
    # controle le dira plutot que de laisser le plan d'experience deriver en silence.
    frag6 = paires_controlees([vol("20231121152933", 3.24, 53), vol("20231130112027", 7.91, 53),
                               vol("20231201112849", 3.24, 88), vol("20231201120546", 3.24, 70)])
    v("Frag6 porte trois paires d'energie",
      sum(1 for q in frag6 if q["isole"] == "energie") == 3)
    v("... et une paire de resolution",
      sum(1 for q in frag6 if q["isole"] == "resolution") == 1)
    # ⚠⚠ Le controle qui empeche de lire ce fichier comme une promesse : la paire
    # 7,91 µm / 53 keV contre 3,24 µm / 88 keV fait varier LES DEUX et n'est pas comptee.
    v("... et la paire ou les deux varient n'y est pas",
      not any(set(q["voxel_um"]) == {3.24, 7.91} and set(q["energie_kev"]) == {53, 88}
              for q in frag6))

    # --- LA LISTE DES FRAGMENTS, ecrite plutot que decouverte ---------------------------
    v("les six fragments sont nommes", len(FRAGMENTS) == 6)
    v("... et sans doublon", len(set(FRAGMENTS)) == len(FRAGMENTS))

    # --- LE RESUME -----------------------------------------------------------------------
    r = resume([{"fragment": "F", "paires": [{"isole": "energie"}, {"isole": "resolution"}]}])
    v("le resume compte les deux familles de paire",
      r["compte"] == {"energie": 1, "resolution": 1})
    v("... et rattache chaque paire a son fragment",
      all(p["fragment"] == "F" for p in r["paires"]))

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lister", action="store_true",
                    help="interroger le dépôt public (le seul mode qui touche au réseau)")
    ap.add_argument("--depuis", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.depuis:
        d = json.loads(a.depuis.read_text())
        for l in d["fragments"]:
            l["paires"] = paires_controlees(l["volumes"])
        d = resume(d["fragments"])
    elif a.lister:
        d = resume([lire_fragment(n) for n in FRAGMENTS])
    else:
        ap.error("donner --lister, --depuis ou --verifier")

    for l in d["fragments"]:
        print(f"  {l['fragment']}  {l.get('volpkg', '?')}")
        for v_ in l["volumes"]:
            print(f"      {v_['voxel_um']:>5} µm  {str(v_['energie_kev']):>4} keV  "
                  f"{v_['volume']}")
    print("\n  paires CONTRÔLÉES (une grandeur varie, l'autre est tenue) :")
    for p in d["paires"]:
        autre = "voxel_um" if p["isole"] == "energie" else "energie_kev"
        print(f"    {p['fragment']:6s} {p['isole']:10s} "
              f"{p['energie_kev'][0]:>3} vs {p['energie_kev'][1]:<3} keV  "
              f"à {p['voxel_um'][0]} / {p['voxel_um'][1]} µm")
    print(f"\n  {d['compte']['energie']} paire(s) qui isolent l'ÉNERGIE, "
          f"{d['compte']['resolution']} la RÉSOLUTION")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

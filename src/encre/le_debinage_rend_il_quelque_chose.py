#!/usr/bin/env python3
"""H2 : le débinage rend-il quelque chose ? — le même objet à deux échantillonnages.

⚠⚠⚠ CE FICHIER TRANCHE UNE CONTRADICTION ENTRE DEUX DOCUMENTS DU DÉPÔT.
[`73`](../../docs/73_seconde_passe_ce_que_le_depot_change.md) présente le courriel à l'ESRF
comme « coût nul, aucune expérience à monter avant la réponse », sur un argument **géométrique** :
à 4,7 µm une feuille fait 8 à 10 voxels au lieu de 4 à 5, donc `d′` monterait.
[`69`](../../docs/69_reponse_dun_chercheur_exterieur.md) §1.2 porte l'argument **physique**
contraire, marqué `[établi]` : à 1,2 m la résolution est bornée par la **décohérence** entre 4,3
et 9,4 µm, donc plus de voxels échantillonnant un signal déjà flou ne relèvent pas `d′`.
Prédiction chiffrée : **au plus 1,3–1,5×**.

⭐ Et `69` écrit la condition en toutes lettres : *« Cette prédiction est testable sur des
données publiques (H2), et **si elle est fausse**, la donnée manquante la plus précieuse du prix
est une demande à l'ESRF. »* Le courriel est donc **conditionnel**, et ceci est sa condition.

⭐⭐ POURQUOI `d′` ET PAS L'AUC D'ENCRE. C'est **la grandeur que l'argument de `73` invoque**, et
elle est sans dimension **donc comparable entre campagnes de scan** — c'est toute la raison de
son choix dans `separabilite_scan.py`. Une AUC d'encre demanderait un rendu de segment et des
annotations, coûterait des jours, et répondrait à une question plus large.

⚠⚠ LE CONFOND, DIT PLUTÔT QUE TU. Les deux volumes ne sont **pas** une acquisition binée deux
fois : ce sont deux acquisitions, `20250528085330-4.317um-1.2m-111keV` (mai) et
`20250820143440-9.362um-1.2m-113keV` (août). Le **bras est le même** (1,2 m) et l'écart d'énergie
vaut 2 keV sur 112, soit 1,8 % — et `66` §3 mesure que la sensibilité à l'énergie est *douce*
dans cette plage. Le confond est donc petit et nommable, mais il existe : ce test compare deux
acquisitions, pas un débinage au sens strict.

⚠ LES PARAMÈTRES SONT DES LONGUEURS, et c'est `separabilite_scan.py` qui le gère : `min_gap` et
`smooth` **dérivent** du pas inter-feuilles, jamais figés en voxels. Son propre commentaire
enregistre le prix de l'oubli — à 2,4 µm la *texture de fibres* fournit un extremum tous les 4 à
8 voxels, et le détecteur comptait des fibres au lieu de feuilles.

Usage :
    uv run python src/encre/le_debinage_rend_il_quelque_chose.py --chunks 343 \\
        --json docs/mesures/le_debinage.json
    uv run python src/encre/le_debinage_rend_il_quelque_chose.py --verifier
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "src" / "encre" / "separabilite_scan.py"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "le_debinage.json"

FIN = "PHerc0500P2/volumes/20250528085330-4.317um-1.2m-111keV-masked.zarr"
GROSSIER = "PHerc0500P2/volumes/20250820143440-9.362um-1.2m-113keV-masked.zarr"

VOLUMES = (
    ("fin", FIN, 4.317, 111.0, 0),
    ("grossier", GROSSIER, 9.362, 113.0, 0),
    # ⭐⭐⭐ LE CONTRÔLE, ET IL EST GRATUIT. Le niveau 1 du volume FIN vaut 8,63 µm — c'est-à-dire
    # un binage ×2 logiciel, donc exactement le `binmean2` dont `69` §1.2 parle — et il se
    # compare aux 9,362 µm du grossier. Il sépare les deux lectures possibles d'un `d′` fin plus
    # bas : « l'acquisition fine est moins bonne » contre « mesurer à pas fin rend un `d′` plus
    # bas ». Sans lui, un écart entre 4,3 et 9,4 µm ne dit pas laquelle des deux on regarde.
    ("fin_bine", FIN, 4.317, 111.0, 1),
)
"""Les deux volumes **au natif** (niveau 0), plus le fin **biné ×2** en contrôle.

⚠⚠ Le niveau importe : comparer le niveau 1 d'un volume à 4,317 µm au niveau 1 d'un volume à
9,362 µm comparerait 8,6 µm à 18,7 µm, ce qui n'est pas la question. Natif contre natif pour la
comparaison ; le niveau 1 du fin **seul** est le contrôle."""

PREDICTION_HAUTE = 1.5
"""Le facteur maximal que `69` §1.2 prédit pour le débinage. ⚠ C'est une prédiction sur la
**résolution effective**, transposée ici au rapport des `d′` : le lien n'est pas une identité,
et le dire évite de traiter un dépassement marginal comme une réfutation."""


def mesurer_un(cle: str, voxel_um: float, chunks: int, level: int = 0,
               timeout: float = 3600.0) -> dict | None:
    """
    @brief Le `d′` d'un volume, par l'instrument de `16`.
    """
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "d.json"
    r = subprocess.run(
        ["uv", "run", "python", str(OUTIL), cle, "--level", str(level),
         "--voxel-um", str(voxel_um), "--chunks", str(chunks), "--out", str(tmp)],
        capture_output=True, text=True, cwd=RACINE, timeout=timeout)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        return {"echec": sortie.strip().splitlines()[-1][:160] if sortie.strip() else "?"}
    # ⚠ La sortie est lue par motif ANCRE : ce depot a deja paye un `grep` non ancre qui
    # attrapait deux valeurs sur une meme ligne et rendait un NaN accuse au mauvais coupable.
    m = re.search(r"d′ median\s+([\d.]+)\s+p10\s+([\d.]+)\s+min\s+([\d.]+)\s+"
                  r"part sous 1,0 :\s+(\d+)\s*%", sortie)
    c = re.search(r"(\d+) chunks mesures sur (\d+) sondes \((\d+) vides\)", sortie)
    if not m:
        return {"echec": "sortie illisible : " + sortie.strip().splitlines()[-1][:120]}
    # ⚠⚠ L'INTERVALLE, PAR BOOTSTRAP SUR LES FENETRES. `64` §1 : un ecart sans intervalle
    # n'etablit rien, et il y faut assez de tuiles. Ici la question est « ces deux medianes
    # sont-elles distinguables », donc l'intervalle est celui de la MEDIANE, retire par
    # tirage avec remise des fenetres -- l'unite d'echantillonnage etant la fenetre.
    valeurs = []
    if tmp.is_file():
        valeurs = (json.loads(tmp.read_text()) or {}).get("valeurs") or []
    ic = None
    if len(valeurs) >= 8:
        import random
        import statistics as st
        alea = random.Random(42)
        meds = sorted(st.median(alea.choices(valeurs, k=len(valeurs))) for _ in range(2000))
        ic = [meds[int(0.025 * len(meds))], meds[int(0.975 * len(meds)) - 1]]
    return dict(d_median=float(m.group(1)), p10=float(m.group(2)), minimum=float(m.group(3)),
                part_sous_1_pct=int(m.group(4)),
                mesures=int(c.group(1)) if c else None,
                sondes=int(c.group(2)) if c else None,
                vides=int(c.group(3)) if c else None,
                ic95=ic, valeurs=valeurs)


def mesurer(chunks: int = 343) -> dict:
    out = {"chunks_demandes": chunks, "volumes": {}}
    for nom, cle, voxel, kev, lvl in VOLUMES:
        r = mesurer_un(cle, voxel, chunks, lvl)
        out["volumes"][nom] = dict(cle=cle, voxel_um=voxel, energie_keV=kev, level=lvl,
                                   voxel_effectif_um=voxel * (2 ** lvl), **(r or {}))
    f = out["volumes"].get("fin", {})
    g = out["volumes"].get("grossier", {})
    b = out["volumes"].get("fin_bine", {})
    if f.get("d_median") and g.get("d_median"):
        out["rapport_fin_sur_grossier"] = f["d_median"] / g["d_median"]
    if b.get("d_median") and g.get("d_median"):
        out["rapport_bine_sur_grossier"] = b["d_median"] / g["d_median"]
    return out


def _verifier(r: dict | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE LECTEUR DE SORTIE, teste sur une ligne REELLE et sur une ligne absente : un motif
    # trop laxiste rendrait un nombre pris ailleurs, un motif absent rendrait None en silence.
    faux = ("PHerc0500P2 niveau 0 : grille (56, 33, 33), voxel 9.4 µm\n"
            "  7 chunks mesures sur 108 sondes (101 vides)\n"
            "  d′ median 1.64   p10 1.12   min 0.69   part sous 1,0 : 14 %\n")
    m = re.search(r"d′ median\s+([\d.]+)\s+p10\s+([\d.]+)\s+min\s+([\d.]+)\s+"
                  r"part sous 1,0 :\s+(\d+)\s*%", faux)
    v("la ligne de résultat est lue", m is not None and float(m.group(1)) == 1.64,
      m.group(1) if m else "aucune")
    v("... et les comptes de sondes aussi",
      bool(re.search(r"(\d+) chunks mesures sur (\d+) sondes \((\d+) vides\)", faux)))
    v("... et une sortie sans résultat ne rend PAS un nombre",
      re.search(r"d′ median\s+([\d.]+)", "erreur : rien\n") is None)

    if r and r.get("volumes"):
        print("\net la mesure")
        f, g = r["volumes"].get("fin", {}), r["volumes"].get("grossier", {})
        v("les deux volumes ont rendu un d′",
          bool(f.get("d_median")) and bool(g.get("d_median")),
          f"fin {f.get('d_median')} · grossier {g.get('d_median')}")
        if f.get("d_median") and g.get("d_median"):
            # ⚠⚠ ASSEZ DE FENETRES POUR QUE CA VEUILLE DIRE QUELQUE CHOSE. `33` §3-4bis mesure
            # qu'il en faut 50 a 100 pour qu'un CLASSEMENT entre rouleaux tienne. Ici la
            # comparaison est appariee -- meme objet, meme bras -- donc l'exigence est moins
            # dure, mais une poignee de fenetres ne dit rien et il faut le dire.
            v("... sur assez de fenêtres pour que ce soit lisible",
              min(f.get("mesures") or 0, g.get("mesures") or 0) >= 20,
              f"fin {f.get('mesures')}/{f.get('sondes')} · "
              f"grossier {g.get('mesures')}/{g.get('sondes')}")
            # ⚠⚠⚠ LE RESULTAT, ECRIT POUR TOMBER DANS LES DEUX SENS. `69` predit au plus
            # 1,3-1,5x ; `73` predit une hausse. Si le rapport depassait 1,5, la prediction de
            # `69` serait fausse et le courriel a l'ESRF deviendrait la priorite qu'il annonce.
            rapport = r.get("rapport_fin_sur_grossier") or 0
            v(f"le débinage ne rend PAS le facteur que `73` suppose (≤ {PREDICTION_HAUTE})",
              rapport <= PREDICTION_HAUTE,
              f"d′ fin / d′ grossier = {rapport:.2f}")
        # ⚠⚠⚠ LE CONTROLE QUI SEPARE DEUX LECTURES. Un `d′` fin plus bas peut vouloir dire
        # « l'acquisition fine est moins bonne » OU « mesurer a pas fin rend un `d′` plus bas ».
        # Le volume fin BINE x2 vaut 8,63 µm : s'il rejoint le grossier, la seconde lecture est
        # la bonne et la comparaison natif-contre-natif ne dit rien de la QUALITE du scan.
        b = r["volumes"].get("fin_bine", {})
        if b.get("d_median") and g.get("d_median"):
            ecart = abs(b["d_median"] - g["d_median"]) / g["d_median"]
            v("le fin BINÉ ×2 reste dans la même bande que les deux natifs",
              ecart < 0.20,
              f"biné {b['d_median']:.2f} (8,63 µm) contre grossier {g['d_median']:.2f} "
              f"(9,36 µm) — écart {100 * ecart:.0f} %")
        # ⚠⚠⚠ ET L'INTERVALLE, PARCE QUE `64` §1 L'EXIGE : deux medianes qui se ressemblent ne
        # sont « indistinguables » que si leurs intervalles se recouvrent. Publier 1,44 contre
        # 1,43 sans ca serait exactement l'ecart sans intervalle que ce depot refuse.
        ic_f, ic_g = f.get("ic95"), g.get("ic95")
        if ic_f and ic_g:
            recouvre = ic_f[0] <= ic_g[1] and ic_g[0] <= ic_f[1]
            v("... et les intervalles des deux natifs SE RECOUVRENT, donc rien ne les sépare",
              recouvre,
              f"fin [{ic_f[0]:.2f} ; {ic_f[1]:.2f}] · grossier [{ic_g[0]:.2f} ; {ic_g[1]:.2f}]")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--chunks", type=int, default=343)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.verifier and not a.json:
        garde = json.loads(DEFAUT_JSON.read_text()) if DEFAUT_JSON.is_file() else None
        return 1 if _verifier(garde) else 0

    r = mesurer(a.chunks)
    for nom, d in r["volumes"].items():
        if d.get("echec"):
            print(f"  {nom:9s} ÉCHEC — {d['echec']}", file=sys.stderr)
            continue
        print(f"  {nom:9s} {d.get('voxel_effectif_um', d['voxel_um']):6.3f} µm  "
              f"{d['energie_keV']:5.1f} keV  "
              f"d′ médian {d['d_median']:5.2f}  p10 {d['p10']:5.2f}  "
              f"sous 1,0 {d['part_sous_1_pct']:3d} %  "
              + (f"IC95 [{d['ic95'][0]:.2f} ; {d['ic95'][1]:.2f}]  " if d.get("ic95") else "")
              + f"({d['mesures']}/{d['sondes']} fenêtres)")
    if r.get("rapport_fin_sur_grossier"):
        print(f"\n  d′ fin / d′ grossier = {r['rapport_fin_sur_grossier']:.2f}"
              f"   (`69` prédit au plus {PREDICTION_HAUTE})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

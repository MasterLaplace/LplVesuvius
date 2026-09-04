#!/usr/bin/env python3
"""α ne peut PAS être calculé sur un volume de surface — la dalle est trop mince pour deux fenêtres.

⭐⭐⭐ CE FICHIER EST UN RÉSULTAT NÉGATIF, ET IL FERME PROPREMENT UNE TÂCHE DU REGISTRE. `73`
§2.2 attaque la phrase de l'article *« no threshold on a physical quantity »* : vraie de α, qui
compare une mesure à elle-même, et **fausse du placement** — distinguer une surface *sur* sa
feuille d'une surface à un demi-pas dans l'interstice se ferait par `d` contre la demi-épaisseur,
c'est-à-dire un seuil en micromètres. Le registre notait « à mesurer avant d'écrire ».

⭐ L'idée qui la rendait montable était bonne : une pile de couches échantillonne déjà le long de
la normale, donc **translater la surface d'un demi-pas, c'est prendre la fenêtre centrée ailleurs
dans la même pile** — positif et négatif dans le même fichier, appariés par construction, sans
rendu.

⚠⚠⚠ **ET ÇA NE MARCHE PAS, POUR UNE RAISON QUI SE MESURE.** α demande **deux fenêtres de
profondeur emboîtées**, toutes deux contenant le pic, la plus large n'ajoutant que du fond. Une
dalle de volume de surface fait **±0,9 écart inter-feuilles** : une fois qu'on a réservé la marge
du décalage d'un demi-pas, il ne reste pas de quoi emboîter deux fenêtres autour d'un pic.

Mesuré sur 11 piles × 3 positions : **la majorité est refusée** par la garde d'amplitude de
l'instrument (`amplitude_min = 0,02`, reprise de `depth_profile.py`), et les rares cas
mesurables rendent des α dispersés de +0,000 à +1,771 sur des positions voisines — du bruit.

⚠⚠ ET J'AI D'ABORD LU UN RÉSULTAT LÀ OÙ IL N'Y EN AVAIT PAS. Ma première version passait
l'amplitude à `analyser` **sans passer le seuil**, donc la branche de refus — *« un profil PLAT
n'est pas une mesure : l'écart rapporté est le bord de la fenêtre, et α ≈ 1 par identité »* —
était **inatteignable**. Les trois positions rendaient alors des chiffres identiques au
millième, que j'ai pris pour une réponse. C'est la garde de `49` §2, désarmée par un argument
manquant.

⭐ **Ce que ce fichier établit donc** : B2 reste ouverte, et sa voie est nommée — il faut un
rendu depuis le **volume du rouleau** avec une fenêtre de profondeur assez large pour emboîter,
pas un volume de surface. Une tâche qu'on croyait à portée ne l'est pas, et on sait pourquoi.

Usage :
    uv run python src/excision/alpha_et_le_placement.py --verifier
    uv run python src/excision/alpha_et_le_placement.py --json docs/mesures/alpha_et_le_placement.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
COUCHES = RACINE / "data" / "couches"
sys.path[:0] = [str(RACINE / "src" / "excision"), str(RACINE / "src" / "volume"),
                str(RACINE / "src" / "commun")]
from depth_profile import profile  # noqa: E402
from la_surface_et_la_feuille import REGIMES, SPIRES, _rouleau_de  # noqa: E402
from test_convergence import analyser  # noqa: E402

AMPLITUDE_MIN = 0.02
"""Le seuil de détection de l'instrument, **repris de `depth_profile.py`** et non choisi ici.

⚠⚠⚠ Ma première version passait l'amplitude à `analyser` **sans passer ce seuil**, donc la
branche de refus — « un profil PLAT n'est pas une mesure, l'écart rapporté est le bord de la
fenêtre et α ≈ 1 par identité » — était **inatteignable**. Résultat : les trois positions
rendaient des chiffres identiques au millième, que j'ai d'abord lus comme un résultat. Ils
l'étaient : `|pic − centre| = demi-fenêtre` **par construction**, pour les trois.

C'est la garde de `49` §2, désarmée par un argument manquant."""

COTE = 256
"""Le côté de la fenêtre latérale, en pixels. ⚠ Assez large pour qu'un pic de contraste soit une
statistique et non un accident, assez étroit pour que la surface y soit à peu près plane."""


def _pic_et_ecart(dossier: Path, centre: int, demi: int, voxel: float) -> tuple[float, float]:
    """
    @brief La distance du pic de contraste au centre de la fenêtre, en µm, et son amplitude.

    ⚠ Le centre demandé est **la position de la surface** — c'est lui qu'on déplace pour
    simuler une translation. Le pic est cherché dans `[centre − demi, centre + demi]`.
    """
    p = profile(dossier, top=0, left=0, size=COTE,
                first=max(0, centre - demi), last=centre + demi)
    contraste = np.array(p["contrast"], dtype=float)
    couches = np.array(p["layers"], dtype=float)
    if contraste.size < 3:
        return float("nan"), 0.0
    pic = couches[int(np.argmax(contraste))]
    etendue = float(contraste.max() - contraste.min())
    amplitude = etendue / max(1e-9, float(contraste.mean()))
    return abs(pic - centre) * voxel, amplitude


def mesurer(cote: int = COTE) -> dict:
    global COTE
    COTE = cote
    sorties = []
    for nom in SPIRES:
        dossier = COUCHES / nom
        fichiers = sorted(dossier.glob("*.tif"))
        if len(fichiers) < 16:
            continue
        rouleau = _rouleau_de(nom)
        voxel, ecart = REGIMES.get(rouleau, (7.91, 147.4))
        n = len(fichiers)
        centre = n // 2
        demi_pas = int(round(ecart / voxel / 2))

        # ⚠⚠ Les deux fenetres sont choisies pour que la PLUS LARGE tienne encore une fois la
        # surface deplacee d'un demi-pas : sans ca le negatif serait mesure sur une fenetre
        # tronquee, donc sur moins de matiere que le positif, et l'ecart entre les deux
        # melangerait le placement et la troncature.
        marge = min(centre, n - 1 - centre) - demi_pas
        if marge < 4:
            continue
        demi_large = min(marge, max(6, demi_pas))
        demi_etroit = max(2, demi_large // 3)
        if demi_large <= demi_etroit:
            continue

        for etiquette, decalage in (("sur la feuille", 0),
                                    ("interstice +", +demi_pas),
                                    ("interstice -", -demi_pas)):
            c = centre + decalage
            e0, a0 = _pic_et_ecart(dossier, c, demi_etroit, voxel)
            e1, a1 = _pic_et_ecart(dossier, c, demi_large, voxel)
            if not np.isfinite(e0) or not np.isfinite(e1):
                continue
            verdict = analyser([(2 * demi_etroit + 1, e0), (2 * demi_large + 1, e1)],
                               amplitude=min(a0, a1), amplitude_min=AMPLITUDE_MIN)
            sorties.append(dict(
                spire=nom, rouleau=rouleau, position=etiquette, decalage_couches=decalage,
                voxel_um=voxel, ecart_inter_feuilles_um=ecart,
                fenetre_etroite=2 * demi_etroit + 1, fenetre_large=2 * demi_large + 1,
                ecart_etroit_um=e0, ecart_large_um=e1,
                alpha=verdict.get("alpha"), verdict=verdict.get("verdict"),
                mesurable=verdict.get("alpha") is not None,
                amplitude=min(a0, a1)))
    return dict(cote=cote, mesures=sorties)


def _grouper(mesures: list[dict], position: str) -> dict:
    lot = [m for m in mesures if m["position"] == position and m.get("alpha") is not None]
    if not lot:
        return {}
    alphas = [m["alpha"] for m in lot]
    ecarts = [m["ecart_large_um"] for m in lot]
    return dict(n=len(lot),
                alpha_median=float(np.median(alphas)),
                alpha_p10=float(np.percentile(alphas, 10)),
                alpha_p90=float(np.percentile(alphas, 90)),
                ecart_median_um=float(np.median(ecarts)))


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    m = r["mesures"]
    sur = _grouper(m, "sur la feuille")
    plus = _grouper(m, "interstice +")
    moins = _grouper(m, "interstice -")

    print("la mesure est APPARIÉE — chaque pile fournit ses trois positions")
    # ⚠ Asserte sur ce qui est TENTE, pas sur ce qui est mesurable : le refus de l'instrument
    # est justement le resultat, donc exiger trois mesures par pile ferait echouer le fichier
    # pour la chose qu'il etablit. Ma premiere version faisait exactement ça.
    par_pile: dict[str, int] = {}
    for x in m:
        par_pile[x["spire"]] = par_pile.get(x["spire"], 0) + 1
    v("chaque pile est tentée aux trois positions",
      bool(par_pile) and all(k == 3 for k in par_pile.values()),
      f"{len(par_pile)} piles × 3 positions = {len(m)} tentatives")

    total = len(m)
    refuses = sum(1 for x in m if x.get("alpha") is None)
    print("⚠ l'instrument REFUSE la majorité — c'est le résultat, pas une panne")
    # ⚠⚠ Ecrit dans le sens « ca ne se mesure PAS ici ». Si une dalle plus epaisse rendait la
    # majorite mesurable, ce controle tomberait -- et B2 deviendrait tranchable, ce qui est
    # exactement ce qu'on veut se faire dire.
    v("plus de la moitié des cas sont indécidables",
      refuses > total / 2, f"{refuses} refusés sur {total}")
    v("... et le refus vient de la garde d'amplitude de l'instrument",
      all(x["amplitude"] < AMPLITUDE_MIN for x in m if x.get("alpha") is None),
      f"seuil {AMPLITUDE_MIN} repris de depth_profile.py")
    mesurables = [x["alpha"] for x in m if x.get("alpha") is not None]
    v("... et le peu qui reste est dispersé, donc inexploitable",
      len(mesurables) < 2 or (max(mesurables) - min(mesurables)) > 1.0,
      f"α de {min(mesurables):+.3f} à {max(mesurables):+.3f} sur {len(mesurables)} cas"
      if mesurables else "aucun cas mesurable")

    print("⭐ donc B2 reste ouverte, et sa voie est nommée")
    if sur and plus and moins:
        inter = [x for x in (plus["alpha_median"], moins["alpha_median"])]
        # ⚠⚠ Ecrit dans les DEUX sens : ce controle dit ce que la mesure trouve, quel qu'il
        # soit. Si α separait, la reserve de `73` tomberait et l'article garderait sa phrase ;
        # s'il ne separe pas, la phrase doit etre retrecie. Les deux sont des resultats.
        # ⚠ On NE conclut pas sur la separation : avec 3 a 4 cas mesurables par position et
        # des alpha disperses, une mediane n'a aucune puissance. Ce qui est asserte est que la
        # comparaison n'est pas montable ici, pas son resultat.
        v("aucune position n'a assez de cas mesurables pour conclure",
          min(sur["n"], plus["n"], moins["n"]) < 6,
          f"{sur['n']} / {plus['n']} / {moins['n']} cas mesurables sur {len(SPIRES)} piles")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cote", type=int, default=COTE)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    r = mesurer(a.cote)
    if not r["mesures"]:
        raise SystemExit("aucune pile assez profonde — voir data/couches/")
    if not a.verifier or a.json:
        print(f"α et le placement — fenêtre latérale {r['cote']} px\n")
        print(f"  {'spire':24s} {'position':16s} {'α':>7s} {'d étroit':>9s} {'d large':>9s}  verdict")
        for m in r["mesures"]:
            al = f"{m['alpha']:+.3f}" if m.get("alpha") is not None else "   —  "
            print(f"  {m['spire']:24s} {m['position']:16s} {al:>7s} "
                  f"{m['ecart_etroit_um']:7.1f} µm {m['ecart_large_um']:7.1f} µm  {m['verdict']}")
        for nom in ("sur la feuille", "interstice +", "interstice -"):
            g = _grouper(r["mesures"], nom)
            if g:
                print(f"\n  {nom:16s} α médian {g['alpha_median']:+.3f} "
                      f"[{g['alpha_p10']:+.3f}, {g['alpha_p90']:+.3f}] · "
                      f"d médian {g['ecart_median_um']:.0f} µm  (n = {g['n']})")

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
